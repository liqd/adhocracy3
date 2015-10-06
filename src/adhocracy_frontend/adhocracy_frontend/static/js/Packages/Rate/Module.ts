import * as AdhAngularHelpersModule from "../AngularHelpers/Module";
import * as AdhCredentialsModule from "../User/Module";
import * as AdhEventManagerModule from "../EventManager/Module";
import * as AdhHttpModule from "../Http/Module";
import * as AdhPermissionsModule from "../Permissions/Module";
import * as AdhPreliminaryNamesModule from "../PreliminaryNames/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";
import * as AdhWebSocketModule from "../WebSocket/Module";

import * as AdhRate from "./Rate";
import * as Adapter from "./Adapter";


export var moduleName = "adhRate";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpersModule.moduleName,
            AdhCredentialsModule.moduleName,
            AdhEventManagerModule.moduleName,
            AdhHttpModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhTopLevelStateModule.moduleName,
            AdhWebSocketModule.moduleName
        ])
        .service("adhRateEventManager", ["adhEventManagerClass", (cls) => new cls()])
        .service("adhRate", ["$q", "adhHttp", AdhRate.Service])
        .directive("adhRate", [
            "$q",
            "adhRate",
            "adhRateEventManager",
            "adhConfig",
            "adhHttp",
            "adhWebSocket",
            "adhPermissions",
            "adhCredentials",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhDone",
            AdhRate.directiveFactory("/Rate.html", new Adapter.RateAdapter())])
        .directive("adhLike", [
            "$q",
            "adhRate",
            "adhRateEventManager",
            "adhConfig",
            "adhHttp",
            "adhWebSocket",
            "adhPermissions",
            "adhCredentials",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhDone",
            AdhRate.directiveFactory("/Like.html", new Adapter.LikeAdapter())])
        .directive("adhOpinion", [
            "$q",
            "adhRate",
            "adhRateEventManager",
            "adhConfig",
            "adhHttp",
            "adhWebSocket",
            "adhPermissions",
            "adhCredentials",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhDone",
            AdhRate.directiveFactory("/Opinion.html", new Adapter.RateAdapter())]);
};
