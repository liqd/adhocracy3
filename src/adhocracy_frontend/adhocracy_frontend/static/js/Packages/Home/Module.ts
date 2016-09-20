import * as AdhProcessModule from "../Process/Module";

import * as Home from "./Home";

export var moduleName = "adhHome";


export var register = (angular) => {
    angular.module(moduleName, [
        AdhProcessModule.moduleName,
    ])
    .directive("adhHome", ["adhConfig", Home.homeDirective]);
};
