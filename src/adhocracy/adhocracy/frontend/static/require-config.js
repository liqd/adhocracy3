require.config({
    baseUrl: "/frontend_static/js/",
    paths: {
        text: "../lib/requirejs-text/text",
        jquery: "../lib/jquery/dist/jquery",
        angular: "../lib/angular/angular",
        angularRoute: "../lib/angular-route/angular-route",
        angularAnimate: "../lib/angular-animate/angular-animate",
        underscore: "../lib/underscore/underscore",
        q: "../lib/q/q",
        modernizr: "../lib2/modernizr/modernizr-2.8.3.min"
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
