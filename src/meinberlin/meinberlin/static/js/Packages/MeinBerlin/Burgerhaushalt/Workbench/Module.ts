import AdhAbuseModule = require("../../../Abuse/Module");
import AdhCommentModule = require("../../../Comment/Module");
import AdhHttpModule = require("../../../Http/Module");
import AdhMovingColumnsModule = require("../../../MovingColumns/Module");
import AdhProcessModule = require("../../../Process/Module");
import AdhResourceAreaModule = require("../../../ResourceArea/Module");
import AdhTopLevelStateModule = require("../../../TopLevelState/Module");
import AdhPermissionsModule = require("../../../Permissions/Module");

import AdhMeinBerlinBurgerhaushaltProcessModule = require("../Process/Module");
import AdhMeinBerlinProposalModule = require("../../../Proposal/Module");

import AdhProcess = require("../../../Process/Process");

import RIBurgerhaushaltProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess");

import Workbench = require("./Workbench");


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
