import * as AdhMeinBerlinKiezkassenContextModule from "./Context/Module";
import * as AdhMeinBerlinKiezkassenProcessModule from "./Process/Module";
import * as AdhMeinBerlinKiezkassenWorkbenchModule from "./Workbench/Module";


export var moduleName = "adhMeinBerlinKiezkassen";

export var register = (angular) => {
    AdhMeinBerlinKiezkassenContextModule.register(angular);
    AdhMeinBerlinKiezkassenProcessModule.register(angular);
    AdhMeinBerlinKiezkassenWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinKiezkassenContextModule.moduleName,
            AdhMeinBerlinKiezkassenProcessModule.moduleName,
            AdhMeinBerlinKiezkassenWorkbenchModule.moduleName
        ]);
};
