import AdhMeinBerlinAlexanderplatzWorkbench = require("./Workbench/Workbench");


export var moduleName = "adhMeinBerlinAlexanderplatz";

export var register = (angular) => {
    AdhMeinBerlinAlexanderplatzWorkbench.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinAlexanderplatzWorkbench.moduleName
        ]);
};
