import AdhEventManagerModule = require("../EventManager/Module");

import AdhWebSocket = require("./WebSocket");


export var moduleName = "adhWebSocket";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEventManagerModule.moduleName
        ])
        .factory("adhRawWebSocketFactory", ["modernizr", AdhWebSocket.rawWebSocketFactoryFactory])
        .service("adhWebSocket", ["adhConfig", "adhEventManagerClass", "adhRawWebSocketFactory", AdhWebSocket.Service]);
};
