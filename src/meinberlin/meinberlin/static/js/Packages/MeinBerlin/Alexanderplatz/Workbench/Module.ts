import * as AdhDocumentModule from "../../../Document/Module";
import * as AdhHttpModule from "../../../Http/Module";
import * as AdhMappingModule from "../../../Mapping/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhProcessModule from "../../../Process/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import RIAlexanderplatzProcess from "../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess";

import * as AdhMapping from "../../../Mapping/Mapping";
import * as AdhProcess from "../../../Process/Process";

import * as Workbench from "./Workbench";


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
