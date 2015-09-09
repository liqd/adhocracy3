import AdhEventManagerModule = require("../EventManager/Module");
import AdhHttpModule = require("../Http/Module");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");

import AdhResourceWidgets = require("./ResourceWidgets");


export var moduleName = "adhResourceWidgets";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEventManagerModule.moduleName,
            AdhHttpModule.moduleName,
            AdhPreliminaryNamesModule.moduleName
        ])
        .directive("adhResourceWrapper", AdhResourceWidgets.resourceWrapper);
};
