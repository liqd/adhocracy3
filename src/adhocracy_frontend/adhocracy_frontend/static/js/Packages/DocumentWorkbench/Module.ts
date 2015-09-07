import AdhCommentModule = require("../Comment/Module");
import AdhMovingColumnsModule = require("../MovingColumns/Module");
import AdhProcessModule = require("../Process/Module");
import AdhResourceAreaModule = require("../ResourceArea/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");
import AdhUserModule = require("../User/Module");

import AdhResourceArea = require("../ResourceArea/ResourceArea");

import AdhDocumentWorkbench = require("./DocumentWorkbench");

import RIBasicPool = require("../../Resources_/adhocracy_core/resources/pool/IBasicPool");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");
import RIUser = require("../../Resources_/adhocracy_core/resources/principal/IUser");
import RIUsersService = require("../../Resources_/adhocracy_core/resources/principal/IUsersService");


export var moduleName = "adhDocumentWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhCommentModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName,
            AdhUserModule.moduleName
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
                .default(RIDocumentVersion, "", "", "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specific(RIDocumentVersion, "", "", "", () => (resource : RIDocumentVersion) => {
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
        .directive("adhDocumentWorkbench", ["adhConfig", "adhTopLevelState", "adhUser", AdhDocumentWorkbench.documentWorkbench]);
};
