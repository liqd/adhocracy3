require.config({
    baseUrl: '/frontend_static/js/',
    paths: {
        text: '../lib/requirejs-text/text',
        jquery: '../lib/jquery/jquery',
        angular: '../lib/angular/angular',
        angularRoute: '../lib/angular-route/angular-route',
        underscore: '../lib/underscore/underscore',
        q: '../lib/q/q',
        modernizr: '../lib2/modernizr/modernizr-2.8.3.min'
    },
    shim: {
        jquery: {
            exports: '$',
        },
        angular: {
            exports: 'angular',
        },
        underscore: {
            exports: '_',
        },
        modernizr: {
            exports: 'Modernizr'
        },
        angularRoute: {
            deps: ['angular']
        }
    }
});
