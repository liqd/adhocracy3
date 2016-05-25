import * as AdhBadgeModule from "../../Badge/Module";
import * as AdhHttpModule from "../../Http/Module";
import * as AdhPermissionsModule from "../../Permissions/Module";
import * as AdhPreliminaryNamesModule from "../../PreliminaryNames/Module";
import * as AdhRateModule from "../../Rate/Module";
import * as AdhTopLevelStateModule from "../../TopLevelState/Module";

import * as Proposal from "./Proposal";


export var moduleName = "AdhPcompassProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhBadgeModule.moduleName,
            AdhHttpModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhRateModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhPcompassProposalDetail", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.detailDirective])
        .directive("adhPcompassProposalListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.listItemDirective])
        .directive("adhPcompassProposalCreate", [
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
        .directive("adhPcompassProposalEdit", [
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
