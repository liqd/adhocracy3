import * as AdhInject from "./Inject";


export var moduleName = "adhInject";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhInject", AdhInject.factory);
};
