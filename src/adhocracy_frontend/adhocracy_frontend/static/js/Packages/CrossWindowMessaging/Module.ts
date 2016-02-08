import * as AdhCredentialsModule from "../User/Module";
import * as AdhUserModule from "../User/Module";

import * as AdhCrossWindowMessaging from "./CrossWindowMessaging";


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
