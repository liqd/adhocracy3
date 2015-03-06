var exec = require("sync-exec");
var pr = process.env.TRAVIS_PULL_REQUEST;
var name = ((pr === "false") ? "" : "#" + pr + " ") + process.env.TRAVIS_COMMIT;

exports.config = {
    suites: {
        core: "../src/adhocracy_frontend/adhocracy_frontend/tests/acceptance/*Spec.js"
    },
    baseUrl: "http://localhost:9090",
    sauceUser: "liqd",
    sauceKey: "77600374-1617-4d7b-b1b6-9fd82ddfe89c",

    capabilities: {
        "browserName": "chrome",
        "version": "40",
        "tunnel-identifier": process.env.TRAVIS_JOB_NUMBER,
        "build": process.env.TRAVIS_BUILD_NUMBER,
        "name": name
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
        defaultTimeoutInterval: 120000,
        isVerbose: true,
        includeStackTrace: true
    }
}
