import * as AdhEventManagerModule from "../EventManager/Module";

import * as AdhLocalSocket from "./LocalSocket";


export var moduleName = "adhLocalSocket";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEventManagerModule.moduleName
        ])
        .service("adhLocalSocket", ["adhEventManagerClass", AdhLocalSocket.Service]);
};
