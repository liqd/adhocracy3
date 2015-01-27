/// <reference path="src/mercator/build/lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="src/mercator/build/lib/DefinitelyTyped/angular-protractor/angular-protractor.d.ts"/>


// porting a3 comment tests from splinter to protractor


"use strict";

var shared = require("./shared.js");


var EmbeddedCommentsPage = function(referer) {
    this.referer = referer;
    this.poolPath = shared.restUrl + 'adhocracy/';
    this.url = "/embed/create-or-show-comment-listing"
        + "?key=" + referer + "&pool-path=" + this.poolPath;

    this.listing = element(by.css(".listing"));
    this.listingCreateForm = this.listing.element(by.css(".listing-create-form"));
    this.commentInput = this.listingCreateForm.element(by.model("data.content"));
    this.submitButton = this.listingCreateForm.element(by.css("input[type=\"submit\"]"));

    this.get = function() {
        browser.get(this.url);
    };

    this.createComment = function(comment) {
        this.commentInput.sendKeys(comment);
        this.submitButton.click();
        return this.listing.element(by.css('.comment'));
    };

    this.createReply = function(parent, content) {
        parent.element(by.css(".icon-reply")).click();
        parent.element(by.model("data.content")).sendKeys(content);
        parent.element(by.css("input[type=\"submit\"]")).click();
        return parent.element(by.css('.comment'));
    };
};

describe("adhocracy root page", function() {
    it("should have a title", function() {
        browser.get('/');
        expect(browser.getTitle()).toEqual("adhocracy root page");
    });
});

describe("comments", function() {
    it("can be created", function() {
        shared.loginAnnotator();
        var page = new EmbeddedCommentsPage("c1");
        page.get();
        var comment = page.createComment("comment 1");
        expect(comment.isPresent()).toBe(true);
        expect(comment.element(by.css(".comment-content")).getText()).toEqual("comment 1");
    });

    it("cannot be created empty", function() {
        shared.loginAnnotator();
        var page = new EmbeddedCommentsPage("c2");
        page.get();
        var comment = page.createComment("");
        expect(comment.isPresent()).toBe(false);
    });

    it("can be created nested", function() {
        shared.loginAnnotator();
        var page = new EmbeddedCommentsPage("c3");
        page.get();
        var comment = page.createComment("comment 3");

        var createNestedReplies = function(parent, parentName, remaining) {
            var name = parentName + ".1";
            var reply = page.createReply(parent, name);
            expect(reply.isPresent()).toBe(true);
            expect(reply.element(by.css(".comment-content")).getText()).toEqual(name);
            if (remaining > 0) {
                createNestedReplies(reply, name, remaining - 1);
            }
        };

        createNestedReplies(comment, "reply 3", 3);
    });
});
