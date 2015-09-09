import * as AdhMeinBerlinAlexanderplatzWorkbenchModule from "./Workbench/Module";
import * as AdhMeinBerlinAlexanderplatzContextModule from "./Context/Module";
import * as AdhMeinBerlinAlexanderplatzProcessModule from "./Process/Module";


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
