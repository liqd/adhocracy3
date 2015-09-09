import AdhAngularHelpersModule = require("../AngularHelpers/Module");
import AdhBadgeModule = require("../Badge/Module");
import AdhEmbedModule = require("../Embed/Module");
import AdhHttpModule = require("../Http/Module");
import AdhMappingModule = require("../Mapping/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");
import AdhRateModule = require("../Rate/Module");
import AdhResourceAreaModule = require("../ResourceArea/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");

import AdhEmbed = require("../Embed/Embed");

import Proposal = require("./Proposal");


export var moduleName = "adhMeinBerlinProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpersModule.moduleName,
            AdhBadgeModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMappingModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhRateModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-detail");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-list-item");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-create");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-edit");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-list");
        }])
        .directive("adhMeinBerlinProposalDetail", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.detailDirective])
        .directive("adhMeinBerlinProposalListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.listItemDirective])
        .directive("adhMeinBerlinProposalMapListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.mapListItemDirective])
        .directive("adhMeinBerlinProposalCreate", [
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhShowError",
            "adhSubmitIfValid",
            "adhResourceUrlFilter",
            "$location",
            Proposal.createDirective
        ])
        .directive("adhMeinBerlinProposalEdit", [
            "adhConfig",
            "adhHttp",
            "adhPermissions",
            "adhPreliminaryNames",
            "adhRate",
            "adhResourceUrlFilter",
            "adhShowError",
            "adhSubmitIfValid",
            "adhTopLevelState",
            "adhGetBadges",
            "$location",
            "$q",
            Proposal.editDirective
        ]);
};
