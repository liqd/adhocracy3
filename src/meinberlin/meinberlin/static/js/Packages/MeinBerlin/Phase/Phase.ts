import AdhConfig = require("../../Config/Config");

export var pkgLocation = "/MeinBerlin/Phase";


export var phaseDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Phase.html",
        scope: {
            phase: "="
        }
    };
};


export var moduleName = "adhMeinBerlinPhase";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhMeinBerlinPhase", ["adhConfig", phaseDirective]);
};
