import * as AdhMeinberlinBurgerhaushaltContextModule from "./Context/Module";
import * as AdhMeinberlinBurgerhaushaltProcessModule from "./Process/Module";
import * as AdhMeinberlinBurgerhaushaltWorkbenchModule from "./Workbench/Module";


export var moduleName = "adhMeinberlinBurgerhaushalt";

export var register = (angular) => {
    AdhMeinberlinBurgerhaushaltContextModule.register(angular);
    AdhMeinberlinBurgerhaushaltProcessModule.register(angular);
    AdhMeinberlinBurgerhaushaltWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinBurgerhaushaltContextModule.moduleName,
            AdhMeinberlinBurgerhaushaltProcessModule.moduleName,
            AdhMeinberlinBurgerhaushaltWorkbenchModule.moduleName
        ]);
};
