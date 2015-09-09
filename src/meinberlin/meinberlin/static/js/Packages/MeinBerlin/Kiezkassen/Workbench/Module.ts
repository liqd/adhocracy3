import AdhAbuseModule = require("../../../Abuse/Module");
import AdhCommentModule = require("../../../Comment/Module");
import AdhHttpModule = require("../../../Http/Module");
import AdhMovingColumnsModule = require("../../../MovingColumns/Module");
import AdhPermissionsModule = require("../../../Permissions/Module");
import AdhProcessModule = require("../../../Process/Module");
import AdhResourceAreaModule = require("../../../ResourceArea/Module");
import AdhTopLevelStateModule = require("../../../TopLevelState/Module");

import AdhMeinBerlinKiezkassenProcessModule = require("../Process/Module");
import AdhMeinBerlinProposalModule = require("../../../Proposal/Module");

import AdhProcess = require("../../../Process/Process");

import RIKiezkassenProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess");

import Workbench = require("./Workbench");


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
