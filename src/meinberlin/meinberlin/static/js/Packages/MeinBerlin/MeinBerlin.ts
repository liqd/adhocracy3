import AdhMeinBerlinKiezkassen = require("./Kiezkassen/Kiezkassen");
import AdhMeinBerlinWorkbench = require("./Workbench/Workbench");


export var moduleName = "adhMeinBerlin";

export var register = (angular) => {
    AdhMeinBerlinKiezkassen.register(angular);
    AdhMeinBerlinWorkbench.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinKiezkassen.moduleName,
            AdhMeinBerlinWorkbench.moduleName
        ]);
};
