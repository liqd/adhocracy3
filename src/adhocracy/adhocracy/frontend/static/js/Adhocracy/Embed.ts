import _ = require("underscore");

import Util = require("./Util");


export var route2template = ($route) => {
    var params = $route.current.params;

    var attrs = [];
    for (var key in params) {
        if (params.hasOwnProperty(key) && key !== "widget") {
            attrs.push(Util.formatString("data-{0}=\"{1}\"", _.escape(key), _.escape(params[key])));
        }
    }
    return Util.formatString("<adh-{0} {1}></adh-{0}>", _.escape(params.widget), attrs.join(" "));
};

export var factory = ($compile, $route) => {
    return {
        restrict: "E",
        scope: {},
        link: (scope, element) => {
            element.html(route2template($route));
            $compile(element.contents())(scope);
        }
    };
};
