/// <reference path="../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/lodash/lodash.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/modernizr/modernizr.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/moment/moment.d.ts"/>
/// <reference path="./_all.d.ts"/>

import angular = require("angular");
import angularRoute = require("angularRoute");  if (angularRoute) { ; };
// (since angularRoute does not export any objects or types we would
// want to use, the extra mention of the module name is needed to keep
// tsc from purging this import entirely.  which would have undesired
// runtime effects.)

import angularAnimate = require("angularAnimate");  if (angularAnimate) { ; };
import angularTranslate = require("angularTranslate");  if (angularTranslate) { ; };
import angularTranslateLoader = require("angularTranslateLoader");  if (angularTranslateLoader) { ; };
import angularElastic = require("angularElastic");  if (angularElastic) { ; };

import modernizr = require("modernizr");
import moment = require("moment");

import AdhConfig = require("./Packages/Config/Config");
import AdhComment = require("./Packages/Comment/Comment");
import AdhCrossWindowMessaging = require("./Packages/CrossWindowMessaging/CrossWindowMessaging");
import AdhDateTime = require("./Packages/DateTime/DateTime");
import AdhDocumentWorkbench = require("./Packages/DocumentWorkbench/DocumentWorkbench");
import AdhDone = require("./Packages/Done/Done");
import AdhEmbed = require("./Packages/Embed/Embed");
import AdhEventHandler = require("./Packages/EventHandler/EventHandler");
import AdhHttp = require("./Packages/Http/Http");
import AdhInject = require("./Packages/Inject/Inject");
import AdhListing = require("./Packages/Listing/Listing");
import AdhPermissions = require("./Packages/Permissions/Permissions");
import AdhPreliminaryNames = require("./Packages/PreliminaryNames/PreliminaryNames");
import AdhProposal = require("./Packages/Proposal/Proposal");
import AdhRate = require("./Packages/Rate/Rate");
import AdhRecursionHelper = require("./Packages/RecursionHelper/RecursionHelper");
import AdhResourceWidgets = require("./Packages/ResourceWidgets/ResourceWidgets");
import AdhRoute = require("./Packages/Route/Route");
import AdhTopLevelState = require("./Packages/TopLevelState/TopLevelState");
import AdhUser = require("./Packages/User/User");
import AdhWebSocket = require("./Packages/WebSocket/WebSocket");


var loadComplete = () : void => {
    var w = (<any>window);
    w.adhocracy = w.adhocracy || {};
    w.adhocracy.loadState = "complete";
};


export var init = (config : AdhConfig.IService, meta_api) => {
    "use strict";

    // detect wheter we are running in iframe
    config.embedded = (window !== top);
    if (config.embedded) {
        window.document.body.className += " is-embedded";
    }

    var app = angular.module("adhocracy3SampleFrontend", [
        "monospaced.elastic",
        "pascalprecht.translate",
        "ngRoute",
        "ngAnimate",
        AdhComment.moduleName,
        AdhDocumentWorkbench.moduleName,
        AdhDone.moduleName,
        AdhCrossWindowMessaging.moduleName,
        AdhEmbed.moduleName,
        AdhRoute.moduleName,
        AdhProposal.moduleName
    ]);

    app.config(["$translateProvider", "$routeProvider", "$locationProvider", (
        $translateProvider,
        $routeProvider,
        $locationProvider
    ) => {
        $routeProvider
            .when("/", {
                template: "",
                controller: ["adhConfig", "$location", (adhConfig, $location) => {
                    $location.replace();
                    $location.path("/r" + adhConfig.rest_platform_path);
                }]
            })
            .when("/r/:path*", {
                controller: ["adhHttp", "adhConfig", "adhTopLevelState", "$routeParams", "$scope", AdhRoute.resourceRouter],
                templateUrl: "/static/js/templates/Wrapper.html",
                reloadOnSearch: false
            })
            .when("/login", {
                templateUrl: "/static/js/templates/Login.html"
            })
            .when("/register", {
                templateUrl: "/static/js/templates/Register.html"
            })
            .when("/activate/:key", {
                controller: ["adhUser", "adhTopLevelState", "adhDone", "$location", AdhUser.activateController],
                template: ""
            })
            .when("/activation_error", {
                templateUrl: "/static/js/templates/ActivationError.html",
                controller: ["adhConfig", "$scope", (adhConfig, $scope) => {
                    $scope.translationData = {
                        supportEmail: adhConfig.support_email
                    };
                }]
            })
            .when("/embed/:widget", {
                template: "<adh-embed></adh-embed>",
                controller: ["$translate", "$route", ($translate, $route : ng.route.IRouteService) => {
                    var params = $route.current.params;
                    if (params.hasOwnProperty("locale")) {
                        $translate.use(params.locale);
                    }
                }]
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

        $translateProvider.useStaticFilesLoader({
            prefix: "/static/i18n/",
            suffix: ".json"
        });
        $translateProvider.preferredLanguage(config.locale);
        $translateProvider.fallbackLanguage("en");
    }]);

    app.value("angular", angular);
    app.value("Modernizr", modernizr);
    app.value("moment", moment);

    app.filter("signum", () => (n : number) : string => n > 0 ? "+" + n.toString() : n.toString());

    // register our modules
    app.value("adhConfig", config);
    AdhComment.register(angular);
    AdhCrossWindowMessaging.register(angular, config.trusted_domains === []);
    AdhDateTime.register(angular);
    AdhDocumentWorkbench.register(angular);
    AdhDone.register(angular);
    AdhEmbed.register(angular);
    AdhEventHandler.register(angular);
    AdhHttp.register(angular, meta_api);
    AdhInject.register(angular);
    AdhListing.register(angular);
    AdhPermissions.register(angular);
    AdhPreliminaryNames.register(angular);
    AdhProposal.register(angular);
    AdhRate.register(angular);
    AdhRecursionHelper.register(angular);
    AdhResourceWidgets.register(angular);
    AdhRoute.register(angular);
    AdhTopLevelState.register(angular);
    AdhUser.register(angular);
    AdhWebSocket.register(angular);

    // force-load some services
    var injector = angular.bootstrap(document, ["adhocracy3SampleFrontend"]);
    injector.get("adhCrossWindowMessaging");

    loadComplete();
};
