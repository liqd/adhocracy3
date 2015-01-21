/// <reference path="../../_all.d.ts"/>

import Sticky = require("sticky"); if (Sticky) { ; };


export var createDirective = () => {
    return {
        restrict: "A",
        link: (scope, element, attrs) => {
            element.stick_in_parent({
                scrolling_parent: ".moving-column-body",
                recalc_every: 2000,
                bottoming: false
            });
        }
    };
};


export var moduleName = "adhSticky";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhSticky", [createDirective]);
};
