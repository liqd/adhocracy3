import Phase = require("./Phase");


export var moduleName = "adhMeinBerlinPhase";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhMeinBerlinPhase", ["adhConfig", Phase.phaseDirective]);
};
