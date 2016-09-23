import * as AdhTrackingModule from "../Tracking/Module";

import * as AdhCredentials from "./Credentials";


export var moduleName = "adhCredentials";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTrackingModule.moduleName
        ])
        .service("adhCredentials", [
            "adhConfig",
            "adhCache",
            "adhTracking",
            "modernizr",
            "angular",
            "$q",
            "$http",
            "$timeout",
            "$rootScope",
            "$window",
            AdhCredentials.Service]);
};
