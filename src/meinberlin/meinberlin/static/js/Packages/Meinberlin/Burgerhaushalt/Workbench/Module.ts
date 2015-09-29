import * as AdhAbuseModule from "../../../Abuse/Module";
import * as AdhCommentModule from "../../../Comment/Module";
import * as AdhHttpModule from "../../../Http/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhProcessModule from "../../../Process/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";

import * as AdhMeinberlinBurgerhaushaltProcessModule from "../Process/Module";
import * as AdhMeinberlinProposalModule from "../../../Proposal/Module";

import * as AdhProcess from "../../../Process/Process";

import RIBurgerhaushaltProcess from "../../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess";

import * as Workbench from "./Workbench";


export var moduleName = "adhMeinberlinBurgerhaushaltWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMeinberlinBurgerhaushaltProcessModule.moduleName,
            AdhMeinberlinProposalModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhResourceAreaProvider", Workbench.registerRoutes(RIBurgerhaushaltProcess.content_type)])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[RIBurgerhaushaltProcess.content_type] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-meinberlin-burgerhaushalt-workbench></adh-meinberlin-burgerhaushalt-workbench>");
            }];
        }])
        .directive("adhMeinberlinBurgerhaushaltWorkbench", [
            "adhTopLevelState", "adhConfig", "adhHttp", Workbench.burgerhaushaltWorkbenchDirective])
        .directive("adhMeinberlinBurgerhaushaltProposalDetailColumn", [
            "adhConfig", "adhPermissions", Workbench.burgerhaushaltProposalDetailColumnDirective])
        .directive("adhMeinberlinBurgerhaushaltProposalCreateColumn", ["adhConfig", Workbench.burgerhaushaltProposalCreateColumnDirective])
        .directive("adhMeinberlinBurgerhaushaltProposalEditColumn", ["adhConfig", Workbench.burgerhaushaltProposalEditColumnDirective])
        .directive("adhMeinberlinBurgerhaushaltDetailColumn", ["adhConfig", Workbench.burgerhaushaltDetailColumnDirective]);
};
