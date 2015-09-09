import AdhMeinBerlinKiezkassenContextModule = require("./Context/Module");
import AdhMeinBerlinKiezkassenProcessModule = require("./Process/Module");
import AdhMeinBerlinKiezkassenWorkbenchModule = require("./Workbench/Module");


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
