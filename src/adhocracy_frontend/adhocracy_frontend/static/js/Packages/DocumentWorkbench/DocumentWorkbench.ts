/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhConfig = require("../Config/Config");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUser = require("../User/User");

import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");


var pkgLocation = "/DocumentWorkbench";

export interface IDocumentWorkbenchScope extends angular.IScope {
    path : string;
    user : AdhUser.Service;
    websocketTestPaths : string;
    contentType : string;
}

export var documentWorkbench = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service,
    adhUser : AdhUser.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DocumentWorkbench.html",
        link: (scope : IDocumentWorkbenchScope) => {
            scope.path = adhConfig.rest_url + adhConfig.rest_platform_path;
            scope.contentType = RIDocument.content_type;
            scope.user = adhUser;
            scope.websocketTestPaths = JSON.stringify([scope.path]);

            // FIXME anycast
            scope.$on("$destroy", <any>adhTopLevelState.bind("view", scope));
        }
    };
};

