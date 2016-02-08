import * as AdhTracking from "./Tracking";


export var moduleName = "adhTracking";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .service("adhTracking", ["$q", "$window", "adhConfig", AdhTracking.Service]);
};
