import * as AdhMeinBerlinBurgerhaushaltContextModule from "./Context/Module";
import * as AdhMeinBerlinBurgerhaushaltProcessModule from "./Process/Module";
import * as AdhMeinBerlinBurgerhaushaltWorkbenchModule from "./Workbench/Module";


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
