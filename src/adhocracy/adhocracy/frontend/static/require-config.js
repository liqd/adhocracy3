require.config({
    baseUrl: '/frontend_static/js/',
    paths: {
        jquery: '../jquery-1.7.2',
        angular: '../angular-1.2.16',
        underscore: '../underscore'
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
