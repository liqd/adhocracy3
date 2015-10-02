import * as AdhMeinberlinKiezkasseContextModule from "./Context/Module";
import * as AdhMeinberlinKiezkasseProcessModule from "./Process/Module";
import * as AdhMeinberlinKiezkasseWorkbenchModule from "./Workbench/Module";


export var moduleName = "adhMeinberlinKiezkasse";

export var register = (angular) => {
    AdhMeinberlinKiezkasseContextModule.register(angular);
    AdhMeinberlinKiezkasseProcessModule.register(angular);
    AdhMeinberlinKiezkasseWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinKiezkasseContextModule.moduleName,
            AdhMeinberlinKiezkasseProcessModule.moduleName,
            AdhMeinberlinKiezkasseWorkbenchModule.moduleName
        ]);
};
