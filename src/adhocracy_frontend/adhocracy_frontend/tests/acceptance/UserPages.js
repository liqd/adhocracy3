"use strict";

var shared = require("./shared.js");

var annotatorName = "annotator";
var annotatorEmail = "annotator@example.org";
var annotatorPassword = "password";

var contributorName = "contributor";
var contributorPassword = "password";


var LoginPage = function() {
    this.loginInput = element(by.model("credentials.nameOrEmail"));
    this.passwordInput = element(by.model("credentials.password"));
    this.submitButton = element(by.css(".login [type=\"submit\"]"));

    this.get = function() {
        browser.get("/login");
        return this;
    };

    this.login = function(login, password) {
        this.loginInput.sendKeys(login);
        this.passwordInput.sendKeys(password);
        this.submitButton.click();
        browser.waitForAngular();
    };
};


var RegisterPage = function() {
    this.nameInput = element(by.model("input.username"));
    this.emailInput = element(by.model("input.email"));
    this.passwordInput = element(by.model("input.password"));
    this.passwordRepeatInput = element(by.model("input.passwordRepeat"));
    this.registerCheck = element(by.model("input.registerCheck"));
    this.submitButton = element(by.css("[type=\"submit\"]"));

    this.get = function() {
        browser.get("/register");
        return this;
    };

    this.fill = function(username, email, password, password_repeat) {
        this.nameInput.sendKeys(username);
        this.emailInput.sendKeys(email);
        this.passwordInput.sendKeys(password);
        this.passwordRepeatInput.sendKeys(password_repeat);
        this.registerCheck.click();
    };

    this.register = function(username, email, password) {
        this.fill(username, email, password, password);
        this.submitButton.click();
        browser.waitForAngular();
    };
};

var register = function(username, email, password) {
    var registerPage = new RegisterPage().get();
    registerPage.register(username, email, password);
};

var login = function(username, password) {
    var loginPage = new LoginPage().get();
    loginPage.login(username, password);
};

var isLoggedIn = function() {
    return element(by.css(".user-indicator-logout")).isPresent();
}

var logout = function() {
    var link = element(by.css(".user-indicator-logout"));
    link.isPresent().then(function(present) {
        if (present) {
            link.click();
        }
    });

    browser.waitForAngular();
};

var loginAnnotator = function() {
    login(annotatorName, annotatorPassword);
};

var loginContributor = function() {
    login(contributorName, contributorPassword);
};


module.exports = {
    register: register,
    LoginPage: LoginPage,
    RegisterPage: RegisterPage,
    login: login,
    logout: logout,
    isLoggedIn: isLoggedIn,
    annotatorName: annotatorName,
    annotatorEmail: annotatorEmail,
    annotatorPassword: annotatorPassword,
    loginAnnotator: loginAnnotator,
    loginContributor: loginContributor
}
