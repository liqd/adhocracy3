import AdhMeinBerlinKiezkassen = require("./Kiezkassen/Kiezkassen");
import AdhMeinBerlinBplaene = require("./Bplaene/Bplaene");
import AdhMeinBerlinAlexanderplatz = require("./Alexanderplatz/Alexanderplatz");
import AdhMeinBerlinBurgerhaushalt = require("./Burgerhaushalt/Burgerhaushalt");
import AdhMeinBerlinPhase = require("./Phase/Phase");


export var moduleName = "adhMeinBerlin";

export var register = (angular) => {
    AdhMeinBerlinKiezkassen.register(angular);
    AdhMeinBerlinBplaene.register(angular);
    AdhMeinBerlinAlexanderplatz.register(angular);
    AdhMeinBerlinBurgerhaushalt.register(angular);
    AdhMeinBerlinPhase.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinAlexanderplatz.moduleName,
            AdhMeinBerlinBplaene.moduleName,
            AdhMeinBerlinKiezkassen.moduleName,
            AdhMeinBerlinBurgerhaushalt.moduleName
        ]);
};
