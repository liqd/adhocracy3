require.config({
    baseUrl: "/static/js/",
% if url_args:
    urlArgs: "${url_args}",
% endif
    config: {
        text: {
            useXhr: function (url, protocol, hostname, port) {
                // we have CORS headers set for all text resources we load
                // through require.
                return true;
            }
        }
    },
    paths: {
% if minify:
        Adhocracy: "./Adhocracy.min",
% else:
        Adhocracy: "./Adhocracy",
        adhTemplates: "./templates",
% endif
        text: "../lib/requirejs-text/text",
% if minify:
        angular: "../lib/angular/angular.min",
% else:
        angular: "../lib/angular/angular",
% endif
        angularAnimate: "../lib/angular-animate/angular-animate.min",
        angularAria: "../lib/angular-aria/angular-aria.min",
        "angular-cache": "../lib/angular-cache/dist/angular-cache.min",
        angularTranslateLoader: "../lib/angular-translate-loader-static-files/angular-translate-loader-static-files.min",
        angularTranslate: "../lib/angular-translate/dist/angular-translate.min",
        angularElastic: "../lib/angular-elastic/elastic",
        angularScroll: "../lib/angular-scroll/angular-scroll.min",
        angularFlow: "../lib/ng-flow/dist/ng-flow.min",
        angularMessages: "../lib/angular-messages/angular-messages.min",
        markdownit: "../lib/markdown-it/dist/markdown-it.min",
        flow: "../lib/flow/flow",
        leaflet: "../lib/leaflet/dist/leaflet",
        leafletMarkerCluster: "../lib/leaflet.markercluster/dist/leaflet.markercluster",
        lodash: "../lib/lodash/lodash.min",
        q: "../lib/q/q",
        modernizr: "../lib2/modernizr/modernizr.min",
        moment: "../lib/moment/min/moment-with-locales.min",
        sticky: "../lib/relatively-sticky/jquery.relatively-sticky.min",
        socialSharePrivacy: "../lib/jquery.socialshareprivacy/jquery.socialshareprivacy.min",
        polyfiller: "../lib/webshim/js-webshim/minified/polyfiller"
    },
    shim: {
        jquery: {
            exports: "$"
        },
        angular: {
            exports: "angular"
        },
        angularAnimate: {
            deps: ["angular"]
        },
        angularAria: {
            deps: ["angular"]
        },
        angularMessages: {
            deps: ["angular"]
        },
        "angular-cache": {
            deps: ["angular"]
        },
        angularTranslate: {
            deps: ["angular"]
        },
        angularTranslateLoader: {
            deps: ["angularTranslate"]
        },
        angularElastic: {
            deps: ["angular"]
        },
        angularScroll: {
            deps: ["angular"]
        },
        angularFlow: {
            deps: ["angular", "flow"]
        },
        modernizr: {
            exports: "Modernizr"
        },
        sticky: {
            deps: ["jquery"]
        },
        leafletMarkerCluster: {
            deps: ["leaflet"]
        }
    }
});
