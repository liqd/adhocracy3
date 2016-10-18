import * as AdhPreliminaryNames from "./PreliminaryNames";


export var moduleName = "adhPreliminaryNames";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .service("adhPreliminaryNames", AdhPreliminaryNames.Service);
};
