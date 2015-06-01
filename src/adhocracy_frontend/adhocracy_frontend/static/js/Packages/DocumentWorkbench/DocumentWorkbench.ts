/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhComment = require("../Comment/Comment");
import AdhConfig = require("../Config/Config");
import AdhMovingColumns = require("../MovingColumns/MovingColumns");
import AdhProcess = require("../Process/Process");
import AdhProposal = require("../Proposal/Proposal");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUser = require("../User/User");

import RIBasicPool = require("../../Resources_/adhocracy_core/resources/pool/IBasicPool");
import RIProposal = require("../../Resources_/adhocracy_core/resources/sample_proposal/IProposal");
import RIProposalVersion = require("../../Resources_/adhocracy_core/resources/sample_proposal/IProposalVersion");
import RIUser = require("../../Resources_/adhocracy_core/resources/principal/IUser");
import RIUsersService = require("../../Resources_/adhocracy_core/resources/principal/IUsersService");


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
            scope.contentType = RIProposal.content_type;
            scope.user = adhUser;
            scope.websocketTestPaths = JSON.stringify([scope.path]);

            // FIXME anycast
            scope.$on("$destroy", <any>adhTopLevelState.bind("view", scope));
        }
    };
};


export var moduleName = "adhDocumentWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhComment.moduleName,
            AdhMovingColumns.moduleName,
            AdhProcess.moduleName,
            AdhProposal.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName,
            AdhUser.moduleName
        ])
        .config(["adhProcessProvider", (adhProcessProvider) => {
            adhProcessProvider.templateFactories[""] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-document-workbench></adh-document-workbench>");
            }];
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .default(RIBasicPool, "", "", "", {
                    space: "content",
                    movingColumns: "is-show-show-hide",
                    content2Url: ""
                })
                .default(RIProposalVersion, "", "", "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specific(RIProposalVersion, "", "", "", () => (resource : RIProposalVersion) => {
                    return {
                        content2Url: resource.path
                    };
                })
                .default(RIUser, "", "", "", {
                    space: "user",
                    movingColumns: "is-show-show-hide"
                })
                .default(RIUsersService, "", "", "", {
                    space: "user",
                    movingColumns: "is-show-show-hide"
                });
        }])
        .directive("adhDocumentWorkbench", ["adhConfig", "adhTopLevelState", "adhUser", documentWorkbench]);
};
