require.config({
    baseUrl: "/static/js/",
    paths: {
        text: "../lib/requirejs-text/text",
        jquery: "../lib/jquery/dist/jquery",
        angular: "../lib/angular/angular",
        angularRoute: "../lib/angular-route/angular-route",
        angularAnimate: "../lib/angular-animate/angular-animate",
        lodash: "../lib/lodash/dist/lodash",
        q: "../lib/q/q",
        modernizr: "../lib2/modernizr/modernizr-2.8.3.min",
        moment: "../lib/moment/moment"
    },
    shim: {
        jquery: {
            exports: "$"
        },
        angular: {
            exports: "angular"
        },
        angularRoute: {
            deps: ["angular"]
        },
        angularAnimate: {
            deps: ["angular"]
        },
        underscore: {
            exports: "_"
        },
        modernizr: {
            exports: "Modernizr"
        }
    }
});
