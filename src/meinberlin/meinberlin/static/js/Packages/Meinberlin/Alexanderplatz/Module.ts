import * as AdhMeinberlinAlexanderplatzWorkbenchModule from "./Workbench/Module";
import * as AdhMeinberlinAlexanderplatzContextModule from "./Context/Module";
import * as AdhMeinberlinAlexanderplatzProcessModule from "./Process/Module";


export var moduleName = "adhMeinberlinAlexanderplatz";

export var register = (angular) => {
    AdhMeinberlinAlexanderplatzContextModule.register(angular);
    AdhMeinberlinAlexanderplatzProcessModule.register(angular);
    AdhMeinberlinAlexanderplatzWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinAlexanderplatzContextModule.moduleName,
            AdhMeinberlinAlexanderplatzProcessModule.moduleName,
            AdhMeinberlinAlexanderplatzWorkbenchModule.moduleName
        ]);
};
