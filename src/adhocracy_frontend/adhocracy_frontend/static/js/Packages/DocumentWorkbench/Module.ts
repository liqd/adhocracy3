import * as AdhCommentModule from "../Comment/Module";
import * as AdhMovingColumnsModule from "../MovingColumns/Module";
import * as AdhProcessModule from "../Process/Module";
import * as AdhResourceAreaModule from "../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";
import * as AdhUserModule from "../User/Module";

import * as AdhResourceArea from "../ResourceArea/ResourceArea";

import * as AdhDocumentWorkbench from "./DocumentWorkbench";

import RIBasicPool from "../../Resources_/adhocracy_core/resources/pool/IBasicPool";
import RIDocumentVersion from "../../Resources_/adhocracy_core/resources/document/IDocumentVersion";
import RIUser from "../../Resources_/adhocracy_core/resources/principal/IUser";
import RIUsersService from "../../Resources_/adhocracy_core/resources/principal/IUsersService";


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
