var exec = require("sync-exec");

exports.config = {
    suites: {
        core: "../src/adhocracy_frontend/adhocracy_frontend/tests/acceptance/*Spec.js",
        mercator: "../src/mercator/tests/acceptance/*Spec.js"
    },
    baseUrl: "http://localhost:9090",
    directConnect: true,
    capabilities: {
        "browserName": "chrome"
    },
    beforeLaunch: function() {
        exec("bin/supervisord");
        exec("bin/supervisorctl restart adhocracy_test:test_zeo test_backend_with_ws adhocracy_test:test_autobahn adhocracy_test:test_frontend");
    },
    afterLaunch: function() {
        exec("bin/supervisorctl stop adhocracy_test:test_zeo test_backend_with_ws adhocracy_test:test_autobahn adhocracy_test:test_frontend");
        exec("rm -rf var/test_zeodata/Data.fs* var/test_zeodata/blobs");
    },
    jasmineNodeOpts: {
        showColors: true,
        defaultTimeoutInterval: 30000,
        isVerbose: true,
        includeStackTrace: true
    }
}
