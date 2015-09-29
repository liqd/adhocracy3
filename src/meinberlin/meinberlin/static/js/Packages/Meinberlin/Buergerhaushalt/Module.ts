import * as AdhMeinberlinBuergerhaushaltContextModule from "./Context/Module";
import * as AdhMeinberlinBuergerhaushaltProcessModule from "./Process/Module";
import * as AdhMeinberlinBuergerhaushaltWorkbenchModule from "./Workbench/Module";


export var moduleName = "adhMeinberlinBuergerhaushalt";

export var register = (angular) => {
    AdhMeinberlinBuergerhaushaltContextModule.register(angular);
    AdhMeinberlinBuergerhaushaltProcessModule.register(angular);
    AdhMeinberlinBuergerhaushaltWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinBuergerhaushaltContextModule.moduleName,
            AdhMeinberlinBuergerhaushaltProcessModule.moduleName,
            AdhMeinberlinBuergerhaushaltWorkbenchModule.moduleName
        ]);
};
