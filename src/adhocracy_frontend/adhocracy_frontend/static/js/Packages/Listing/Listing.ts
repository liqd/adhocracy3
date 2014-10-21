/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/lodash/lodash.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhPermissions = require("../Permissions/Permissions");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhWebSocket = require("../WebSocket/WebSocket");

import ResourcesBase = require("../../ResourcesBase");

import SIPool = require("../../Resources_/adhocracy_core/sheets/pool/IPool");

var pkgLocation = "/Listing";

//////////////////////////////////////////////////////////////////////
// Listings

export interface IListingContainerAdapter {
    // A list of elements that should be displayed
    elemRefs(any) : string[];

    // The pool a new element should be posted to.
    poolPath(any) : string;
}

export class ListingPoolAdapter implements IListingContainerAdapter {
    public elemRefs(container : ResourcesBase.Resource) {
        return container.data[SIPool.nick].elements;
    }

    public poolPath(container : ResourcesBase.Resource) {
        return container.path;
    }
}

export interface ListingScope<Container> extends ng.IScope {
    path : string;
    actionColumn : boolean;
    contentType? : string;
    container : Container;
    poolPath : string;
    poolOptions : AdhHttp.IOptions;
    createPath? : string;
    elements : string[];
    update : () => ng.IPromise<void>;
    wshandle : string;
    clear : () => void;
    show : { createForm : boolean };
    onCreate : () => void;
    showCreateForm : () => void;
    hideCreateForm : () => void;
}

// FIXME: as the listing elements are tracked by their $id (the element path) in the listing template, we don't allow duplicate elements
// in one listing. We should add a proper warning if that occurs or handle that case properly.

export class Listing<Container extends ResourcesBase.Resource> {
    public static templateUrl : string = pkgLocation + "/Listing.html";

    constructor(private containerAdapter : IListingContainerAdapter) {}

    public createDirective(adhConfig : AdhConfig.IService, adhWebSocket: AdhWebSocket.IService) {
        var _self = this;
        var _class = (<any>_self).constructor;

        var unregisterWebsocket = (scope) => {
            if (typeof scope.poolPath !== "undefined" && typeof scope.wshandle !== "undefined") {
                adhWebSocket.unregister(scope.poolPath, scope.wshandle);
                scope.wshandle = undefined;
            }
        };

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + _class.templateUrl,
            scope: {
                path: "@",
                actionColumn: "@",
                contentType: "@"
            },
            transclude: true,
            link: (scope, element, attrs, controller, transclude) => {
                element.on("$destroy", () => {
                    unregisterWebsocket(scope);
                });
            },
            controller: ["$scope", "adhHttp", "adhPreliminaryNames", "adhPermissions", (
                $scope: ListingScope<Container>,
                adhHttp: AdhHttp.Service<Container>,
                adhPreliminaryNames : AdhPreliminaryNames,
                adhPermissions : AdhPermissions.Service
            ) : void => {
                $scope.show = {createForm: false};

                $scope.showCreateForm = () => {
                    $scope.show.createForm = true;
                    $scope.createPath = adhPreliminaryNames.nextPreliminary();
                };

                $scope.hideCreateForm = () => {
                    $scope.show.createForm = false;
                };

                $scope.update = () : ng.IPromise<void> => {
                    var params = <any>{};
                    if (typeof $scope.contentType !== "undefined") {
                        params.content_type = $scope.contentType;
                    }
                    return adhHttp.get($scope.path, params).then((container) => {
                        $scope.container = container;
                        $scope.poolPath = _self.containerAdapter.poolPath($scope.container);
                        $scope.elements = _self.containerAdapter.elemRefs($scope.container);

                        return adhPermissions.bindScope($scope, $scope.poolPath, "poolOptions");
                    });
                };

                $scope.clear = () : void => {
                    $scope.container = undefined;
                    $scope.poolPath = undefined;
                    $scope.elements = [];
                };

                $scope.onCreate = () : void => {
                    $scope.update();
                    $scope.hideCreateForm();
                };

                $scope.$watch("path", (newPath : string) => {
                    unregisterWebsocket($scope);

                    if (newPath) {
                        // NOTE: Ideally we would like to first subscribe to
                        // websocket messages and only then get the resource in
                        // order to not miss any messages in between. But in
                        // order to subscribe we already need the resource. So
                        // that is not possible.
                        $scope.update().then(() => {
                            try {
                                $scope.wshandle = adhWebSocket.register($scope.poolPath, $scope.update);
                            } catch (e) {
                                console.log(e);
                                console.log("Will continue on resource " + $scope.poolPath + " without server bind.");
                            }
                        });
                    } else {
                        $scope.clear();
                    }
                });
            }]
        };
    }
}
