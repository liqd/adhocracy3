import AdhMeinBerlinBurgerhaushaltWorkbench = require("./Workbench/Workbench");


export var moduleName = "adhMeinBerlinBurgerhaushalt";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhMeinBerlinBurgerhaushaltWorkbench.moduleName
        ]);
};
