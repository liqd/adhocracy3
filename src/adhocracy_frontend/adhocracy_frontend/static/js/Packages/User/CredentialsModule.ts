import AdhTrackingModule = require("../Tracking/Module");

import AdhCredentials = require("./Credentials");


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
