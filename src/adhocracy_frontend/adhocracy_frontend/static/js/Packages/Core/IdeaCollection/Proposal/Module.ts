import * as AdhAngularHelpersModule from "../../AngularHelpers/Module";
import * as AdhAnonymizeModule from "../../Anonymize/Module";
import * as AdhBadgeModule from "../../Badge/Module";
import * as AdhHttpModule from "../../Http/Module";
import * as AdhMappingModule from "../../Mapping/Module";
import * as AdhPermissionsModule from "../../Permissions/Module";
import * as AdhPreliminaryNamesModule from "../../PreliminaryNames/Module";
import * as AdhRateModule from "../../Rate/Module";
import * as AdhResourceAreaModule from "../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../TopLevelState/Module";

import * as Proposal from "./Proposal";

import RIProposal from "../../../../Resources_/adhocracy_core/resources/proposal/IProposal";
import RIProposalVersion from "../../../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";

export var moduleName = "adhIdeaCollectionProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpersModule.moduleName,
            AdhAnonymizeModule.moduleName,
            AdhBadgeModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMappingModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhRateModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider) => {
                adhResourceAreaProvider.names[RIProposal.content_type] = "TR__PROPOSALS";
                adhResourceAreaProvider.names[RIProposalVersion.content_type] = "TR__PROPOSALS";
            }])
        .directive("adhIdeaCollectionProposalDetail", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.detailDirective])
        .directive("adhIdeaCollectionProposalListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.listItemDirective])
        .directive("adhIdeaCollectionProposalMapListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.mapListItemDirective])
        .directive("adhIdeaCollectionProposalCreate", [
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
        .directive("adhIdeaCollectionProposalEdit", [
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
