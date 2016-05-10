import * as AdhMeinberlinBuergerhaushaltContextModule from "./Context/Module";


export var moduleName = "adhMeinberlinBuergerhaushalt";

export var register = (angular) => {
    AdhMeinberlinBuergerhaushaltContextModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinBuergerhaushaltContextModule.moduleName
        ]);
};
