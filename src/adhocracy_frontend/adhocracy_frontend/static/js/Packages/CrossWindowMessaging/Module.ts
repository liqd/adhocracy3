import AdhCredentialsModule = require("../User/Module");
import AdhUserModule = require("../User/Module");

import AdhCrossWindowMessaging = require("./CrossWindowMessaging");


export var moduleName = "adhCrossWindowMessaging";

export var register = (angular, trusted = false) => {
    var mod = angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhUserModule.moduleName
        ]);

    if (trusted) {
        mod.factory("adhCrossWindowMessaging", [
            "adhConfig", "$location", "$window", "$rootScope", "adhCredentials", "adhUser", AdhCrossWindowMessaging.factory]);
    } else {
        mod.factory("adhCrossWindowMessaging", ["adhConfig", "$location", "$window", "$rootScope", AdhCrossWindowMessaging.factory]);
    }
};
