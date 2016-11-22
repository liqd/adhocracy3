import * as AdhEmbedModule from "../../Core/Embed/Module";
import * as AdhNamesModule from "../../Core/Names/Module";
import * as AdhProcessModule from "../../Core/Process/Module";
import * as AdhResourceAreaModule from "../../Core/ResourceArea/Module";
import * as AdhWorkbenchModule from "../../Core/Workbench/Module";

import * as AdhEmbed from "../../Core/Embed/Embed";
import * as AdhNames from "../../Core/Names/Names";
import * as AdhProcess from "../../Core/Process/Process";
import * as AdhProposal from "../../Core/Proposal/Proposal";
import * as AdhResourceArea from "../../Core/ResourceArea/ResourceArea";
import * as AdhWorkbench from "../../Core/Workbench/Workbench";

import RIKiezkasseProcess from "../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess";
import RIKiezkasseProposal from "../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposal";
import RIKiezkasseProposalVersion from "../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion";
import * as SIKiezkasseProposal from "../../../Resources_/adhocracy_meinberlin/sheets/kiezkassen/IProposal";


export var moduleName = "adhMeinberlinKiezkasse";

export var register = (angular) => {
    var processType = RIKiezkasseProcess.content_type;

    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhNamesModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhWorkbenchModule.moduleName,
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("kiezkasse", ["kiezkassen"]);
        }])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider : AdhResourceArea.Provider, adhConfig) => {
            var registerRoutes = (context? : string) => (provider) => {
                AdhWorkbench.registerCommonRoutesFactory(
                    RIKiezkasseProcess, RIKiezkasseProposal, RIKiezkasseProposalVersion)(context)(provider);
                AdhWorkbench.registerProposalRoutesFactory(
                    RIKiezkasseProcess, RIKiezkasseProposal, RIKiezkasseProposalVersion, true)(context)(provider);
            };
            registerRoutes()(adhResourceAreaProvider);
            registerRoutes("kiezkasse")(adhResourceAreaProvider);

            var processHeaderSlot = adhConfig.pkg_path + AdhWorkbench.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType] = processHeaderSlot;
        }])
        .config(["adhConfig", "adhProcessProvider", (adhConfig, adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[processType] =
                "<adh-workbench data-process-properties=\"processProperties\"></adh-workbench>";
            adhProcessProvider.setProperties(processType, {
                createSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/CreateSlot.html",
                detailSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/DetailSlot.html",
                editSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/EditSlot.html",
                hasAuthorInListItem: true,
                hasCommentColumn: true,
                hasCreatorParticipate: true,
                hasDescription: true,
                hasImage: true,
                hasLocation: true,
                hasLocationText: true,
                itemClass: RIKiezkasseProposal,
                maxBudget: 50000,
                proposalSheet: SIKiezkasseProposal,
                versionClass: RIKiezkasseProposalVersion
            });
        }])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[RIKiezkasseProcess.content_type] = "TR__RESOURCE_KIEZKASSE";
            adhNamesProvider.names[RIKiezkasseProposalVersion.content_type] = "TR__RESOURCE_PROPOSAL";
        }]);
};
