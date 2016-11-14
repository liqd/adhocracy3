import * as AdhHttpModule from "../Http/Module";
import * as AdhProcessModule from "../Process/Module";

import * as Home from "./Home";

export var moduleName = "adhHome";


export var register = (angular) => {
    angular.module(moduleName, [
        AdhHttpModule.moduleName,
        AdhProcessModule.moduleName,
    ])
    .directive("adhHome", ["adhConfig", "adhHttp", Home.homeDirective]);
};
