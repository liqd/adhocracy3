import * as Sticky from "sticky"; if (Sticky) { ; };

import * as AdhSticky from "./Sticky";


export var moduleName = "adhSticky";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhSticky", ["modernizr", AdhSticky.createDirective]);
};
