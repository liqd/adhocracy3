import * as AdhNamesModule from "../../Core/Names/Module";
import * as AdhProcessModule from "../../Core/Process/Module";
import * as AdhProposalModule from "../../Core/Proposal/Module";
import * as AdhResourceAreaModule from "../../Core/ResourceArea/Module";
import * as AdhWorkbenchModule from "../../Core/Workbench/Module";

import * as AdhNames from "../../Core/Names/Names";
import * as AdhProcess from "../../Core/Process/Process";
import * as AdhProposal from "../../Core/Proposal/Proposal";
import * as AdhResourceArea from "../../Core/ResourceArea/ResourceArea";
import * as AdhWorkbench from "../../Core/Workbench/Workbench";

import RIGeoProposal from "../../../Resources_/adhocracy_core/resources/proposal/IGeoProposal";
import RIGeoProposalVersion from "../../../Resources_/adhocracy_core/resources/proposal/IGeoProposalVersion";
import RIWorkbenchProcess from "../../../Resources_/adhocracy_meinberlin/resources/idea_collection/IProcess";


export var moduleName = "adhMeinberlinWorkbench";

export var register = (angular) => {
    var processType = RIWorkbenchProcess.content_type;

    angular
        .module(moduleName, [
            AdhNamesModule.moduleName,
            AdhProcessModule.moduleName,
            AdhProposalModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhWorkbenchModule.moduleName,
        ])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider: AdhResourceArea.Provider, adhConfig) => {
            AdhWorkbench.registerCommonRoutesFactory(
                RIWorkbenchProcess, RIGeoProposal, RIGeoProposalVersion)()(adhResourceAreaProvider);
            AdhWorkbench.registerProposalRoutesFactory(
                RIWorkbenchProcess, RIGeoProposal, RIGeoProposalVersion, true)()(adhResourceAreaProvider);

            var processHeaderSlot = adhConfig.pkg_path + AdhWorkbench.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType] = processHeaderSlot;
        }])
        .config(["adhConfig", "adhProcessProvider", (adhConfig, adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[processType] =
                "<adh-idea-collection-workbench data-process-properties=\"processProperties\">" +
                "</adh-idea-collection-workbench>";
            adhProcessProvider.setProperties(processType, {
                createSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/CreateSlot.html",
                detailSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/DetailSlot.html",
                editSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/EditSlot.html",
                hasAuthorInListItem: true,
                hasCommentColumn: true,
                hasDescription: true,
                hasImage: true,
                hasLocation: true,
                itemClass: RIGeoProposal,
                versionClass: RIGeoProposalVersion
            });
        }])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[RIWorkbenchProcess.content_type] = "TR__RESOURCE_IDEA_COLLECTION";
            adhNamesProvider.names[RIGeoProposalVersion.content_type] = "TR__RESOURCE_PROPOSAL";
        }]);
};
