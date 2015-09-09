import AdhMeinBerlinAlexanderplatzWorkbenchModule = require("./Workbench/Module");
import AdhMeinBerlinAlexanderplatzContextModule = require("./Context/Module");
import AdhMeinBerlinAlexanderplatzProcessModule = require("./Process/Module");


export var moduleName = "adhMeinBerlinAlexanderplatz";

export var register = (angular) => {
    AdhMeinBerlinAlexanderplatzContextModule.register(angular);
    AdhMeinBerlinAlexanderplatzProcessModule.register(angular);
    AdhMeinBerlinAlexanderplatzWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinAlexanderplatzContextModule.moduleName,
            AdhMeinBerlinAlexanderplatzProcessModule.moduleName,
            AdhMeinBerlinAlexanderplatzWorkbenchModule.moduleName
        ]);
};
