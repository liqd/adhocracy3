import * as AdhAbuseModule from "../../../Abuse/Module";
import * as AdhCommentModule from "../../../Comment/Module";
import * as AdhHttpModule from "../../../Http/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhProcessModule from "../../../Process/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinBerlinKiezkassenProcessModule from "../Process/Module";
import * as AdhMeinBerlinProposalModule from "../../../Proposal/Module";

import * as AdhProcess from "../../../Process/Process";

import RIKiezkassenProcess from "../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess";

import * as Workbench from "./Workbench";


export var moduleName = "adhMeinBerlinKiezkassenWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMeinBerlinKiezkassenProcessModule.moduleName,
            AdhMeinBerlinProposalModule.moduleName,
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
                return $q.when("<adh-mein-berlin-kiezkassen-workbench></adh-mein-berlin-kiezkassen-workbench>");
            }];
        }])
        .directive("adhMeinBerlinKiezkassenWorkbench", [
            "adhTopLevelState", "adhConfig", "adhHttp", Workbench.kiezkassenWorkbenchDirective])
        .directive("adhMeinBerlinKiezkassenProposalDetailColumn", [
            "adhConfig", "adhPermissions", Workbench.kiezkassenProposalDetailColumnDirective])
        .directive("adhMeinBerlinKiezkassenProposalCreateColumn", ["adhConfig", Workbench.kiezkassenProposalCreateColumnDirective])
        .directive("adhMeinBerlinKiezkassenProposalEditColumn", ["adhConfig", Workbench.kiezkassenProposalEditColumnDirective])
        .directive("adhMeinBerlinKiezkassenDetailColumn", ["adhConfig", Workbench.kiezkassenDetailColumnDirective])
        .directive("adhMeinBerlinKiezkassenEditColumn", ["adhConfig", Workbench.kiezkassenEditColumnDirective]);
};
