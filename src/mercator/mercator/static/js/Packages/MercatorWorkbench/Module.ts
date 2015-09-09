import AdhAbuseModule = require("../Abuse/Module");
import AdhCommentModule = require("../Comment/Module");
import AdhHttpModule = require("../Http/Module");
import AdhListingModule = require("../Listing/Module");
import AdhMercatorProposalModule = require("../MercatorProposal/Module");
import AdhMovingColumnsModule = require("../MovingColumns/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhResourceAreaModule = require("../ResourceArea/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");
import AdhUserModule = require("../User/Module");

import RIProcess = require("../../Resources_/adhocracy_mercator/resources/mercator/IProcess");

import MercatorWorkbench = require("./MercatorWorkbench");


export var moduleName = "adhMercatorWorkbench";

export var register = (angular) => {
    var processType = RIProcess.content_type;

    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhListingModule.moduleName,
            AdhMercatorProposalModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName,
            AdhUserModule.moduleName
        ])
        .config(["adhResourceAreaProvider", MercatorWorkbench.registerRoutes(RIProcess.content_type)])
        .config(["adhProcessProvider", (adhProcessProvider) => {
            adhProcessProvider.templateFactories[processType] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-mercator-workbench></adh-mercator-workbench>");
            }];
        }])
        .directive("adhMercatorWorkbench", ["adhConfig", "adhTopLevelState", MercatorWorkbench.mercatorWorkbenchDirective])
        .directive("adhMercatorProposalCreateColumn", [
            "adhConfig", "adhResourceUrlFilter", "$location", MercatorWorkbench.mercatorProposalCreateColumnDirective])
        .directive("adhMercatorProposalDetailColumn", [
            "$window", "adhTopLevelState", "adhPermissions", "adhConfig", MercatorWorkbench.mercatorProposalDetailColumnDirective])
        .directive("adhMercatorProposalEditColumn", [
            "adhConfig", "adhResourceUrlFilter", "$location", MercatorWorkbench.mercatorProposalEditColumnDirective])
        .directive("adhMercatorProposalListingColumn",
            ["adhConfig", "adhHttp", "adhTopLevelState", MercatorWorkbench.mercatorProposalListingColumnDirective]);
};
