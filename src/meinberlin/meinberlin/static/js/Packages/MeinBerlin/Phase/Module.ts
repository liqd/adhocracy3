import * as Phase from "./Phase";


export var moduleName = "adhMeinBerlinPhase";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhMeinBerlinPhase", ["adhConfig", Phase.phaseDirective]);
};
