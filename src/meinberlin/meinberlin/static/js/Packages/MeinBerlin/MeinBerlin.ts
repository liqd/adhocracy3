import AdhMeinBerlinKiezkassen = require("./Kiezkassen/Kiezkassen");
import AdhMeinBerlinBplaene = require("./Bplaene/Bplaene");
import AdhMeinBerlinAlexanderplatz = require("./Alexanderplatz/Alexanderplatz");
import AdhMeinBerlinBuergerhaushalt = require("./Buergerhaushalt/Buergerhaushalt");


export var moduleName = "adhMeinBerlin";

export var register = (angular) => {
    AdhMeinBerlinKiezkassen.register(angular);
    AdhMeinBerlinBplaene.register(angular);
    AdhMeinBerlinAlexanderplatz.register(angular);
    AdhMeinBerlinBuergerhaushalt.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinAlexanderplatz.moduleName,
            AdhMeinBerlinBplaene.moduleName,
            AdhMeinBerlinKiezkassen.moduleName,
            AdhMeinBerlinBuergerhaushalt.moduleName
        ]);
};
