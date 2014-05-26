
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


export interface ListingScope<Container, Element> {
    container: Container;
    elements: Element[];
}

export class ListingContainerAdapter {
    public ContainerType : Types.Content<Resources.HasIPoolSheet>;

    public elemRefs(c : Types.Content<Resources.HasIPoolSheet>) : string[] {
        return c.data["adhocracy.sheets.pool.IPool"].elements;
    }
}

export class ListingElementAdapter {
    static ElementType: Types.Content<any>;

    static name(e: typeof ListingElementAdapter.ElementType) : string {  // FIXME: s/ListingContainerAdapter./self./ does not work.  what does?
        return "[content type " + e.content_type + ", resource " + e.path + "]"
    }
    static path(e: typeof ListingElementAdapter.ElementType) : string {  // FIXME: s/ListingContainerAdapter./self./ does not work.  what does?
        return e.path;
    }
}

export class Listing<Container extends ListingContainerAdapter, Element extends ListingElementAdapter> {

    static templateUrl: string = "/Widgets/Listing.html";

    constructor(private containerPath: string) {}

    public factory = function() : ng.IDirective {
        return {
            restrict: "E",
            templateUrl: templatePath + "/" + Listing.templateUrl,  // FIXME: "s/Listing./self./"?
            controller: ["$scope",
                         "adhHttp",
                         "adhHttp",  // FIXME(?): do we really want to duplicate adhHttp for the type system?
                         function(// $scope: ListingScope<Container.ContainerType, Element.ElementType>  // FIXME: this refuses to typecheck.  :(
                                  // adhHttpC: AdhHttp.IService<>,
                                  // adhHttpE: AdhHttp.IService<>
                                 ) : void
                         {
                             /*
                             adhHttpC.get(this.containerPath).then((pool) => {
                                 $scope.container = pool;
                                 $scope.elements = [];

                                 var elemRefs : string[] = containerAccess.elemRefs($scope.container);
                                 for (var x in elemRefs) {
                                     (function(x : number) {
                                         adhHttpE.get(elemRefs[x]).then((element : Element)
                                                                        => $scope.elements[x] = element);
                                     })(x);
                                 }
                             })
                             */
                         }
                        ]
        }
    }
}



/*


next: introduce Proposals in Listing clone, and replace
elementAccess.name.

next: introduce Proposal detail view in clone of the above, factor out
shared code from controller into helper attribute, and replace
controller.



export function wgtListingDocument(path:       string,
                            container:  Content<HasIDocumentSheet>,
                            element:    Content<HasIDocumentSheet>
                           ) : Directive
{
    return {
        restrict: "E"
        templateUrl: templatePath + "/Widgets/Listing.html",
        controller: ["$scope",
                     function($scope : IDocumentWorkbenchScope<Resources.HasIDocumentSheet>)



                     {
                     }]
    }
}

*/




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


// FIXME: good dynamic type error handling?

