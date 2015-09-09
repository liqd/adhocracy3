import AdhCredentialsModule = require("../User/CredentialsModule");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");
import AdhWebSocketModule = require("../WebSocket/Module");

import AdhCache = require("./Cache");
import AdhError = require("./Error");
import AdhHttp = require("./Http");
import AdhMetaApi = require("./MetaApi");


export var moduleName = "adhHttp";

export var register = (angular, config, metaApi) => {
    angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhWebSocketModule.moduleName,
            "angular-cache",
        ])
        .config(["$httpProvider", ($httpProvider) => {
            $httpProvider.interceptors.push(["adhHttpBusy", (adhHttpBusy : AdhHttp.Busy) => adhHttpBusy.createInterceptor()]);
        }])
        .service("adhHttpBusy", ["$q", AdhHttp.Busy])
        .directive("adhHttpBusy", ["adhConfig", "adhHttpBusy", AdhHttp.busyDirective])
        .service("adhHttp", [
            "$http", "$q", "$timeout", "adhCredentials", "adhMetaApi", "adhPreliminaryNames", "adhConfig", "adhCache", AdhHttp.Service])
        .service("adhCache", ["$q", "adhConfig", "adhWebSocket", "CacheFactory", AdhCache.Service])
        .factory("adhMetaApi", () => new AdhMetaApi.MetaApiQuery(metaApi))
        .filter("adhFormatError", () => AdhError.formatError);
};
