import * as AdhMeinberlinAlexanderplatzWorkbenchModule from "./Workbench/Module";
import * as AdhMeinberlinAlexanderplatzContextModule from "./Context/Module";


export var moduleName = "adhMeinberlinAlexanderplatz";

export var register = (angular) => {
    AdhMeinberlinAlexanderplatzContextModule.register(angular);
    AdhMeinberlinAlexanderplatzWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinAlexanderplatzContextModule.moduleName,
            AdhMeinberlinAlexanderplatzWorkbenchModule.moduleName
        ]);
};
