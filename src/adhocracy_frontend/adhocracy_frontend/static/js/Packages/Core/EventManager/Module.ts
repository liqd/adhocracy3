import * as AdhEventManager from "./EventManager";


export var moduleName = "adhEventManager";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .value("adhEventManagerClass", AdhEventManager.EventManager);
};
