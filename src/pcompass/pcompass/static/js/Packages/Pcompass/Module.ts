import * as AdhEmbedModule from "../Core/Embed/Module";
import * as AdhIdeaCollectionModule from "../Core/IdeaCollection/Module";
import * as AdhProcessModule from "../Core/Process/Module";
import * as AdhResourceAreaModule from "../Core/ResourceArea/Module";

import * as AdhEmbed from "../Core/Embed/Embed";
import * as AdhIdeaCollectionWorkbench from "../Core/IdeaCollection/Workbench/Workbench";
import * as AdhProcess from "../Core/Process/Process";
import * as AdhResourceArea from "../Core/ResourceArea/ResourceArea";

import RIPcompassProcess from "../../Resources_/adhocracy_pcompass/resources/request/IProcess";
import RIProposal from "../../Resources_/adhocracy_core/resources/proposal/IProposal";
import RIProposalVersion from "../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";


export var moduleName = "adhPcompass";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhIdeaCollectionModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("pcompass");
        }])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider : AdhResourceArea.Provider, adhConfig) => {
            var processHeaderSlot = adhConfig.pkg_path + AdhIdeaCollectionWorkbench.pkgLocation + "/ProcessHeaderSlot.html";
            var registerRoutes = AdhIdeaCollectionWorkbench.registerRoutesFactory(RIPcompassProcess, RIProposal, RIProposalVersion, true);
            registerRoutes()(adhResourceAreaProvider);
            registerRoutes("pcompass")(adhResourceAreaProvider);
            adhResourceAreaProvider.processHeaderSlots[RIPcompassProcess.content_type] = processHeaderSlot;
        }])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[RIPcompassProcess.content_type] =
                "<adh-idea-collection-workbench data-process-properties=\"processProperties\"></adh-idea-collection-workbench>";
            adhProcessProvider.processProperties[RIPcompassProcess.content_type] = {
                hasCommmentColumn: true,
                hasDescription: true,
                proposalClass: RIProposal,
                proposalVersionClass: RIProposalVersion
            };
        }]);
};
