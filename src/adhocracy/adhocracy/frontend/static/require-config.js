require.config({
    baseUrl: '/frontend_static/js/',
    paths: {
        jquery: '../lib/jquery/jquery',
        angular: '../lib/angular/angular',
        underscore: '../lib/underscore/underscore'
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
