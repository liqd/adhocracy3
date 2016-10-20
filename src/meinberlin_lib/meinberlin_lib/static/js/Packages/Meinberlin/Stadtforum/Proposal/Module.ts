import * as AdhBadgeModule from "../../../Core/Badge/Module";
import * as AdhHttpModule from "../../../Core/Http/Module";
import * as AdhPermissionsModule from "../../../Core/Permissions/Module";
import * as AdhPreliminaryNamesModule from "../../../Core/PreliminaryNames/Module";
import * as AdhRateModule from "../../../Core/Rate/Module";
import * as AdhTopLevelStateModule from "../../../Core/TopLevelState/Module";

import * as Proposal from "./Proposal";


export var moduleName = "adhMeinBerlinStadtforumProposal";

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
        .directive("adhMeinberlinStadtforumProposalEdit", [
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
        .directive("adhMeinberlinStadtforumProposalListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.listItemDirective]);
};
