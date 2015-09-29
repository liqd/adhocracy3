import * as AdhMeinberlinKiezkasseModule from "./Kiezkasse/Module";
import * as AdhMeinberlinBplaeneModule from "./Bplaene/Module";
import * as AdhMeinberlinAlexanderplatzModule from "./Alexanderplatz/Module";
import * as AdhMeinberlinBurgerhaushaltModule from "./Burgerhaushalt/Module";
import * as AdhMeinberlinPhaseModule from "./Phase/Module";


export var moduleName = "adhMeinberlin";

export var register = (angular) => {
    AdhMeinberlinKiezkasseModule.register(angular);
    AdhMeinberlinBplaeneModule.register(angular);
    AdhMeinberlinAlexanderplatzModule.register(angular);
    AdhMeinberlinBurgerhaushaltModule.register(angular);
    AdhMeinberlinPhaseModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinAlexanderplatzModule.moduleName,
            AdhMeinberlinBplaeneModule.moduleName,
            AdhMeinberlinKiezkasseModule.moduleName,
            AdhMeinberlinBurgerhaushaltModule.moduleName
        ]);
};
