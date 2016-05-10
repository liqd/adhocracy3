import * as AdhMeinberlinKiezkasseContextModule from "./Context/Module";
import * as AdhMeinberlinKiezkasseProcessModule from "./Process/Module";


export var moduleName = "adhMeinberlinKiezkasse";

export var register = (angular) => {
    AdhMeinberlinKiezkasseContextModule.register(angular);
    AdhMeinberlinKiezkasseProcessModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinKiezkasseContextModule.moduleName,
            AdhMeinberlinKiezkasseProcessModule.moduleName
        ]);
};
