"use strict";

var UserPages = require("./UserPages.js");
var fs = require("fs");
var _ = require("lodash");
var shared = require("./shared");

/*describe("user registration", function() {
    xit("can register - broken due to issue #583 (duplicate tpc_begin)", function() {
        UserPages.register("u1", "u1@example.com", "password1");
        UserPages.logout();
        UserPages.login("u1", "password1");
        expect(UserPages.isLoggedIn()).toBe(true);
    });

    it("cannot register with wrong password repeat", function() {
        var page = new UserPages.RegisterPage().get();
        page.fill("u2", "u2@example.com", "password2", "password3");
        expect(page.submitButton.isEnabled()).toBe(false);
    });
});*/

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
        page.submitButton.click();
        expect(element(by.css(".form-error")).getText()).toContain("Short");
    });

    /*it("login is persistent", function() {
        UserPages.login(UserPages.participantName, UserPages.participantPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        browser.refresh();
        browser.waitForAngular();
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });*/
});

describe("user password reset", function() {
    it("email is sent to user", function() {
        var mailsBeforeMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");

        var page = new UserPages.ResetPasswordCreatePage().get();
        page.fill(UserPages.participantEmail);
        expect(element(by.css(".login-success")).getText()).toContain("SPAM");

        var flow = browser.controlFlow();
        flow.execute(function() {
            var mailsAfterMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
            expect(mailsAfterMessaging.length).toEqual(mailsBeforeMessaging.length + 1);
        });
    });

    it("error displayed if the email is not associated to an user", function() {
        var page = new UserPages.ResetPasswordCreatePage().get();
        page.fill("abc@xy.de");
        expect(element(by.css(".form-error")).getText()).toContain("No user");
    });

    it("recover access with the link contained in the email", function(){
        var mailsBeforeMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
        var page = new UserPages.ResetPasswordCreatePage().get();
        var resetUrl = "";

        page.fill(UserPages.participantEmail);

        var flow = browser.controlFlow();
        flow.execute(function() {
            var mailsAfterMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
            var newMails = _.difference(mailsAfterMessaging, mailsBeforeMessaging);
            var mailpath = browser.params.mail.queue_path + "/new/" + newMails[0];

            shared.parseEmail(mailpath, function(mail) {
                // console.log('email=', mail);
                expect(mail.subject).toContain("Passwor");
                expect(mail.to[0].address).toContain("participant");
                resetUrl = _.find(mail.text.split("\n"), function(line) {return _.startsWith(line, "http");});
            });
        });

        browser.driver.wait(function() {
            return resetUrl != "";
        }).then(function() {
            var resetPage = new UserPages.ResetPasswordPage().get(resetUrl);
            resetPage.fill('new password');

            // After changing the password the user is logged in
            //expect(UserPages.isLoggedIn()).toBe(true);

            // and can now login with the new password
            UserPages.logout();
            UserPages.login(UserPages.participantEmail, 'new password');
            expect(UserPages.isLoggedIn()).toBe(true);
        });
    });
});
