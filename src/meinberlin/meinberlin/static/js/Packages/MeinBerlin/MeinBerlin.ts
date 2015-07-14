import AdhMeinBerlinKiezkassen = require("./Kiezkassen/Kiezkassen");
import AdhMeinBerlinBplaene = require("./Bplaene/Bplaene");
import AdhMeinBerlinAlexanderplatz = require("./Alexanderplatz/Alexanderplatz");


export var moduleName = "adhMeinBerlin";

export var register = (angular) => {
    AdhMeinBerlinKiezkassen.register(angular);
    AdhMeinBerlinBplaene.register(angular);
    AdhMeinBerlinAlexanderplatz.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinAlexanderplatz.moduleName,
            AdhMeinBerlinBplaene.moduleName,
            AdhMeinBerlinKiezkassen.moduleName
        ]);
};
