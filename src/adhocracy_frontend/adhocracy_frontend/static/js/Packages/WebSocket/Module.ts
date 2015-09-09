import * as AdhEventManagerModule from "../EventManager/Module";

import * as AdhWebSocket from "./WebSocket";


export var moduleName = "adhWebSocket";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEventManagerModule.moduleName
        ])
        .factory("adhRawWebSocketFactory", ["modernizr", AdhWebSocket.rawWebSocketFactoryFactory])
        .service("adhWebSocket", ["adhConfig", "adhEventManagerClass", "adhRawWebSocketFactory", AdhWebSocket.Service]);
};
