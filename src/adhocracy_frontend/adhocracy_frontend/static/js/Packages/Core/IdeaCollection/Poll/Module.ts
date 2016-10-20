import * as AdhBadgeModule from "../../Badge/Module";
import * as AdhHttpModule from "../../Http/Module";
import * as AdhPermissionsModule from "../../Permissions/Module";
import * as AdhPreliminaryNamesModule from "../../PreliminaryNames/Module";
import * as AdhRateModule from "../../Rate/Module";
import * as AdhTopLevelStateModule from "../../TopLevelState/Module";

import * as Proposal from "./Proposal";


export var moduleName = "adhPoll";

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
        .directive("adhPollDetailColumn", ["adhConfig", "adhTopLevelState", Proposal.pollDetailColumnDirective])
        .directive("adhPollDetail", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", Proposal.detailDirective]);
};
