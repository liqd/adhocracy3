import * as AdhAngularHelpersModule from "../../../AngularHelpers/Module";
import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhHttpModule from "../../../Http/Module";
import * as AdhPreliminaryNamesModule from "../../../PreliminaryNames/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";

import * as AdhEmbed from "../../../Embed/Embed";

import * as Proposal from "./Proposal";


export var moduleName = "adhMeinBplaeneProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpersModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-bplaene-proposal-embed");
        }])
        .directive("adhMeinBerlinBplaeneProposalCreate", [
            "adhConfig", "adhHttp", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", Proposal.createDirective])
        .directive("adhMeinBerlinBplaeneProposalEmbed", ["adhConfig", "adhHttp", Proposal.embedDirective]);
};
