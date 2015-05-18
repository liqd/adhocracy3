import AdhMeinBerlinKiezkassen = require("./Kiezkassen/Kiezkassen");
import AdhMeinBerlinBplaene = require("./Bplaene/Bplaene");


export var moduleName = "adhMeinBerlin";

export var register = (angular) => {
    AdhMeinBerlinKiezkassen.register(angular);
    AdhMeinBerlinBplaene.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinKiezkassen.moduleName,
            AdhMeinBerlinBplaene.moduleName
        ]);
};
