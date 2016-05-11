import * as AdhMeinberlinKiezkasseContextModule from "./Context/Module";


export var moduleName = "adhMeinberlinKiezkasse";

export var register = (angular) => {
    AdhMeinberlinKiezkasseContextModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinKiezkasseContextModule.moduleName,
        ]);
};
