import * as Phase from "./Phase";


export var moduleName = "adhMeinberlinPhase";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhMeinberlinPhase", ["adhConfig", Phase.phaseDirective]);
};
