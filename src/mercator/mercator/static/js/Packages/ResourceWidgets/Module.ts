import * as AdhEventManagerModule from "../Core/EventManager/Module";
import * as AdhHttpModule from "../Core/Http/Module";
import * as AdhPreliminaryNamesModule from "../Core/PreliminaryNames/Module";

import * as AdhResourceWidgets from "./ResourceWidgets";


export var moduleName = "adhResourceWidgets";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEventManagerModule.moduleName,
            AdhHttpModule.moduleName,
            AdhPreliminaryNamesModule.moduleName
        ])
        .directive("adhResourceWrapper", AdhResourceWidgets.resourceWrapper);
};
