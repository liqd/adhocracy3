"use strict";

var UserPages = require("./UserPages.js");
var fs = require("fs");
var _ = require("lodash");
var shared = require("./shared");

describe("user registration", function() {
    it("can register", function() {
        var mailsBeforeMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
        browser.get("/");
        UserPages.ensureLogout();
        UserPages.register("u1", "u1@example.com", "password1");
        var flow = browser.controlFlow();
        flow.execute(function() {
            var mailsAfterMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
            expect(mailsAfterMessaging.length).toEqual(mailsBeforeMessaging.length + 1);
        });
    });

    it("cannot register with wrong password repeat", function() {
        browser.get("/");
        UserPages.ensureLogout();
        var page = new UserPages.RegisterPage().get();
        page.fill("u2", "u2@example.com", "password2", "password3");
        expect(page.submitButton.isEnabled()).toBe(false);
    });
});

describe("user login", function() {
    it("can login with username", function() {
        UserPages.login(UserPages.participantName, UserPages.participantPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });

    it("can login with email", function() {
        UserPages.login(UserPages.participantEmail, UserPages.participantPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });

    it("cannot login with wrong name", function() {
        UserPages.login("noexist", "password1");
        expect(UserPages.isLoggedIn()).toBe(false);
    });

    it("cannot login with wrong password", function() {
        UserPages.login("participant", "password1");
        expect(UserPages.isLoggedIn()).toBe(false);
    });

    it("cannot login with short password", function() {
        var page = new UserPages.LoginPage().get();
        page.loginInput.sendKeys("abc");
        page.passwordInput.sendKeys("abc");
        expect(page.submitButton.getAttribute("disabled")).toBe("true");
    });

    it("login is persistent", function() {
        UserPages.login(UserPages.participantName, UserPages.participantPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        browser.refresh();
        browser.waitForAngular();
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });
});

describe("user password reset", function() {
    it("email is sent to user", function() {
        var mailsBeforeMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");

        var page = new UserPages.ResetPasswordCreatePage().get();
        page.fill(UserPages.participantEmail);
        expect(element(by.css(".login-success")).getText()).toContain("Spam");

        var flow = browser.controlFlow();
        flow.execute(function() {
            var mailsAfterMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
            expect(mailsAfterMessaging.length).toEqual(mailsBeforeMessaging.length + 1);
        });
    });

    it("error displayed if the email is not associated to an user", function() {
        var page = new UserPages.ResetPasswordCreatePage().get();
        page.fill("abc@xy.de");
        browser.wait(browser.isElementPresent(element(by.css(".form-error"))), 1000)
        expect(element(by.css(".form-error")).getText()).toContain("No user");
    });

    it("recover access with the link contained in the email", function(){
        var mailsBeforeMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
        var page = new UserPages.ResetPasswordCreatePage().get();
        var resetUrl = "";

        page.fill(UserPages.participantEmail);

        expect(element(by.css(".login-success")).getText()).toContain("Spam");
        var flow = browser.controlFlow();
        flow.execute(function() {
            var mailsAfterMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
            expect(mailsAfterMessaging.length).toEqual(mailsBeforeMessaging.length + 1);
        });
    });
});
