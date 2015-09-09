import AdhMeinBerlinKiezkassenModule = require("./Kiezkassen/Module");
import AdhMeinBerlinBplaeneModule = require("./Bplaene/Module");
import AdhMeinBerlinAlexanderplatzModule = require("./Alexanderplatz/Module");
import AdhMeinBerlinBurgerhaushaltModule = require("./Burgerhaushalt/Module");
import AdhMeinBerlinPhaseModule = require("./Phase/Module");


export var moduleName = "adhMeinBerlin";

export var register = (angular) => {
    AdhMeinBerlinKiezkassenModule.register(angular);
    AdhMeinBerlinBplaeneModule.register(angular);
    AdhMeinBerlinAlexanderplatzModule.register(angular);
    AdhMeinBerlinBurgerhaushaltModule.register(angular);
    AdhMeinBerlinPhaseModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinAlexanderplatzModule.moduleName,
            AdhMeinBerlinBplaeneModule.moduleName,
            AdhMeinBerlinKiezkassenModule.moduleName,
            AdhMeinBerlinBurgerhaushaltModule.moduleName
        ]);
};
