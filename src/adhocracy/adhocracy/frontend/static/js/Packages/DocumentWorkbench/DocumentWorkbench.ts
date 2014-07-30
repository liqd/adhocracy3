/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhConfig = require("../Config/Config");
import AdhUser = require("../User/User");

var pkgLocation = "/DocumentWorkbench";

interface IDocumentWorkbenchScope extends ng.IScope {
    path : string;
    user : AdhUser.User;
    insertParagraph : (any) => void;
}

export class DocumentWorkbench {
    public static templateUrl: string = pkgLocation + "/DocumentWorkbench.html";

    public createDirective(adhConfig: AdhConfig.Type) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + _class.templateUrl,
            controller: ["adhUser", "$scope", (
                adhUser : AdhUser.User,
                $scope : IDocumentWorkbenchScope
            ) : void => {
                $scope.path = adhConfig.root_path;
                $scope.user = adhUser;

                $scope.insertParagraph = (proposalVersion) => {
                    // This function is called when we create a new proposal ourselves.
                    // It could be used to update the proposal list.
                };
            }]
        };
    }
}
