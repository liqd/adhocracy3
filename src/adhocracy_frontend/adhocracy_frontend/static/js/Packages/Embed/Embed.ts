/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular-route.d.ts"/>

import _ = require("lodash");

import AdhUtil = require("../Util/Util");

/**
 * List of directive names that can be embedded.  names must be in
 * lower-case with dashes, but without 'adh-' prefix.  (example:
 * 'document-workbench' for directive DocumentWorkbench.)
 */
var embeddableDirectives = [
    "document-workbench",
    "paragraph-version-detail",
    "comment-listing",
    "create-or-show-comment-listing"
];

export var route2template = ($route : ng.route.IRouteService) => {
    var params = $route.current.params;

    var attrs = [];
    if (!params.hasOwnProperty("widget")) {
        throw "widget not specified";
    }
    if (!AdhUtil.isArrayMember(params.widget, embeddableDirectives)) {
        throw "unknown widget: " + params.widget;
    }
    for (var key in params) {
        if (params.hasOwnProperty(key) && key !== "widget" && key !== "locale") {
            attrs.push(AdhUtil.formatString("data-{0}=\"{1}\"", _.escape(key), _.escape(params[key])));
        }
    }
    return AdhUtil.formatString("<adh-{0} {1}></adh-{0}>", _.escape(params.widget), attrs.join(" "));
};

export var factory = ($compile : ng.ICompileService, $route : ng.route.IRouteService) => {
    return {
        restrict: "E",
        scope: {},
        link: (scope, element) => {
            var template = "<header class=\"l-header main-header\">" +
                "<adh-user-indicator></adh-user-indicator>" +
                "</header>";
            template += route2template($route);
            element.html(template);
            $compile(element.contents())(scope);
        }
    };
};
