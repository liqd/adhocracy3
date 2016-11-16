import * as AdhIdeaCollectionModule from "../../Core/IdeaCollection/Module";
import * as AdhNamesModule from "../../Core/Names/Module";
import * as AdhProcessModule from "../../Core/Process/Module";
import * as AdhResourceAreaModule from "../../Core/ResourceArea/Module";

import * as AdhEmbed from "../../Core/Embed/Embed";
import * as AdhNames from "../../Core/Names/Names";
import * as AdhPoll from "../../Core/IdeaCollection/Poll/Poll";
import * as AdhProcess from "../../Core/Process/Process";
import * as AdhProposal from "../../Core/Proposal/Proposal";
import * as AdhResourceArea from "../../Core/ResourceArea/ResourceArea";
import * as AdhWorkbench from "../../Core/Workbench/Workbench";

import RIPoll from "../../../Resources_/adhocracy_meinberlin/resources/stadtforum/IPoll";
import RIProposalVersion from "../../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";
import RIStadtforumProcess from "../../../Resources_/adhocracy_meinberlin/resources/stadtforum/IProcess";

export var moduleName = "adhMeinberlinStadtforum";

export var register = (angular) => {
    var processType = RIStadtforumProcess.content_type;

    angular
        .module(moduleName, [
            AdhIdeaCollectionModule.moduleName,
            AdhNamesModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider
                .registerDirective("meinberlin-stadtforum-proposal-detail");
        }])
        .directive("adhMeinberlinStadtforumProposalDetail", [
            "adhConfig",
            "adhHttp",
            "adhPermissions",
            "adhProcess",
            "adhRate",
            "adhTopLevelState",
            "adhGetBadges",
            "$q",
            AdhPoll.detailDirective(processType)])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider : AdhResourceArea.Provider, adhConfig) => {
            var registerRoutes = (context? : string) => (provider) => {
                AdhWorkbench.registerCommonRoutesFactory(
                    RIStadtforumProcess, RIPoll, RIProposalVersion)(context)(provider);
                AdhWorkbench.registerProposalRoutesFactory(
                    RIStadtforumProcess, RIPoll, RIProposalVersion, false)(context)(provider);
            };
            registerRoutes()(adhResourceAreaProvider);

            var processHeaderSlot = adhConfig.pkg_path + AdhWorkbench.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType] = processHeaderSlot;
        }])
        .config(["adhProcessProvider", "adhConfig", (adhProcessProvider : AdhProcess.Provider, adhConfig) => {
            adhProcessProvider.templates[processType] =
                "<adh-idea-collection-workbench data-process-properties=\"processProperties\">" +
                "</adh-idea-collection-workbench>";
            adhProcessProvider.setProperties(processType, {
                createSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/CreateSlot.html",
                detailSlot: adhConfig.pkg_path + AdhPoll.pkgLocation + "/DetailSlot.html",
                editSlot: adhConfig.pkg_path + AdhProposal.pkgLocation + "/EditSlot.html",
                itemClass: RIPoll,
                versionClass: RIProposalVersion
            });
        }])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[processType] = "TR__RESOURCE_STADTFORUM";
            adhNamesProvider.names[RIProposalVersion.content_type] = "TR__RESOURCE_POLL";
        }]);
};
