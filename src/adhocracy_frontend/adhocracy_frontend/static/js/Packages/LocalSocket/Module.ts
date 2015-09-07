import AdhEventManagerModule = require("../EventManager/Module");

import AdhLocalSocket = require("./LocalSocket");


export var moduleName = "adhLocalSocket";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEventManagerModule.moduleName
        ])
        .service("adhLocalSocket", ["adhEventManagerClass", AdhLocalSocket.Service]);
};
