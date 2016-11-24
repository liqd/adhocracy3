import * as AdhDocumentModule from "../../../Core/Document/Module";
import * as AdhHttpModule from "../../../Core/Http/Module";
import * as AdhMappingModule from "../../../Core/Mapping/Module";
import * as AdhMovingColumnsModule from "../../../Core/MovingColumns/Module";
import * as AdhNamesModule from "../../../Core/Names/Module";
import * as AdhPermissionsModule from "../../../Core/Permissions/Module";
import * as AdhProcessModule from "../../../Core/Process/Module";
import * as AdhResourceAreaModule from "../../../Core/ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../Core/TopLevelState/Module";

import * as AdhNames from "../../../Core/Names/Names";
import * as AdhProcess from "../../../Core/Process/Process";
import * as AdhProposal from "../../../Core/Proposal/Proposal";
import * as AdhWorkbench from "../../../Core/Workbench/Workbench";

import RIGeoProposal from "../../../../Resources_/adhocracy_core/resources/proposal/IGeoProposal";
import RIGeoProposalVersion from "../../../../Resources_/adhocracy_core/resources/proposal/IGeoProposalVersion";
import RIAlexanderplatzProcess from "../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess";

import * as Workbench from "./Workbench";


export var moduleName = "adhMeinberlinAlexanderplatzWorkbench";

export var register = (angular) => {
    var processType = RIAlexanderplatzProcess.content_type;

    angular
        .module(moduleName, [
            AdhDocumentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMappingModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhNamesModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhConfig", "adhProcessProvider", (adhConfig, adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[processType] = "<adh-meinberlin-alexanderplatz-workbench " +
                "data-process-properties=\"processProperties\"></adh-meinberlin-alexanderplatz-workbench>";
            adhProcessProvider.setProperties(processType, {
                createSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/CreateSlot.html",
                detailSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/DetailSlot.html",
                editSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/EditSlot.html",
                hasAuthorInListItem: true,
                hasCommentColumn: true,
                hasDescription: true,
                hasLocation: true,
                itemClass: RIGeoProposal,
                versionClass: RIGeoProposalVersion
            });
        }])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider, adhConfig) => {
            var processHeaderSlot = adhConfig.pkg_path + AdhWorkbench.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType] = processHeaderSlot;
            Workbench.registerRoutes(processType)(adhResourceAreaProvider);
        }])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[RIAlexanderplatzProcess.content_type] = "TR__RESOURCE_ALEXANDERPLATZ";
            adhNamesProvider.names[RIGeoProposalVersion.content_type] = "TR__RESOURCE_PROPOSAL";
        }])
        .directive("adhMeinberlinAlexanderplatzWorkbench", ["adhConfig", "adhTopLevelState", Workbench.workbenchDirective])
        .directive("adhMeinberlinAlexanderplatzProcessColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", "adhHttp", Workbench.processDetailColumnDirective])
        .directive("adhMeinberlinAlexanderplatzDocumentDetailColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", Workbench.documentDetailColumnDirective])
        .directive("adhMeinberlinAlexanderplatzProposalDetailColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", Workbench.proposalDetailColumnDirective])
        .directive("adhMeinberlinAlexanderplatzDocumentCreateColumn", [
            "adhConfig", "adhHttp", "adhTopLevelState", Workbench.documentCreateColumnDirective])
        .directive("adhMeinberlinAlexanderplatzProposalCreateColumn", [
            "adhConfig", "adhTopLevelState", Workbench.proposalCreateColumnDirective])
        .directive("adhMeinberlinAlexanderplatzDocumentEditColumn", [
            "adhConfig", "adhHttp", "adhTopLevelState", Workbench.documentEditColumnDirective])
        .directive("adhMeinberlinAlexanderplatzProposalEditColumn", [
            "adhConfig", "adhTopLevelState", Workbench.proposalEditColumnDirective]);
};
