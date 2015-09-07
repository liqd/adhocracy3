import AdhEventManager = require("./EventManager");


export var moduleName = "adhEventManager";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .value("adhEventManagerClass", AdhEventManager.EventManager);
};
