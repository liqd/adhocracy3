import * as AdhEmbedModule from "../../Core/Embed/Module";
import * as AdhResourceAreaModule from "../../Core/ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../Core/TopLevelState/Module";

import * as AdhMeinberlinAlexanderplatzWorkbenchModule from "../Alexanderplatz/Workbench/Module";
import * as AdhWorkbenchModule from "../../Core/Workbench/Module";

import * as AdhEmbed from "../../Core/Embed/Embed";
import * as AdhResourceArea from "../../Core/ResourceArea/ResourceArea";

import * as AdhMeinberlinAlexanderplatzWorkbench from "../Alexanderplatz/Workbench/Workbench";
import * as AdhWorkbench from "../../Core/Workbench/Workbench";

import RIAlexanderplatzProcess from "../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess";
import RIBuergerhaushaltProcess from "../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess";
import RIBuergerhaushaltProposal from "../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProposal";
import RIBuergerhaushaltProposalVersion from "../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProposalVersion";
import RICollaborativeTextProcess from "../../../Resources_/adhocracy_meinberlin/resources/collaborative_text/IProcess";
import RIDocument from "../../../Resources_/adhocracy_core/resources/document/IDocument";
import RIDocumentVersion from "../../../Resources_/adhocracy_core/resources/document/IDocumentVersion";
import RIGeoProposal from "../../../Resources_/adhocracy_core/resources/proposal/IGeoProposal";
import RIGeoProposalVersion from "../../../Resources_/adhocracy_core/resources/proposal/IGeoProposalVersion";
import RIWorkbenchProcess from "../../../Resources_/adhocracy_meinberlin/resources/idea_collection/IProcess";
import RIKiezkasseProcess from "../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess";
import RIKiezkasseProposal from "../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposal";
import RIKiezkasseProposalVersion from "../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion";
import RIPoll from "../../../Resources_/adhocracy_meinberlin/resources/stadtforum/IPoll";
import RIProposalVersion from "../../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";
import RIStadtforumProcess from "../../../Resources_/adhocracy_meinberlin/resources/stadtforum/IProcess";

import * as AdhMeinberlinDe from "./MeinberlinDe";


export var moduleName = "adhMeinberlinDe";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhWorkbenchModule.moduleName,
            AdhMeinberlinAlexanderplatzWorkbenchModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("mein.berlin.de");
            adhEmbedProvider.contextHeaders["mein.berlin.de"] = "<adh-meinberlin-de-header></adh-meinberlin-de-header>";
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            AdhMeinberlinAlexanderplatzWorkbench.registerRoutes(
                RIAlexanderplatzProcess.content_type, "mein.berlin.de")(adhResourceAreaProvider);

            var registerCommonAndProposalRoutes = (processType, itemType, versionType, hasCommentColumn) => {
                AdhWorkbench.registerCommonRoutesFactory(
                    processType, itemType, versionType)("mein.berlin.de")(adhResourceAreaProvider);
                AdhWorkbench.registerProposalRoutesFactory(
                    processType, itemType, versionType, hasCommentColumn)("mein.berlin.de")(adhResourceAreaProvider);
            };

            var registerCommonAndDocumentRoutes = (processType, itemType, versionType) => {
                AdhWorkbench.registerCommonRoutesFactory(
                    processType, itemType, versionType)("mein.berlin.de")(adhResourceAreaProvider);
                AdhWorkbench.registerDocumentRoutesFactory(
                    processType, itemType, versionType)("mein.berlin.de")(adhResourceAreaProvider);
            };

            registerCommonAndProposalRoutes(RIBuergerhaushaltProcess, RIBuergerhaushaltProposal, RIBuergerhaushaltProposalVersion, true);
            registerCommonAndProposalRoutes(RIWorkbenchProcess, RIGeoProposal, RIGeoProposalVersion, true);
            registerCommonAndProposalRoutes(RIKiezkasseProcess, RIKiezkasseProposal, RIKiezkasseProposalVersion, true);
            registerCommonAndProposalRoutes(RIStadtforumProcess, RIPoll, RIProposalVersion, false);
            registerCommonAndDocumentRoutes(RICollaborativeTextProcess, RIDocument, RIDocumentVersion);
        }])
        .directive("adhMeinberlinDeHeader", ["adhConfig", "adhTopLevelState", AdhMeinberlinDe.headerDirective]);
};
