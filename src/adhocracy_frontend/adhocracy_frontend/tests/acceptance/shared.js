"use strict";

var UserPages = require("./UserPages.js");

var restUrl = "http://localhost:9080/";


var hasClass = function (element, cls) {
    return element.getAttribute("class").then(function (classes) {
        return classes.split(" ").indexOf(cls) !== -1;
    });
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
    hasClass: hasClass
}
