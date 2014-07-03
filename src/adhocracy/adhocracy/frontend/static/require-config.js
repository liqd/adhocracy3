require.config({
    baseUrl: '/frontend_static/js/',
    paths: {
        text: '../lib/requirejs-text/text',
        jquery: '../lib/jquery/jquery',
        angular: '../lib/angular/angular',
        underscore: '../lib/underscore/underscore',
        q: '../lib/q/q'
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
    }
});
