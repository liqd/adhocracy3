var common = require("./protractorCommon.js");

var local = {
    capabilities: {
        browserName: "chrome"
    }
};

exports.config = Object.assign({}, common.config, local);
