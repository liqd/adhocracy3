import * as AdhPcompassWorkbenchModule from "./Workbench/Module";


export var moduleName = "adhPcompass";

export var register = (angular) => {
    AdhPcompassWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhPcompassWorkbenchModule.moduleName
        ]);
};
