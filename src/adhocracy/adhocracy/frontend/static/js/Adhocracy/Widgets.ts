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


//////////////////////////////////////////////////////////////////////
// Listings

export class AbstractListingContainerAdapter<Type> {
    public ContainerType : Type;
    public elemRefs(container : Type) : string[] {
        return [];
    }
}

export class ListingPoolAdapter extends AbstractListingContainerAdapter<Types.Content<Resources.HasIPoolSheet>> {
    public elemRefs(container) {
        // FIXME: derived type of argument c appears to be 'any',
        // should be 'Types.Content<Resources.HasIPoolSheet>'!
        // http://stackoverflow.com/questions/23893372/expecting-type-error-when-extending-and-generic-class
        return container.data["adhocracy.sheets.pool.IPool"].elements;
    }
}

export interface ListingScope<Container> {
    path: string;
    title: string;
    container: Container;
    elements: string[];
}

// FIXME: the way Listing works now is similar to ngRepeat, but it
// does not allow for the template author to control the name of the
// iterator.  Instead of something like:
//
// <listing element="row">
//   <element path="{{row}}"></element>
// </listing>
//
// She has to write:
//
// <listing>
//   <element path="{{element}}"></element>
// </listing>
//
// and implicitly know that Listing propagates the identifier
// ``element`` to the element's scope.
export class Listing<ContainerAdapter extends AbstractListingContainerAdapter<Types.Content<any>>>
{
    public static templateUrl: string = "/Widgets/Listing.html";

    constructor(public containerAdapter: ContainerAdapter) {
    }

    public factory() {
        // REVIEW: please resolve this FIXME (or remove)
        // FIXME: "factory" might be misinterpreted as "ListingFactory".
        // possible solutions: (1) rename; (2) implement Listing class
        // such that the instance type is '() => IDirective', and no
        // factory method is needed.

        var _this = this;  // REVIEW: can we use () => {} syntax instead of this explicit declaration?
        // REVIEW: this looks strange. I guess there is a more "natural" way to do this. Maybe something with `prototype`.
        var _class = (<any>_this).constructor;

        return {
            restrict: "E",
            templateUrl: templatePath + "/" + _class.templateUrl,
            scope: {
                path: "@",
                title: "@"
            },
            transclude: true,
            controller: ["$scope",
                         "adhHttp",
                         function($scope: ListingScope<typeof _this.containerAdapter.ContainerType>,
                                  adhHttp: AdhHttp.IService<typeof _this.containerAdapter.ContainerType>
                                  // FIXME: i think these all evaluate to 'any' statically.
                                 ) : void
                         {
                             adhHttp.get($scope.path).then((pool: typeof _this.containerAdapter.ContainerType) => {
                                 $scope.container = pool;
                                 $scope.elements = _this.containerAdapter.elemRefs($scope.container);
                             });
                         }
                        ]
        };
    }
}


//////////////////////////////////////////////////////////////////////
// Elements

export class AbstractListingElementAdapter<Type> {
    public ElementType: Type;

    constructor(public $q: ng.IQService) { }

    public name: (element: Type) => ng.IPromise<string> = (element) => {
        var deferred = this.$q.defer();
        deferred.resolve("");
        return deferred.promise;
    };
    public path: (element: Type) => string = () => {
        return "";
    };
}

export class ListingElementAdapter extends AbstractListingElementAdapter<Types.Content<any>> {
    public name = (element) => {
        var deferred = this.$q.defer();
        deferred.resolve("[content type " + element.content_type + ", resource " + element.path + "]");
        return deferred.promise;
    };
    public path = (element) => {
        return element.path;
    };
}

export class ListingElementTitleAdapter extends AbstractListingElementAdapter<Types.Content<Resources.HasIVersionsSheet>> {
    constructor(public $q: ng.IQService,
                public adhHttp: AdhHttp.IService<Types.Content<Resources.HasIDocumentSheet>>) {
        super($q);
    }

    public name = (element) => {
        var versionPaths: string[] = element.data["adhocracy.sheets.versions.IVersions"].elements;
        var lastVersionPath: string = versionPaths[versionPaths.length - 1];

        return this.adhHttp.get(lastVersionPath)
            .then((lastVersion) => {
                return lastVersion.data["adhocracy.sheets.document.IDocument"].title;
            });
    };

    public path = (element) => {
        return element.path;
    };
}

export interface ListingElementScope<Container> {
    path: string;
    name: string;
}

export class ListingElement<ElementAdapter extends AbstractListingElementAdapter<Types.Content<any>>>
{
    public static templateUrl: string = "/Widgets/ListingElement.html";

    constructor(public elementAdapter: ElementAdapter) {
    }

    public factory() {   // REVIEW: see Listing
        var _this = this;  // REVIEW: see Listing
        // REVIEW: see Listing
        var _class = (<any>this).constructor;

        return {
            restrict: "E",
            templateUrl: templatePath + "/" + _class.templateUrl,
            scope: {
                path: "@"
            },
            controller: ["$scope",
                         "adhHttp",
                         function($scope: ListingElementScope<typeof _this.elementAdapter.ElementType>,
                                  adhHttp: AdhHttp.IService<typeof _this.elementAdapter.ElementType>
                                 ) : void
                         {
                             adhHttp.get($scope.path)
                                 .then(_this.elementAdapter.name)
                                 .then((name) => $scope.name = name);
                         }
                        ]
        };
    }
}
