import * as AdhAbuseModule from "../../../Abuse/Module";
import * as AdhCommentModule from "../../../Comment/Module";
import * as AdhHttpModule from "../../../Http/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhProcessModule from "../../../Process/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";

import * as AdhMeinBerlinBurgerhaushaltProcessModule from "../Process/Module";
import * as AdhMeinBerlinProposalModule from "../../../Proposal/Module";

import * as AdhProcess from "../../../Process/Process";

import RIBurgerhaushaltProcess from "../../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess";

import * as Workbench from "./Workbench";


export var moduleName = "adhMeinBerlinBurgerhaushaltWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMeinBerlinBurgerhaushaltProcessModule.moduleName,
            AdhMeinBerlinProposalModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhResourceAreaProvider", Workbench.registerRoutes(RIBurgerhaushaltProcess.content_type)])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[RIBurgerhaushaltProcess.content_type] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-mein-berlin-burgerhaushalt-workbench></adh-mein-berlin-burgerhaushalt-workbench>");
            }];
        }])
        .directive("adhMeinBerlinBurgerhaushaltWorkbench", [
            "adhTopLevelState", "adhConfig", "adhHttp", Workbench.burgerhaushaltWorkbenchDirective])
        .directive("adhMeinBerlinBurgerhaushaltProposalDetailColumn", [
            "adhConfig", "adhPermissions", Workbench.burgerhaushaltProposalDetailColumnDirective])
        .directive("adhMeinBerlinBurgerhaushaltProposalCreateColumn", ["adhConfig", Workbench.burgerhaushaltProposalCreateColumnDirective])
        .directive("adhMeinBerlinBurgerhaushaltProposalEditColumn", ["adhConfig", Workbench.burgerhaushaltProposalEditColumnDirective])
        .directive("adhMeinBerlinBurgerhaushaltDetailColumn", ["adhConfig", Workbench.burgerhaushaltDetailColumnDirective]);
};
