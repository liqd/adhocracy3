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

export class AbstractListingContainerAdapter<T> {
    public ContainerType : T;
    public elemRefs(c : T) : string[] {
        return [];
    }
}

export class ListingContainerAdapter extends AbstractListingContainerAdapter<Types.Content<Resources.HasIPoolSheet>> {
    public elemRefs(c) {
        // FIXME: derived type of argument c appears to be 'any',
        // should be 'Types.Content<Resources.HasIPoolSheet>'!
        // http://stackoverflow.com/questions/23893372/expecting-type-error-when-extending-and-generic-class
        return c.data["adhocracy.sheets.pool.IPool"].elements;
    }
}

export interface ListingScope<Container> {
    path: string;
    title: string;
    container: Container;
    elements: string[];
}

export class Listing<ContainerAdapter extends AbstractListingContainerAdapter<Types.Content<any>>>
{
    public static templateUrl: string = "/Widgets/Listing.html";

    constructor(public containerAdapter: ContainerAdapter) {
    }

    public factory() {
        // FIXME: "factory" might be misinterpreted as "ListingFactory".
        // possible solutions: (1) rename; (2) implement Listing class
        // such that the instance type is '() => IDirective', and no
        // factory method is needed.

        var _this = this;
        var _class = (<any>_this).constructor;

        return {
            restrict: "E",
            templateUrl: templatePath + "/" + _class.templateUrl,
            scope: {
                path: '@',
                title: '@'
            },
            transclude: true,
            controller: ["$scope",
                         "adhHttp",
                         function($scope: ListingScope<typeof _this.containerAdapter.ContainerType>,
                                  adhHttpC: AdhHttp.IService<typeof _this.containerAdapter.ContainerType>
                                  // FIXME: how can i see the value of these 'typeof' expressions?
                                 ) : void
                         {
                             adhHttpC.get($scope.path).then((pool: typeof _this.containerAdapter.ContainerType) => {
                                 $scope.container = pool;
                                 $scope.elements = _this.containerAdapter.elemRefs($scope.container);
                             })
                         }
                        ]
        }
    }
}


//////////////////////////////////////////////////////////////////////
// Elements

export class AbstractListingElementAdapter<T> {
    public ElementType: T;

    constructor(public $q: ng.IQService) { }

    public name: (e: T) => ng.IPromise<string> = (e) => {
        var deferred = this.$q.defer();
        deferred.resolve("");
        return deferred.promise;
    }
    public path: (e: T) => string = () => {
        return "";
    }
}

export class ListingElementAdapter extends AbstractListingElementAdapter<Types.Content<any>> {
    constructor(public $q: ng.IQService) {
        super($q);
    }

    public name = (e) => {
        var deferred = this.$q.defer();
        deferred.resolve("[content type " + e.content_type + ", resource " + e.path + "]");
        return deferred.promise;
    }
    public path = (e) => {
        return e.path;
    }
}

export class ListingElementTitleAdapter extends AbstractListingElementAdapter<Types.Content<Resources.HasIVersionsSheet>> {
                                           // FIXME: should the type constraint here say anything about the document sheet in the version resource?
    constructor(public $q: ng.IQService,
                public adhHttp: AdhHttp.IService<Types.Content<Resources.HasIDocumentSheet>>) {
        super($q);
    }

    public name = (e) => {
        var versionPaths: string[] = e.data["adhocracy.sheets.versions.IVersions"].elements;
        var lastVersionPath: string = versionPaths[versionPaths.length-1];

        return this.adhHttp.get(lastVersionPath)
            .then((lastVersion) => {
                return lastVersion.data["adhocracy.sheets.document.IDocument"].title;
            });
    }

    public path = (e) => {
        return e.path;
    }
}

export interface ListingElementScope<Container> {
    path: string;
    name: string;

    element: string;  // FIXME: remove this once bug concerning
                      // ListingElement scope attribute is fixed.
}

export class ListingElement<ElementAdapter extends AbstractListingElementAdapter<Types.Content<any>>>
{
    public static templateUrl: string = "/Widgets/ListingElement.html";

    constructor(public elementAdapter: ElementAdapter) {
    }

    public factory() {
        var _this = this;  // FIXME: can we use () => {} syntax instead of this explicit declaration?
        var _class = (<any>this).constructor;

        return {
            restrict: "E",
            templateUrl: templatePath + "/" + _class.templateUrl,
            // scope: { path: '=element' },
            //
            // FIXME: the above scope attribute is supposed to
            // generate a new isolated child scop and import 'element'
            // from the parent scope as 'path'.  this results in path
            // being undefined, but if the scope is not isolated at
            // all, $scope.element contains the expected value (see
            // below).  my best idea so far is that this is because
            // there are two scopes between this one and the one that
            // defines 'element', and '=element' only searches the
            // parent scope, not all ancestor scopes.  not sure what
            // to do about this.  (mf)
            controller: ["$scope",
                         "adhHttp",
                         function($scope: ListingElementScope<typeof _this.elementAdapter.ElementType>,
                                  adhHttpE: AdhHttp.IService<typeof _this.elementAdapter.ElementType>
                                 ) : void
                         {
                             $scope.path = $scope.element;  // FIXME see issue in scope attribute above.

                             adhHttpE.get($scope.path)
                                 .then(_this.elementAdapter.name)
                                 .then((name) => $scope.name = name);
                         }
                        ]
        }
    }
}



// next steps:
// 1. detail view
// 2. think about what else we want to do with generic widgets



// FIXME: extend ListingContainerAdapter to something that has no
// IPoolSheet.


// a note on heterogenous lists.
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
// service.)  also: dynamic handling of 404-errors and others.
