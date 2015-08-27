import AdhMeinBerlinBurgerhaushaltContext = require("./Context/Context");
import AdhMeinBerlinBurgerhaushaltProcess = require("./Process/Process");
import AdhMeinBerlinBurgerhaushaltWorkbench = require("./Workbench/Workbench");


export var moduleName = "adhMeinBerlinBurgerhaushalt";

export var register = (angular) => {
    AdhMeinBerlinBurgerhaushaltContext.register(angular);
    AdhMeinBerlinBurgerhaushaltProcess.register(angular);
    AdhMeinBerlinBurgerhaushaltWorkbench.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinBurgerhaushaltContext.moduleName,
            AdhMeinBerlinBurgerhaushaltProcess.moduleName,
            AdhMeinBerlinBurgerhaushaltWorkbench.moduleName
        ]);
};
