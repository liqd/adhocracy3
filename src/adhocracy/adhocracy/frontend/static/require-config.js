require.config({
    baseUrl: './js/',
    paths: {
        jquery: '../jquery-1.7.2',  // FIXME: ../submodules/jquery/dist/...
                                    // (we use this version because
                                    // obviel had someissue with a
                                    // more recent one a while ago.
                                    // nothing else is know about
                                    // this.)
        datalink: '../submodules/jquery-datalink/jquery.datalink',
        bbq: '../submodules/jquery-bbq/jquery.ba-bbq',
        obviel: '../submodules/obviel/src/obviel/obviel',
        obvieltemplate: '../submodules/obviel/src/obviel/obviel-template',
    },
    shim: {
        jquery: {
        },
        datalink: {  // this may be a dependency of some other package.  if not, remove!
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
    }
});

// require(['jquery'], function($) {});
