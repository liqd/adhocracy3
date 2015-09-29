import * as AdhAbuseModule from "../../../Abuse/Module";
import * as AdhCommentModule from "../../../Comment/Module";
import * as AdhHttpModule from "../../../Http/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhProcessModule from "../../../Process/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinberlinKiezkassenProcessModule from "../Process/Module";
import * as AdhMeinberlinProposalModule from "../../../Proposal/Module";

import * as AdhProcess from "../../../Process/Process";

import RIKiezkassenProcess from "../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess";

import * as Workbench from "./Workbench";


export var moduleName = "adhMeinberlinKiezkassenWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMeinberlinKiezkassenProcessModule.moduleName,
            AdhMeinberlinProposalModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider) => {
            Workbench.registerRoutes(RIKiezkassenProcess.content_type)(adhResourceAreaProvider);
        }])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[RIKiezkassenProcess.content_type] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-meinberlin-kiezkassen-workbench></adh-meinberlin-kiezkassen-workbench>");
            }];
        }])
        .directive("adhMeinberlinKiezkassenWorkbench", [
            "adhTopLevelState", "adhConfig", "adhHttp", Workbench.kiezkassenWorkbenchDirective])
        .directive("adhMeinberlinKiezkassenProposalDetailColumn", [
            "adhConfig", "adhPermissions", Workbench.kiezkassenProposalDetailColumnDirective])
        .directive("adhMeinberlinKiezkassenProposalCreateColumn", ["adhConfig", Workbench.kiezkassenProposalCreateColumnDirective])
        .directive("adhMeinberlinKiezkassenProposalEditColumn", ["adhConfig", Workbench.kiezkassenProposalEditColumnDirective])
        .directive("adhMeinberlinKiezkassenDetailColumn", ["adhConfig", Workbench.kiezkassenDetailColumnDirective])
        .directive("adhMeinberlinKiezkassenEditColumn", ["adhConfig", Workbench.kiezkassenEditColumnDirective]);
};
