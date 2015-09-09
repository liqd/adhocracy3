import AdhMeinBerlinBurgerhaushaltContextModule = require("./Context/Module");
import AdhMeinBerlinBurgerhaushaltProcessModule = require("./Process/Module");
import AdhMeinBerlinBurgerhaushaltWorkbenchModule = require("./Workbench/Module");


export var moduleName = "adhMeinBerlinBurgerhaushalt";

export var register = (angular) => {
    AdhMeinBerlinBurgerhaushaltContextModule.register(angular);
    AdhMeinBerlinBurgerhaushaltProcessModule.register(angular);
    AdhMeinBerlinBurgerhaushaltWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinBurgerhaushaltContextModule.moduleName,
            AdhMeinBerlinBurgerhaushaltProcessModule.moduleName,
            AdhMeinBerlinBurgerhaushaltWorkbenchModule.moduleName
        ]);
};
