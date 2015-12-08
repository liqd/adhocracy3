import * as AdhMercator2016Module from "./2016/Module";


export var moduleName = "adhMercator";

export var register = (angular) => {
    AdhMercator2016Module.register(angular);

    angular
        .module(moduleName, [
            AdhMercator2016Module.moduleName
        ]);
};
