"use strict";

var UserPages = require("./UserPages.js");


describe("user registration", function() {
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
});

describe("user login", function() {
    it("can login with username", function() {
        UserPages.login(UserPages.annotatorName, UserPages.annotatorPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });

    it("can login with email", function() {
        UserPages.login(UserPages.annotatorEmail, UserPages.annotatorPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });

    it("login is persistent", function() {
        UserPages.login(UserPages.annotatorName, UserPages.annotatorPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        browser.refresh()
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });

    it("cannot login with wrong name", function() {
        UserPages.login("noexist", "password1");
        expect(UserPages.isLoggedIn()).toBe(false);
    });

    it("cannot login with wrong password", function() {
        UserPages.login("annotator", "password1");
        expect(UserPages.isLoggedIn()).toBe(false);
    });

    it("cannot login with short password", function() {
        var page = new UserPages.LoginPage().get();
        page.loginInput.sendKeys("abc");
        page.passwordInput.sendKeys("abc");
        page.submitButton.click();
        expect(element(by.css(".form-error")).getText()).toContain("Short");
    });
});
