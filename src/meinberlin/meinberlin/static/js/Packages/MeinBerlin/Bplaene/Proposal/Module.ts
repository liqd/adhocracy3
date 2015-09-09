import AdhAngularHelpersModule = require("../../../AngularHelpers/Module");
import AdhEmbedModule = require("../../../Embed/Module");
import AdhHttpModule = require("../../../Http/Module");
import AdhPreliminaryNamesModule = require("../../../PreliminaryNames/Module");
import AdhResourceAreaModule = require("../../../ResourceArea/Module");

import AdhEmbed = require("../../../Embed/Embed");

import Proposal = require("./Proposal");


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
