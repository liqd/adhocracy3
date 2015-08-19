import AdhMeinBerlinBurgerhaushaltProcess = require("./Process/Process");
import AdhMeinBerlinBurgerhaushaltWorkbench = require("./Workbench/Workbench");


export var moduleName = "adhMeinBerlinBurgerhaushalt";

export var register = (angular) => {
    AdhMeinBerlinBurgerhaushaltProcess.register(angular);
    AdhMeinBerlinBurgerhaushaltWorkbench.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinBurgerhaushaltProcess.moduleName,
            AdhMeinBerlinBurgerhaushaltWorkbench.moduleName
        ]);
};
