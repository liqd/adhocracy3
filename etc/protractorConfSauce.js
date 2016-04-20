var pr = process.env.TRAVIS_PULL_REQUEST;
var souceUser = process.env.SAUCE_USERNAME || "liqd";
var sauceKey = process.env.SAUCE_ACCESS_KEY;
var name = ((pr === "false") ? "" : "#" + pr + " ") + process.env.TRAVIS_COMMIT;

var common = require("./protractorCommon.js");

var local = {
    sauceUser: souceUser,
    sauceKey: sauceKey,

    capabilities: {
        "browserName": "chrome",
        "tunnel-identifier": process.env.TRAVIS_JOB_NUMBER,
        "build": process.env.TRAVIS_BUILD_NUMBER,
        "name": name
    },
    allScriptsTimeout: 21000,
    getPageTimeout: 20000,
    jasmineNodeOpts: {
        showColors: true,
        defaultTimeoutInterval: 120000,
        isVerbose: true,
        includeStackTrace: true
    }
};

exports.config = Object.assign({}, common.config, local);
