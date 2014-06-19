/// <reference path="../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../_all.d.ts"/>

import Types = require("./Types");
import AdhHttp = require("./Services/Http");
import AdhConfig = require("./Services/Config");

import Resources = require("./Resources");


//////////////////////////////////////////////////////////////////////
// Listings

export class AbstractListingContainerAdapter {
    public elemRefs(container : any) : string[] {
        return [];
    }
}

export class ListingPoolAdapter extends AbstractListingContainerAdapter {
    public elemRefs(container : Types.Content<Resources.HasIPoolSheet>) {
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
export class Listing<Container extends Types.Content<any>, ContainerAdapter extends AbstractListingContainerAdapter> {
    public static templateUrl: string = "/Widgets/Listing.html";

    constructor(public containerAdapter: ContainerAdapter) {}

    public createDirective(adhConfig: AdhConfig.Type) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/" + _class.templateUrl,
            scope: {
                path: "@",
                title: "@"
            },
            transclude: true,
            controller: ["$scope", "adhHttp", (
                $scope: ListingScope<Container>,
                adhHttp: AdhHttp.IService<Container>
            ) : void => {
                adhHttp.get($scope.path).then((pool: Container) => {
                    $scope.container = pool;
                    $scope.elements = _self.containerAdapter.elemRefs($scope.container);
                });
            }]
        };
    }
}


//////////////////////////////////////////////////////////////////////
// Elements

export class AbstractListingElementAdapter {
    constructor(public $q: ng.IQService) {}

    public name: (element: any) => ng.IPromise<string> = (element) => {
        var deferred = this.$q.defer();
        deferred.resolve("");
        return deferred.promise;
    };
    public path: (element: any) => string = (element) => {
        return "";
    };
}

export class ListingElementAdapter extends AbstractListingElementAdapter {
    public name: (element: Types.Content<any>) => ng.IPromise<string> = (element) => {
        var deferred = this.$q.defer();
        deferred.resolve("[content type " + element.content_type + ", resource " + element.path + "]");
        return deferred.promise;
    };
    public path: (element: Types.Content<any>) => string = (element) => {
        return element.path;
    };
}

export class ListingElementTitleAdapter extends AbstractListingElementAdapter {
    constructor(
        public $q: ng.IQService,
        public adhHttp: AdhHttp.IService<Types.Content<Resources.HasIDocumentSheet>>
    ) {
        super($q);
    }

    public name: (element: Types.Content<Resources.HasIVersionsSheet>) => ng.IPromise<string> = (element) => {
        var versionPaths: string[] = element.data["adhocracy.sheets.versions.IVersions"].elements;
        var lastVersionPath: string = versionPaths[versionPaths.length - 1];

        return this.adhHttp.get(lastVersionPath)
            .then((lastVersion) => {
                return lastVersion.data["adhocracy.sheets.document.IDocument"].title;
            });
    };

    public path: (element: Types.Content<Resources.HasIVersionsSheet>) => string = (element) => {
        return element.path;
    };
}

export interface ListingElementScope {
    path: string;
    name: string;
}

export class ListingElement<Element extends Types.Content<any>, ElementAdapter extends AbstractListingElementAdapter> {
    public static templateUrl: string = "/Widgets/ListingElement.html";

    constructor(public elementAdapter: ElementAdapter) {}

    public createDirective(adhConfig: AdhConfig.Type) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/" + _class.templateUrl,
            scope: {
                path: "@"
            },
            controller: ["$scope", "adhHttp", (
                $scope: ListingElementScope,
                adhHttp: AdhHttp.IService<Element>
            ) : void => {
                adhHttp.get($scope.path)
                    .then(_self.elementAdapter.name)
                    .then((name) => $scope.name = name);
            }]
        };
    }
}
