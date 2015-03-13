"use strict";

var UserPages = require("./UserPages.js");
var MailParser = require("mailparser").MailParser;
var fs = require("fs");

var restUrl = "http://localhost:9080/";


var hasClass = function (element, cls) {
    return element.getAttribute("class").then(function (classes) {
        return classes.split(" ").indexOf(cls) !== -1;
    });
};

var parseEmail = function(filename, callback) {
    var mailparser = new MailParser();

    mailparser.on("end", callback);
    mailparser.write(fs.readFileSync(filename));
    mailparser.end();
};

module.exports = {
    restUrl: restUrl,
    register: UserPages.register,
    login: UserPages.login,
    logout: UserPages.logout,
    isLoggedIn: UserPages.isLoggedIn,
    loginAnnotator: UserPages.loginAnnotator,
    annotatorName: UserPages.annotatorName,
    loginContributor: UserPages.loginContributor,
    hasClass: hasClass,
    parseEmail: parseEmail
}
