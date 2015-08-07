import AdhMeinBerlinAlexanderplatzWorkbench = require("./Workbench/Workbench");
import AdhMeinBerlinAlexanderplatzContext = require("./Context/Context");


export var moduleName = "adhMeinBerlinAlexanderplatz";

export var register = (angular) => {
	AdhMeinBerlinAlexanderplatzContext.register(angular);
    AdhMeinBerlinAlexanderplatzWorkbench.register(angular);

    angular
        .module(moduleName, [
        	AdhMeinBerlinAlexanderplatzContext.moduleName,
            AdhMeinBerlinAlexanderplatzWorkbench.moduleName
        ]);
};
