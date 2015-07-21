/// <reference path="../../_all.d.ts"/>

import Sticky = require("sticky"); if (Sticky) { ; };


export var createDirective = (modernizr : ModernizrStatic) => {
    return {
        restrict: "A",
        link: (scope, element, attrs) => {
            if ((<any>modernizr).csspositionsticky) {
                element.addClass("sticky");
            } else {
                element.stick_in_parent({
                    scrollable: ".moving-column-body"
                });
            }
        }
    };
};


export var moduleName = "adhSticky";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhSticky", ["modernizr", createDirective]);
};
