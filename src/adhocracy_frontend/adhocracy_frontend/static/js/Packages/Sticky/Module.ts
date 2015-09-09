import Sticky = require("sticky"); if (Sticky) { ; };

import AdhSticky = require("./Sticky");


export var moduleName = "adhSticky";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhSticky", ["modernizr", AdhSticky.createDirective]);
};
