import * as AdhMercator2015Module from "./2015/Module";


export var moduleName = "adhMercator";

export var register = (angular) => {
    AdhMercator2015Module.register(angular);

    angular
        .module(moduleName, [
            AdhMercator2015Module.moduleName
        ]);
};
