import * as AdhBadgeModule from "../../Badge/Module";
import * as AdhHttpModule from "../../Http/Module";
import * as AdhPermissionsModule from "../../Permissions/Module";
import * as AdhPreliminaryNamesModule from "../../PreliminaryNames/Module";
import * as AdhProcessModule from "../../Process/Module";
import * as AdhRateModule from "../../Rate/Module";
import * as AdhTopLevelStateModule from "../../TopLevelState/Module";

import * as Poll from "./Poll";


export var moduleName = "adhPoll";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhBadgeModule.moduleName,
            AdhHttpModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhRateModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhPollDetailColumn", ["adhConfig", "adhTopLevelState", Poll.pollDetailColumnDirective])
        .directive("adhPollDetail", [
            "adhConfig",
            "adhHttp",
            "adhPermissions",
            "adhProcess",
            "adhRate",
            "adhTopLevelState",
            "adhGetBadges",
            "$q",
            Poll.detailDirective()]);
};
