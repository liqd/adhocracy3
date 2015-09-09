/// <reference path="../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/lodash/lodash.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/modernizr/modernizr.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/moment/moment.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/leaflet/leaflet.d.ts"/>
/// <reference path="./_all.d.ts"/>

import angular = require("angular");

import angularAnimate = require("angularAnimate");  if (angularAnimate) { ; };
import angularAria = require("angularAria");  if (angularAria) { ; };
import angularMessages = require("angularMessages");  if (angularMessages) { ; };
import angularCache = require("angularCache");  if (angularCache) { ; };
import angularTranslate = require("angularTranslate");  if (angularTranslate) { ; };
import angularTranslateLoader = require("angularTranslateLoader");  if (angularTranslateLoader) { ; };
import angularElastic = require("angularElastic");  if (angularElastic) { ; };
import angularScroll = require("angularScroll");  if (angularScroll) { ; };
import angularFlow = require("angularFlow");  if (angularFlow) { ; };

import markdownit = require("markdownit");
import modernizr = require("modernizr");
import moment = require("moment");
import leaflet = require("leaflet");
import webshim = require("polyfiller");

import AdhAbuseModule = require("./Packages/Abuse/Module");
import AdhAngularHelpersModule = require("./Packages/AngularHelpers/Module");
import AdhBadgeModule = require("./Packages/Badge/Module");
import AdhCommentModule = require("./Packages/Comment/Module");
import AdhCrossWindowMessagingModule = require("./Packages/CrossWindowMessaging/Module");
import AdhDateTimeModule = require("./Packages/DateTime/Module");
import AdhDocumentModule = require("./Packages/Document/Module");
import AdhDoneModule = require("./Packages/Done/Module");
import AdhEmbedModule = require("./Packages/Embed/Module");
import AdhEventManagerModule = require("./Packages/EventManager/Module");
import AdhHttpModule = require("./Packages/Http/Module");
import AdhImageModule = require("./Packages/Image/Module");
import AdhInjectModule = require("./Packages/Inject/Module");
import AdhListingModule = require("./Packages/Listing/Module");
import AdhLocaleModule = require("./Packages/Locale/Module");
import AdhLocalSocketModule = require("./Packages/LocalSocket/Module");
import AdhMappingModule = require("./Packages/Mapping/Module");
import AdhMarkdownModule = require("./Packages/Markdown/Module");
import AdhMeinBerlinProposalModule = require("./Packages/Proposal/Module");
import AdhMeinBerlinModule = require("./Packages/MeinBerlin/Module");
import AdhMovingColumnsModule = require("./Packages/MovingColumns/Module");
import AdhPermissionsModule = require("./Packages/Permissions/Module");
import AdhPreliminaryNamesModule = require("./Packages/PreliminaryNames/Module");
import AdhProcessModule = require("./Packages/Process/Module");
import AdhRateModule = require("./Packages/Rate/Module");
import AdhResourceAreaModule = require("./Packages/ResourceArea/Module");
import AdhResourceWidgetsModule = require("./Packages/ResourceWidgets/Module");
import AdhShareSocialModule = require("./Packages/ShareSocial/Module");
import AdhStickyModule = require("./Packages/Sticky/Module");
import AdhTabsModule = require("./Packages/Tabs/Module");
import AdhTopLevelStateModule = require("./Packages/TopLevelState/Module");
import AdhTrackingModule = require("./Packages/Tracking/Module");
import AdhUserModule = require("./Packages/User/Module");
import AdhUserViewsModule = require("./Packages/User/ViewsModule");
import AdhWebSocketModule = require("./Packages/WebSocket/Module");

import AdhConfig = require("./Packages/Config/Config");
import AdhTopLevelState = require("./Packages/TopLevelState/TopLevelState");

import AdhTemplates = require("adhTemplates");  if (AdhTemplates) { ; };

webshim.setOptions("basePath", "/static/lib/webshim/js-webshim/minified/shims/");
webshim.setOptions("forms-ext", {"replaceUI": true});
webshim.setOptions({"waitReady": false});
webshim.polyfill("forms forms-ext");

var loadComplete = () : void => {
    var w = (<any>window);
    w.adhocracy = w.adhocracy || {};
    w.adhocracy.loadState = "complete";
};


export var init = (config : AdhConfig.IService, metaApi) => {
    "use strict";

    // detect wheter we are running in iframe
    config.embedded = (window !== top);
    if (config.embedded) {
        window.document.body.className += " is-embedded";
    }

    var appDependencies = [
        "monospaced.elastic",
        "pascalprecht.translate",
        "ngAnimate",
        "ngAria",
        "ngMessages",
        "flow",
        AdhCommentModule.moduleName,
        AdhDoneModule.moduleName,
        AdhImageModule.moduleName,
        AdhMappingModule.moduleName,

        AdhCrossWindowMessagingModule.moduleName,
        AdhEmbedModule.moduleName,
        AdhMeinBerlinModule.moduleName,
        AdhResourceAreaModule.moduleName,
        AdhStickyModule.moduleName,
        AdhTrackingModule.moduleName,
        AdhUserViewsModule.moduleName
    ];

    if (config.cachebust) {
        appDependencies.push("templates");
    }

    var app = angular.module("a3", appDependencies);

    app.config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
        adhTopLevelStateProvider
            .when("", ["$location", ($location) : AdhTopLevelState.IAreaInput => {
                $location.replace();
                $location.path("/r/organisation/kiezkasse/");
                return {
                    skip: true
                };
            }])
            .otherwise(() : AdhTopLevelState.IAreaInput => {
                return {
                    template: "<adh-page-wrapper><h1>404 - Not Found</h1></adh-page-wrapper>"
                };
            })
            // FIXME: should be full urls. (but seems to work)
            .space("user", {
                resourceUrl: "/principals/users/"
            })
            .space("content", {
                resourceUrl: "/organisation/kiezkasse/"
            });
    }]);
    app.config(["$compileProvider", ($compileProvider) => {
        $compileProvider.debugInfoEnabled(config.debug);
    }]);
    app.config(["$locationProvider", ($locationProvider) => {
        // Make sure HTML5 history API works.  (If support for older
        // browsers is required, we may have to study angular support
        // for conversion between history API and #!-URLs.  See
        // angular documentation for details.)
        $locationProvider.html5Mode(true);
    }]);
    app.config(["$translateProvider", ($translateProvider) => {
         $translateProvider.useStaticFilesLoader({
            files: [{
                prefix: "/static/i18n/core_",
                suffix: config.cachebust ? ".json?" + config.cachebust_suffix : ".json"
            }, {
                prefix: "/static/i18n/countries_",
                suffix: config.cachebust ? ".json?" + config.cachebust_suffix : ".json"
            }, {
                prefix: "/static/i18n/meinberlin_",
                suffix: config.cachebust ? ".json?" + config.cachebust_suffix : ".json"
            }]
        });
        $translateProvider.useSanitizeValueStrategy("escape");
        $translateProvider.preferredLanguage(config.locale);
        $translateProvider.fallbackLanguage("en");
    }]);
    app.config(["$ariaProvider", ($ariaProvider) => {
        $ariaProvider.config({
            tabindex: false
        });
    }]);

    app.value("angular", angular);

    app.value("markdownit", markdownit);
    app.value("modernizr", modernizr);
    app.value("moment", moment);
    app.value("leaflet", leaflet);

    // register our modules
    app.value("adhConfig", config);
    AdhAbuseModule.register(angular);
    AdhBadgeModule.register(angular);
    AdhCommentModule.register(angular);
    AdhCrossWindowMessagingModule.register(angular, config.trusted_domains !== []);
    AdhDateTimeModule.register(angular);
    AdhDocumentModule.register(angular);
    AdhDoneModule.register(angular);
    AdhEmbedModule.register(angular);
    AdhEventManagerModule.register(angular);
    AdhHttpModule.register(angular, config, metaApi);
    AdhImageModule.register(angular);
    AdhInjectModule.register(angular);
    AdhListingModule.register(angular);
    AdhLocaleModule.register(angular);
    AdhLocalSocketModule.register(angular);
    AdhMeinBerlinModule.register(angular);
    AdhMeinBerlinProposalModule.register(angular);
    AdhMappingModule.register(angular);
    AdhMarkdownModule.register(angular);
    AdhMovingColumnsModule.register(angular);
    AdhPermissionsModule.register(angular);
    AdhPreliminaryNamesModule.register(angular);
    AdhProcessModule.register(angular);
    AdhRateModule.register(angular);
    AdhAngularHelpersModule.register(angular);
    AdhResourceAreaModule.register(angular);
    AdhResourceWidgetsModule.register(angular);
    AdhShareSocialModule.register(angular);
    AdhStickyModule.register(angular);
    AdhTabsModule.register(angular);
    AdhTopLevelStateModule.register(angular);
    AdhTrackingModule.register(angular);
    AdhUserModule.register(angular);
    AdhUserViewsModule.register(angular);
    AdhWebSocketModule.register(angular);

    // force-load some services
    var injector = angular.bootstrap(document.body, ["a3"], {strictDi: true});
    injector.get("adhCrossWindowMessaging");

    loadComplete();
};
