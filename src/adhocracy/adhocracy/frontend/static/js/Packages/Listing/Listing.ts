/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import AdhHttp = require("../Http/Http");
import AdhWebSocket = require("../WebSocket/WebSocket");
import AdhConfig = require("../Config/Config");

import Resources = require("../../Resources");
import SIPool = require("../../Resources_/adhocracy/sheets/pool/IPool");

var pkgLocation = "/Listing";

//////////////////////////////////////////////////////////////////////
// Listings

export class AbstractListingContainerAdapter {
    public elemRefs(container : any) : string[] {
        return [];
    }
}

export class ListingPoolAdapter extends AbstractListingContainerAdapter {
    public elemRefs(container : Resources.Content<SIPool.HasAdhocracySheetsPoolIPool>) {
        return container.data["adhocracy.sheets.pool.IPool"].elements;
    }
}

export interface ListingScope<Container> {
    path : string;
    title : string;
    container : Container;
    elements : string[];
    update : (...any) => ng.IPromise<void>;
    wshandle : string;
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
//
//
// FIXME: as the listing elements are tracked by their $id (the element path) in the listing template, we don't allow duplicate elements
// in one listing. We should add a proper warning if that occurs or handle that case properly.

export class Listing<Container extends Resources.Content<any>, ContainerAdapter extends AbstractListingContainerAdapter> {
    public static templateUrl : string = pkgLocation + "/Listing.html";

    constructor(private containerAdapter : ContainerAdapter) {}

    public createDirective(adhConfig : AdhConfig.Type, adhWebSocket: AdhWebSocket.IService) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + _class.templateUrl,
            scope: {
                path: "@",
                title: "@"
            },
            transclude: true,
            link: (scope, element, attrs, controller, transclude) => {
                element.on("$destroy", () => {
                    if (typeof scope.wshandle === 'string') {
                        adhWebSocket.unregister(scope.path, scope.wshandle);
                    }
                });
            },
            controller: ["$scope", "adhHttp", "adhDone", (
                $scope: ListingScope<Container>,
                adhHttp: AdhHttp.Service<Container>,
                adhDone
            ) : void => {
                $scope.update = () : ng.IPromise<void> => {
                    return adhHttp.get($scope.path).then((pool) => {
                        $scope.container = pool;
                        $scope.elements = _self.containerAdapter.elemRefs($scope.container);
                    });
                };

                // (The call order is important: first subscribe to
                // the updates, then get an initial copy.)
                try {
                    $scope.wshandle = adhWebSocket.register($scope.path, $scope.update);
                } catch (e) {
                    console.log(e);
                    console.log("Will continue on resource " + $scope.path + " without server bind.");
                }

                $scope.update().then(adhDone);
            }]
        };
    }
}
