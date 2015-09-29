import * as AdhMeinberlinKiezkassenContextModule from "./Context/Module";
import * as AdhMeinberlinKiezkassenProcessModule from "./Process/Module";
import * as AdhMeinberlinKiezkassenWorkbenchModule from "./Workbench/Module";


export var moduleName = "adhMeinberlinKiezkassen";

export var register = (angular) => {
    AdhMeinberlinKiezkassenContextModule.register(angular);
    AdhMeinberlinKiezkassenProcessModule.register(angular);
    AdhMeinberlinKiezkassenWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinKiezkassenContextModule.moduleName,
            AdhMeinberlinKiezkassenProcessModule.moduleName,
            AdhMeinberlinKiezkassenWorkbenchModule.moduleName
        ]);
};
