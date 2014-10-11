/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhConfig = require("../Config/Config");
import AdhUser = require("../User/User");

import RIProposal = require("../../Resources_/adhocracy_core/resources/sample_proposal/IProposal");

var pkgLocation = "/DocumentWorkbench";

interface IDocumentWorkbenchScope extends ng.IScope {
    path : string;
    user : AdhUser.User;
    websocketTestPaths : string;
    contentType : string;
}

export class DocumentWorkbench {
    public static templateUrl : string = pkgLocation + "/DocumentWorkbench.html";

    public createDirective(adhConfig : AdhConfig.Type) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + _class.templateUrl,
            controller: ["adhUser", "$scope", (
                adhUser : AdhUser.User,
                $scope : IDocumentWorkbenchScope
            ) : void => {
                $scope.path = adhConfig.rest_url + adhConfig.rest_platform_path;
                $scope.contentType = RIProposal.content_type;
                $scope.user = adhUser;
                $scope.websocketTestPaths = JSON.stringify([$scope.path]);
            }]
        };
    }
}
