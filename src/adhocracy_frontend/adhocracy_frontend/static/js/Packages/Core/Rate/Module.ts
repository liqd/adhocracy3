import * as AdhAngularHelpersModule from "../AngularHelpers/Module";
import * as AdhCredentialsModule from "../User/Module";
import * as AdhEventManagerModule from "../EventManager/Module";
import * as AdhHttpModule from "../Http/Module";
import * as AdhPermissionsModule from "../Permissions/Module";
import * as AdhPreliminaryNamesModule from "../PreliminaryNames/Module";
import * as AdhResourceAreaModule from "../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";
import * as AdhUserModule from "../User/Module";
import * as AdhWebSocketModule from "../WebSocket/Module";

import * as AdhRate from "./Rate";

import * as SILikeable from "../../../Resources_/adhocracy_core/sheets/rate/ILikeable";
import * as SIRateable from "../../../Resources_/adhocracy_core/sheets/rate/IRateable";


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
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName,
            AdhUserModule.moduleName,
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
            "adhResourceArea",
            "adhUser",
            "adhDone",
            AdhRate.directiveFactory("/Rate.html", SIRateable.nick)])
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
            "adhResourceArea",
            "adhUser",
            "adhDone",
            AdhRate.directiveFactory("/Like.html", SILikeable.nick)])
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
            "adhResourceArea",
            "adhUser",
            "adhDone",
            AdhRate.directiveFactory("/Opinion.html", SIRateable.nick)]);
};
