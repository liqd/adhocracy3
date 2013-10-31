require.config({
    baseUrl: './js/',
    paths: {
        jquery: '../jquery-1.7.2',  // FIXME: ../submodules/jquery/dist/...
        datalink: '../submodules/jquery-datalink/jquery.datalink',
        bbq: '../submodules/jquery-bbq/jquery.ba-bbq',
        obviel: '../submodules/obviel/src/obviel/obviel',
        obvieltemplate: '../submodules/obviel/src/obviel/obviel-template',
        chai: '../submodules/chai/chai',
        mocha: '../submodules/mocha/mocha',
    },
    shim: {
        jquery: {
        },
        datalink: {
            deps: ['jquery'],
        },
        bbq: {
            deps: ['jquery'],
        },
        obviel: {
            exports: 'obviel',
            deps: ['jquery', 'obvieltemplate'],
        },
        obvieltemplate: {
            exports: 'obvieltemplate',
            deps: ['jquery'],
        },
        mocha: {
            exports: 'mocha',
        },
    }
});

// require(['jquery'], function($) {});
