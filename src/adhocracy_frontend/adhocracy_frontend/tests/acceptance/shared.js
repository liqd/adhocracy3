"use strict";

var UserPages = require("./UserPages.js");
var MailParser = require("mailparser").MailParser;
var fs = require("fs");
var EC = protractor.ExpectedConditions;

var restUrl = "http://localhost:9080/api/";


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

var waitAndClick = function(element) {
    var isClickable = EC.elementToBeClickable(element);
    browser.wait(isClickable, 5000);
    element.click();
}

module.exports = {
    restUrl: restUrl,
    register: UserPages.register,
    login: UserPages.login,
    logout: UserPages.logout,
    isLoggedIn: UserPages.isLoggedIn,
    loginParticipant: UserPages.loginParticipant,
    participantName: UserPages.participantName,
    loginOtherParticipant: UserPages.loginOtherParticipant,
    hasClass: hasClass,
    parseEmail: parseEmail,
    waitAndClick: waitAndClick
}
