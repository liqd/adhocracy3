import AdhMeinBerlinKiezkassen = require("./Kiezkassen/Kiezkassen");


export var moduleName = "adhMeinBerlin";

export var register = (angular) => {
    AdhMeinBerlinKiezkassen.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinKiezkassen.moduleName
        ]);
};
