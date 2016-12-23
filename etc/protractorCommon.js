var exec = require("sync-exec");
var fs = require("fs");
var ini = require("ini");

exports.config = {
    getPageTimeout: 30000,
    directConnect: true,
    suites: {
        // FIXME: mercator tests fail on travis
        //current: "../src/current/current/tests/acceptance/*Spec.js",
        core: "../src/adhocracy_frontend/adhocracy_frontend/tests/acceptance/*Spec.js"
    },
    baseUrl: "http://localhost:9090",
    beforeLaunch: function() {
        exec("bin/supervisord");
        exec("bin/supervisorctl restart  adhocracy_test:");
        exec("bin/ad_fixtures -a etc/acceptance.ini ");
        exec("src/current/current/tests/acceptance/setup_tests.sh");
    },
    afterLaunch: function() {
        exec("bin/supervisorctl stop adhocracy_test:");
        exec("rm -rf var/db/test/Data.fs* var/db/test/blobs/* var/mail/new/* ");
    },
    onPrepare: function() {
        var getMailQueuePath = function() {
            return process.cwd() + "/var/mail";
        };

        browser.params.mail = {
            queue_path: getMailQueuePath()
        }

        // https://stackoverflow.com/questions/26584451/
        // Disable animations so e2e tests run more quickly
        var disableNgAnimate = function() {
          angular.module('disableNgAnimate', []).run(['$animate', function($animate) {
            $animate.enabled(false);
          }]);
        };

        browser.addMockModule('disableNgAnimate', disableNgAnimate);
    },
    jasmineNodeOpts: {
        showColors: true,
        defaultTimeoutInterval: 30000,
        isVerbose: true,
        includeStackTrace: true
    }
}
