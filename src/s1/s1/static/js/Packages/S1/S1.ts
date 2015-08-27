import AdhS1Workbench = require("./Workbench/Workbench");


export var moduleName = "adhS1";

export var register = (angular) => {
    AdhS1Workbench.register(angular);

    angular
        .module(moduleName, [
            AdhS1Workbench.moduleName
        ]);
};
