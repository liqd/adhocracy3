import _ = require("underscore");

import Util = require("./Util");

/**
 * List of directive names that can be embedded.  names must be in
 * lower-case with dashes, but without 'adh-' prefix.  (example:
 * 'document-workbench' for directive DocumentWorkbench.)
 */
var embeddableDirectives = ["document-workbench", "paragraph-version-detail"];

export var route2template = ($route) => {
    var params = $route.current.params;

    var attrs = [];
    if (!params.hasOwnProperty("widget")) {
        throw "widget not specified";
    }
    if (!Util.isArrayMember(params.widget, embeddableDirectives)) {
        throw "unknown widget: " + params.widget;
    }
    for (var key in params) {
        if (params.hasOwnProperty(key) && key !== "widget") {
            attrs.push(Util.formatString("data-{0}=\"{1}\"", _.escape(key), _.escape(Util.escapeNgExp(params[key]))));
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
