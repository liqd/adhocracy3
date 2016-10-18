import * as AdhAngularHelpersModule from "../../Core/AngularHelpers/Module";
import * as AdhAnonymizeModule from "../../Core/Anonymize/Module";
import * as AdhBadgeModule from "../../Core/Badge/Module";
import * as AdhHttpModule from "../../Core/Http/Module";
import * as AdhNamesModule from "../../Core/Names/Module";
import * as AdhPermissionsModule from "../../Core/Permissions/Module";
import * as AdhPreliminaryNamesModule from "../../Core/PreliminaryNames/Module";
import * as AdhRateModule from "../../Core/Rate/Module";
import * as AdhResourceAreaModule from "../../Core/ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../Core/TopLevelState/Module";

import * as AdhNames from "../../Core/Names/Names";

import * as Proposal from "./Proposal";

import RIProposalVersion from "../../../Resources_/adhocracy_s1/resources/s1/IProposalVersion";

export var moduleName = "adhS1Proposal";

export var register = (angular) => {
    angular.module(moduleName, [
        AdhAngularHelpersModule.moduleName,
        AdhAnonymizeModule.moduleName,
        AdhBadgeModule.moduleName,
        AdhHttpModule.moduleName,
        AdhNamesModule.moduleName,
        AdhPermissionsModule.moduleName,
        AdhPreliminaryNamesModule.moduleName,
        AdhRateModule.moduleName,
        AdhResourceAreaModule.moduleName,
        AdhTopLevelStateModule.moduleName
    ])
    .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
        adhNamesProvider.names[RIProposalVersion.content_type] = "TR__RESOURCE_PROPOSAL";
    }])
    .directive("adhS1ProposalDetail", [
        "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.detailDirective])
    .directive("adhS1ProposalListItem", [
        "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.listItemDirective])
    .directive("adhS1ProposalCreate", [
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
    .directive("adhS1ProposalEdit", [
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
    ])
    .directive("adhS1ProposalListing", ["adhConfig", "adhTopLevelState", Proposal.listingDirective])
    .directive("adhS1RenominateProposal", ["adhConfig", "adhHttp", "$q", "$translate", "$window", Proposal.renominateProposalDirective]);
};
