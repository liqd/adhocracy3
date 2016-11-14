/// <reference path="../../../_all.d.ts"/>

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
