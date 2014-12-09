/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular-route.d.ts"/>

import _ = require("lodash");

import AdhTopLevelState = require("../TopLevelState/TopLevelState");
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
    "create-or-show-comment-listing",
    "login",
    "register",
    "user-indicator",
    "empty"
];

var metaParams = [
    "autoresize",
    "locale",
    "nocenter",
    "noheader"
];

export var location2template = ($location : ng.ILocationService) => {
    var widget : string = $location.path().split("/")[2];
    var search = $location.search();

    var attrs = [];
    if (!AdhUtil.isArrayMember(widget, embeddableDirectives)) {
        throw "unknown widget: " + widget;
    }

    if (widget === "empty") {
        return "";
    }
    for (var key in search) {
        if (search.hasOwnProperty(key) && metaParams.indexOf(key) === -1) {
            attrs.push(AdhUtil.formatString("data-{0}=\"{1}\"", _.escape(key), _.escape(search[key])));
        }
    }
    return AdhUtil.formatString("<adh-{0} {1}></adh-{0}>", _.escape(widget), attrs.join(" "));
};


export var moduleName = "adhEmbed";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelState.moduleName
        ])
        .config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
            adhTopLevelStateProvider
                .when("embed", ["$translate", "$location", ($translate, $location : ng.ILocationService) : AdhTopLevelState.IAreaInput => {
                    var params = $location.search();
                    if (params.hasOwnProperty("locale")) {
                        $translate.use(params.locale);
                    }
                    var template = location2template($location);

                    if (!params.hasOwnProperty("nocenter")) {
                        template = "<div class=\"l-center\">" + template + "</div>";
                    }

                    if (!params.hasOwnProperty("noheader")) {
                        template = "<header class=\"l-header main-header\">" +
                        "<div class=\"l-header-wrapper\"><div class=\"l-header-right\">" +
                        "<adh-user-indicator></adh-user-indicator>" +
                        "</div></div></header>" + template;
                    }
                    return {
                        template: template
                    };
                }]);
        }]);
};
