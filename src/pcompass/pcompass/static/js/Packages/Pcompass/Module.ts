import * as AdhPcompassContextModule from "./Context/Module";
import * as AdhPcompassWorkbenchModule from "./Workbench/Module";


export var moduleName = "adhPcompass";

export var register = (angular) => {
    AdhPcompassContextModule.register(angular);
    AdhPcompassWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhPcompassContextModule.moduleName
        ]);
};
