import AdhAngularHelpersModule = require("../AngularHelpers/Module");
import AdhCredentialsModule = require("../User/Module");
import AdhEventManagerModule = require("../EventManager/Module");
import AdhHttpModule = require("../Http/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");
import AdhWebSocketModule = require("../WebSocket/Module");

import AdhRate = require("./Rate");
import Adapter = require("./Adapter");


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
            AdhRate.directiveFactory("/Like.html", new Adapter.LikeAdapter())]);
};
