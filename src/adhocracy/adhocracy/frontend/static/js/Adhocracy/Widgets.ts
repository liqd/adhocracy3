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

export class Listing<ContainerAdapter extends ListingContainerAdapter, ElementAdapter extends ListingElementAdapter> {

    static templateUrl: string = "/Widgets/Listing.html";

    constructor(private containerPath: string,
                public containerAdapter: ContainerAdapter,
                public elementAdapter: ElementAdapter)
    { }

    public factory = function() : ng.IDirective {
        // FIXME: "factory" might be misinterpreted as "ListingFactory".
        // possible solutions: (1) rename; (2) implement Listing class
        // such that the instance type is '() => IDirective', and no
        // factory method is needed.

// FIXME FIRST: if this function is extracted from the object and
// passed to app.directive, it is stuck into a new object before it is
// called.  that makes "this" invalid.  (if the factory method is
// invoked, 'this' is intact, but we want to return a factory, not the
// invoked factory.)

        // FIXME: is there a way to use typescript's "typeof" on
        // this.*?  that would make these local variables unnecessary.

        debugger;

        var ca = this.containerAdapter;
        var ea = this.elementAdapter;

        return {
            restrict: "E",
            templateUrl: templatePath + "/" + Listing.templateUrl,  // FIXME: "s/Listing./self./"?
            scope: { },
            controller: ["$scope",
                         "adhHttp",
                         "adhHttp",  // FIXME(?): do we really want to duplicate adhHttp for the type system?
                         function($scope: ListingScope<typeof ca.ContainerType, typeof ea.ElementType>,
                                  adhHttpC: AdhHttp.IService<typeof ca.ContainerType>,
                                  adhHttpE: AdhHttp.IService<typeof ea.ElementType>
                                 ) : void
                         {
                             debugger;

                             adhHttpC.get(this.containerPath).then((pool) => {
                                 $scope.container = pool;
                                 $scope.elements = [];

                                 debugger;

                                 var elemRefs : string[] = this.elementAdapter.elemRefs($scope.container);
                                 for (var x in elemRefs) {
                                     (function(x : number) {
                                         adhHttpE.get(elemRefs[x]).then((element: typeof ea.ElementType)
                                                                        => $scope.elements[x] = element);
                                     })(x);
                                 }
                             })
                         }
                        ]
        }
    }
}


// FIXME: now i can't derive from ListingContainerAdapter with a more
// specific type, because that woudl require to change the references
// to ListingContainerAdapter all over the controller implementation.
// what now?
//
// pass type to class *and* instance to construtor?
//
// pass http and scope services to constructor as well?  (type
// annotation in line 79 could just be dropped.)
//
// am i right that i can't use the concrete type of ContainerAdapter
// (if it's a class template parameter), because it is unknown at
// compile time?  WAIT: the only thing we need is that
// ContainerAdapter is the same type all over.  we don't need to know
// what type exactly it is.  it should be possible to fix this!


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

