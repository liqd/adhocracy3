/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/modernizr/modernizr.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import angular = require("angular");
import angularRoute = require("angularRoute");  angularRoute;
// (since angularRoute does not export any objects or types we would
// want to use, the extra mention of the module name is needed to keep
// tsc from purging this import entirely.  which would have undesired
// runtime effects.)

import modernizr = require("modernizr");

import AdhHttp = require("../Services/Http");
import AdhWebSocket = require("../Services/WebSocket");
import AdhUser = require("../Services/User");
import AdhDone = require("../Services/Done");
import AdhCrossWindowMessaging = require("../Services/CrossWindowMessaging");
import AdhRecursionHelper = require("../Services/RecursionHelper");

import Resources = require("../Resources");
import Widgets = require("../Widgets");
import Directives = require("../Directives");
import Filters = require("../Filters");
import Embed = require("../Embed");


export var run = (config) => {
    "use strict";

    var app = angular.module("adhocracy3SampleFrontend", ["ngRoute"]);

    app.config(["$routeProvider", "$locationProvider", ($routeProvider, $locationProvider) => {
        $routeProvider
            .when("/frontend_static/root.html", {
                templateUrl: config.template_path + "/Wrapper.html"
            })
            .when("/embed/:widget", {
                template: "<adh-embed></adh-embed>"
            })
            .otherwise({
                // FIXME: proper error template
                template: "<h1>404 - not Found</h1>"
            });

        // Make sure HTML5 history API works.  (If support for older
        // browsers is required, we may have to study angular support
        // for conversion between history API and #!-URLs.  See
        // angular documentation for details.)
        $locationProvider.html5Mode(true);
    }]);

    app.value("Modernizr", modernizr);

    app.service("adhResources", Resources.Service);
    app.service("adhUser", AdhUser.User);
    app.directive("adhLogin", ["adhUser", AdhUser.loginDirective]);
    app.value("adhConfig", config);
    app.factory("adhDone", AdhDone.factory);

    app.factory("recursionHelper", ["$compile", AdhRecursionHelper.factory]);
    app.factory("adhHttp", ["$http", AdhHttp.factory]);
    app.factory("adhWebSocket", ["Modernizr", "adhConfig", AdhWebSocket.factory]);

    app.factory("adhCrossWindowMessaging", ["adhConfig", "$window", "$rootScope", AdhCrossWindowMessaging.factory]);

    app.filter("documentTitle", [Filters.filterDocumentTitle]);

    app.directive("adhEmbed", ["$compile", "$route", Embed.factory]);

    app.directive("adhListing",
        ["adhConfig", (adhConfig) =>
            new Widgets.Listing(new Widgets.ListingPoolAdapter()).createDirective(adhConfig)]);

    app.directive("adhListingElement",
        ["$q", "adhConfig", ($q, adhConfig) =>
            new Widgets.ListingElement(new Widgets.ListingElementAdapter($q)).createDirective(adhConfig)]);

    app.directive("adhListingElementTitle",
        ["$q", "adhHttp", "adhConfig", ($q, adhHttp, adhConfig) =>
            new Widgets.ListingElement(new Widgets.ListingElementTitleAdapter($q, adhHttp)).createDirective(adhConfig)]);

    app.directive("adhWebSocketTest",
        ["$timeout", "adhConfig", "adhWebSocket", ($timeout, adhConfig, adhWebSocket) =>
            new AdhWebSocket.WebSocketTest().createDirective($timeout, adhConfig, adhWebSocket)]);


    // application-specific (local) directives

    app.directive("adhDocumentWorkbench", ["adhConfig", "adhResources", "adhCrossWindowMessaging", Directives.adhDocumentWorkbench]);
    app.directive("adhProposalVersionDetail", ["adhConfig", Directives.adhProposalVersionDetail]);
    app.directive("adhProposalVersionEdit", ["adhConfig", Directives.adhProposalVersionEdit]);
    app.directive("adhProposalVersionNew", ["adhHttp", "adhConfig", "adhResources", Directives.adhProposalVersionNew]);
    app.directive("adhSectionVersionDetail", ["adhConfig", "recursionHelper", Directives.adhSectionVersionDetail]);
    app.directive("adhParagraphVersionDetail", ["adhConfig", Directives.adhParagraphVersionDetail]);
    app.directive("adhDocumentSheetEdit", ["adhHttp", "$q", "adhConfig", Directives.adhDocumentSheetEdit]);
    app.directive("adhDocumentSheetShow", ["adhConfig", Directives.adhDocumentSheetShow]);
    app.directive("adhParagraphSheetEdit", ["adhConfig", Directives.adhParagraphSheetEdit]);


    // get going

    angular.bootstrap(document, ["adhocracy3SampleFrontend"]);
};
