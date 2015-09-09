import AdhDocumentModule = require("../../../Document/Module");
import AdhHttpModule = require("../../../Http/Module");
import AdhMappingModule = require("../../../Mapping/Module");
import AdhMovingColumnsModule = require("../../../MovingColumns/Module");
import AdhPermissionsModule = require("../../../Permissions/Module");
import AdhProcessModule = require("../../../Process/Module");
import AdhResourceAreaModule = require("../../../ResourceArea/Module");
import AdhTopLevelStateModule = require("../../../TopLevelState/Module");

import RIAlexanderplatzProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess");

import AdhMapping = require("../../../Mapping/Mapping");
import AdhProcess = require("../../../Process/Process");

import Workbench = require("./Workbench");


export var moduleName = "adhMeinBerlinAlexanderplatzWorkbench";

export var register = (angular) => {
    var processType = RIAlexanderplatzProcess.content_type;

    angular
        .module(moduleName, [
            AdhDocumentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMappingModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[processType] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-mein-berlin-alexanderplatz-workbench></adh-mein-berlin-alexanderplatz-workbench>");
            }];
        }])
        .config(["adhResourceAreaProvider", Workbench.registerRoutes(processType)])
        .config(["adhMapDataProvider", (adhMapDataProvider : AdhMapping.MapDataProvider) => {
            adhMapDataProvider.icons["document"] = {
                className: "icon-board-pin",
                iconAnchor: [20, 39],
                iconSize: [40, 40]
            };
            adhMapDataProvider.icons["document-selected"] = {
                className: "icon-board-pin is-active",
                iconAnchor: [20, 39],
                iconSize: [40, 40]
            };
        }])
        .directive("adhMeinBerlinAlexanderplatzWorkbench", [
            "adhConfig", "adhTopLevelState", Workbench.workbenchDirective])
        .directive("adhMeinBerlinAlexanderplatzProcessColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", "adhHttp", Workbench.processDetailColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzDocumentDetailColumn", [
            "adhConfig",
            "adhPermissions",
            "adhTopLevelState",
            "adhHttp",
            "adhResourceUrlFilter",
            "$location",
            "$window",
            Workbench.documentDetailColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzProposalDetailColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", Workbench.proposalDetailColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzDocumentCreateColumn", [
            "adhConfig", "adhHttp", "adhTopLevelState", "adhResourceUrlFilter", Workbench.documentCreateColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzProposalCreateColumn", [
            "adhConfig", "adhTopLevelState", "adhResourceUrlFilter", Workbench.proposalCreateColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzDocumentEditColumn", [
            "adhConfig", "adhHttp", "adhTopLevelState", "adhResourceUrlFilter", Workbench.documentEditColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzProposalEditColumn", [
            "adhConfig", "adhTopLevelState", "adhResourceUrlFilter", Workbench.proposalEditColumnDirective]);
};
