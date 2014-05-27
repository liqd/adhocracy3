/// <reference path="../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../_all.d.ts"/>

import angular = require("angular");
import _ = require("underscore");

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");
import Css = require("Adhocracy/Css");
import AdhHttp = require("Adhocracy/Services/Http");
import AdhWS = require("Adhocracy/Services/WS");
import AdhCache = require("Adhocracy/Services/Cache");

import Resources = require("Adhocracy/Resources");

var templatePath : string = "/frontend_static/templates";  // FIXME: move this to config file.


export class ListingContainerAdapter {
    static ContainerType : Types.Content<Resources.HasIPoolSheet>;  // FIXME: (for elemRefs sig)
    public ContainerType : Types.Content<Resources.HasIPoolSheet>;  // FIXME: (for typeof sigs in controller)

    public elemRefs(c : typeof ListingContainerAdapter.ContainerType) : string[] {  // FIXME: argument type should be something like 'self.ContainerType'.
        return c.data["adhocracy.sheets.pool.IPool"].elements;
    }
}

export class ListingElementAdapter {
    static ElementType: Types.Content<any>;  // FIXME (see ListingContainerAdapter)
    public ElementType: Types.Content<any>;

    public name(e: typeof ListingElementAdapter.ElementType) : string {  // FIXME: s/ListingContainerAdapter./self./ does not work.  what does?
        return "[content type " + e.content_type + ", resource " + e.path + "]"
    }
    public path(e: typeof ListingElementAdapter.ElementType) : string {  // FIXME: s/ListingContainerAdapter./self./ does not work.  what does?
        return e.path;
    }
}

export interface ListingScope<Container> {
    container: Container;
    elements: { name: string;
                path: string;
              }[];
}

export class Listing<ContainerAdapter extends ListingContainerAdapter, ElementAdapter extends ListingElementAdapter> {

    static templateUrl: string = "/Widgets/Listing.html";

    constructor(private containerPath: string,
                public containerAdapter: ContainerAdapter,
                public elementAdapter: ElementAdapter)
    { }

    public factory = function() {
        // FIXME: "factory" might be misinterpreted as "ListingFactory".
        // possible solutions: (1) rename; (2) implement Listing class
        // such that the instance type is '() => IDirective', and no
        // factory method is needed.

        var _this = this;

        return function() {
          return {
            restrict: "E",
            templateUrl: templatePath + "/" + Listing.templateUrl,  // FIXME: "s/Listing./self./"?
            scope: { },
            controller: ["$scope",
                         "adhHttp",
                         "adhHttp",  // FIXME(?): do we really want to duplicate adhHttp for the type system?  (mf thinks we do!)
                         function($scope: ListingScope<typeof _this.containerAdapter.ContainerType>,
                                  adhHttpC: AdhHttp.IService<typeof _this.containerAdapter.ContainerType>,
                                  adhHttpE: AdhHttp.IService<typeof _this.elementAdapter.ElementType>
                                 ) : void
                         {
                             adhHttpC.get(_this.containerPath).then((pool: typeof _this.containerAdapter.ContainerType) => {
                                 $scope.container = pool;
                                 $scope.elements = [];

                                 var elemRefs : string[] = _this.containerAdapter.elemRefs($scope.container);

                                 for (var x in elemRefs) {
                                     $scope.elements[x] = {name: x, path: x};
                                     // FIXME: this is a workaround.
                                     // if we don't do this, the last
                                     // in a long array of elements
                                     // may be initialized first in
                                     // the next loop, and then all
                                     // previous elements are
                                     // 'undefined' when the template
                                     // is rendered for the first
                                     // time.  this will result in
                                     // duplicate errors during
                                     // template rendering.  this loop
                                     // avoids that by initializing
                                     // the elements in order.  the
                                     // correct solution would be to
                                     // postpone rendering until all
                                     // elements have been downloaded.
                                 }

                                 for (var x in elemRefs) {
                                     (function(x : number) {
                                         adhHttpE.get(elemRefs[x]).then((element: typeof _this.elementAdapter.ElementType)
                                                                        => $scope.elements[x] = {name: _this.elementAdapter.name(element),
                                                                                                 path: _this.elementAdapter.path(element)});
                                                                                // FIXME: if i replace "{name..}" with "elements", there is on type error!
                                     })(x);
                                 }
                             })
                         }
                        ]
          }
        }
    }
}



// next steps:
// 1. extend ListingElementAdapter to ListingDocumentElementAdapter
// 2. extend listingcontaineradapter to something that has no
//    ipoolsheet!
// 3. detail view
// 4. think about what else we want to do with generic widgets



// FIXME: with the current design, if we want to change the element
// template / directive, we need to change the container template,
// because the element directive is used there as a constant.
//
// there should be a good solution to this.  possible options: (1) the
// element adapter needs to provide an injection function that takes
// the template and string-replaces the directive name in the template
// with one that suis the adapter.  (2) the adapter has a method that
// registers a new directive <listing-row element={element}>
// (preferably locally).  the listing template is only rendered after
// that directive is registered.  (3) ...?



// FIXME: heterogenous lists?
//
// rationale: on the one hand, we want to be able to restrict element
// types in the implementation of the listing and row widgets.  this
// has the benefit of giving concise implementations for specific
// container and element types, and makes the task of deriving new
// such types much less complex and much more robust.
//
// on the other hand, we want to allow for lists that contain a wide
// range of different elements in different rows, and we want to
// dispatch a different widget for each row individually.  this is the
// idea of hetergenous containers, and it can be easily implemented
// with a class HeterogenousListingElementAdapter that extends
// ListingElementAdapter.



// FIXME: good dynamic type error handling?  (this should go to Http
// service.)
