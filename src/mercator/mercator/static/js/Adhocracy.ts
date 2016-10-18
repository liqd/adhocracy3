/// <reference path="../lib2/types/angular.d.ts"/>
/// <reference path="../lib2/types/lodash.d.ts"/>
/// <reference path="../lib2/types/moment.d.ts"/>
/// <reference path="./_all.d.ts"/>

import * as angular from "angular";

import * as angularAnimate from "angularAnimate";  if (angularAnimate) { ; };
import * as angularAria from "angularAria";  if (angularAria) { ; };
import * as angularMessages from "angularMessages";  if (angularMessages) { ; };
import * as angularCache from "angular-cache";  if (angularCache) { ; };
import * as angularTranslate from "angularTranslate";  if (angularTranslate) { ; };
import * as angularTranslateLoader from "angularTranslateLoader";  if (angularTranslateLoader) { ; };
import * as angularElastic from "angularElastic";  if (angularElastic) { ; };
import * as angularScroll from "angularScroll";  if (angularScroll) { ; };
import * as angularFlow from "angularFlow";  if (angularFlow) { ; };

import * as markdownit from "markdownit";
import * as modernizr from "modernizr";
import * as moment from "moment";
import * as webshim from "polyfiller";

import * as AdhBlogModule from "./Packages/Blog/Module";
import * as AdhResourceWidgetsModule from "./Packages/ResourceWidgets/Module";
import * as AdhCoreModule from "./Packages/Core/Module";
import * as AdhMercatorModule from "./Packages/Mercator/Module";

import * as AdhConfig from "./Packages/Core/Config/Config";
import * as AdhTopLevelState from "./Packages/Core/TopLevelState/TopLevelState";

import * as AdhTemplates from "adhTemplates";  if (AdhTemplates) { ; };

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
        "duScroll",
        "flow",
        AdhCoreModule.moduleName,
        AdhMercatorModule.moduleName
    ];

    if (config.cachebust) {
        appDependencies.push("templates");
    }

    var app = angular.module("a3Mercator", appDependencies);

    app.config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
        adhTopLevelStateProvider
            .when("", ["$location", "adhConfig", "adhEmbed", ($location, adhConfig, adhEmbed) : AdhTopLevelState.IAreaInput => {
                var url;
                if (adhEmbed.initialUrl) {
                    url = adhEmbed.initialUrl;
                } else if (adhConfig.redirect_url !== "/") {
                    url = adhConfig.redirect_url;
                } else {
                    url = "/r/";
                }
                $location.replace();
                $location.path(url);
                return {
                    skip: true
                };
            }])
            .otherwise(() : AdhTopLevelState.IAreaInput => {
                return {
                    template: "<adh-header></adh-header><div class=\"l-content\"><h1>404 - Not Found</h1></div>"
                };
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
                prefix: "/static/i18n/mercator_",
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

    // register our modules
    AdhBlogModule.register(angular);
    AdhResourceWidgetsModule.register(angular);
    AdhCoreModule.register(angular, config, metaApi);
    AdhMercatorModule.register(angular);

    // force-load some services
    var injector = angular.bootstrap(document.body, ["a3Mercator"], {strictDi: true});
    injector.get("adhCrossWindowMessaging");

    loadComplete();
};
