/// <reference path="../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/modernizr/modernizr.d.ts"/>
/// <reference path="./_all.d.ts"/>

import angular = require("angular");
import angularRoute = require("angularRoute");  if (angularRoute) { return; };
// (since angularRoute does not export any objects or types we would
// want to use, the extra mention of the module name is needed to keep
// tsc from purging this import entirely.  which would have undesired
// runtime effects.)

import modernizr = require("modernizr");

import AdhHttp = require("./Adhocracy/Http/Http");
import AdhWebSocket = require("./Adhocracy/WebSocket/WebSocket");
import AdhUser = require("./Adhocracy/User/User");
import AdhDone = require("./Adhocracy/Done/Done");
import AdhCrossWindowMessaging = require("./Adhocracy/CrossWindowMessaging/CrossWindowMessaging");
import AdhRecursionHelper = require("./Adhocracy/RecursionHelper/RecursionHelper");

import Resources = require("./Resources");
import Listing = require("./Adhocracy/Listing/Listing");
import Directives = require("./Adhocracy/TODO/Directives");
import Embed = require("./Adhocracy/Embed/Embed");


export var init = (config) => {
    "use strict";

    // detect wheter we are running in iframe
    config.embedded = (window !== top);
    if (config.embedded) {
        window.document.body.className += " is-embedded";
    }

    var app = angular.module("adhocracy3SampleFrontend", ["ngRoute"]);

    app.config(["$routeProvider", "$locationProvider", ($routeProvider, $locationProvider) => {
        $routeProvider
            .when("/frontend_static/root.html", {
                templateUrl: config.template_path + "/Wrapper.html"
            })
            .when("/register", {
                template: "<adh-register></adh-register>"
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
    app.service("adhUser", ["adhHttp", "$q", "$http", "$window", "Modernizr", AdhUser.User]);
    app.directive("adhLogin", ["adhConfig", AdhUser.loginDirective]);
    app.directive("adhRegister", ["adhConfig", "$location", AdhUser.registerDirective]);
    app.value("adhConfig", config);
    app.factory("adhDone", AdhDone.factory);

    app.factory("recursionHelper", ["$compile", AdhRecursionHelper.factory]);
    app.service("adhHttp", ["$http", "$q", AdhHttp.Service]);
    app.factory("adhWebSocket", ["Modernizr", "adhConfig", AdhWebSocket.factory]);

    app.factory("adhCrossWindowMessaging", ["adhConfig", "$window", "$rootScope", AdhCrossWindowMessaging.factory]);

    app.directive("adhEmbed", ["$compile", "$route", Embed.factory]);

    app.directive("adhListing",
        ["adhConfig", (adhConfig) =>
            new Listing.Listing(new Listing.ListingPoolAdapter()).createDirective(adhConfig)]);

    app.directive("adhListingElement",
        ["$q", "adhConfig", ($q, adhConfig) =>
            new Listing.ListingElement(new Listing.ListingElementAdapter($q)).createDirective(adhConfig)]);

    app.directive("adhListingElementTitle",
        ["$q", "adhHttp", "adhConfig", ($q, adhHttp, adhConfig) =>
            new Listing.ListingElement(new Listing.ListingElementTitleAdapter($q, adhHttp)).createDirective(adhConfig)]);

    app.directive("adhWebSocketTest",
        ["$timeout", "adhConfig", "adhWebSocket", ($timeout, adhConfig, adhWebSocket) =>
            new AdhWebSocket.WebSocketTest().createDirective($timeout, adhConfig, adhWebSocket)]);


    // application-specific (local) directives

    // adhCrossWindowMessaging does work by itself. We only need to inject in anywhere in order to instantiate it.
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
