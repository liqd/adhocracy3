/// <reference path="../../_all.d.ts"/>

import Sticky = require("sticky"); if (Sticky) { ; };


export var createDirective = () => {
    return {
        restrict: "A",
        link: (scope, element, attrs) => {
            var el = element.first();
            var par = el.parents(".moving-column-body");

            // if we are in a moving column use this as our parent by default
            var opts = (par.length > 0) ? { scrolling_parent: par } : {};
            el.stick_in_parent(opts);
        }
    };
};


export var moduleName = "adhSticky";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhSticky", [createDirective]);
};
