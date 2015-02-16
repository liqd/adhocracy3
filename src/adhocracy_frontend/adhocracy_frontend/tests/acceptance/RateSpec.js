"use strict";

var shared = require("./shared.js");
var EmbeddedCommentsPage = require("./EmbeddedCommentsPage.js");


describe("ratings", function() {
    var page;

    beforeEach(function() {
        shared.loginAnnotator();
        page = new EmbeddedCommentsPage("c1").get();
    });

    it("can upvote", function() {
        var comment = page.createComment("c1");
        var rate = page.getRateWidget(comment);
        rate.element(by.css(".rate-pro")).click();
        expect(rate.element(by.css(".rate-difference")).getText()).toEqual("+1");
    });

    it("can downvote", function() {
        var comment = page.createComment("c2");
        var rate = page.getRateWidget(comment);
        rate.element(by.css(".rate-contra")).click();
        expect(rate.element(by.css(".rate-difference")).getText()).toEqual("-1");
    });

    it("can vote neutrally", function() {
        var comment = page.createComment("c3");
        var rate = page.getRateWidget(comment);
        rate.element(by.css(".rate-pro")).click();
        expect(rate.element(by.css(".rate-difference")).getText()).toEqual("+1");
        rate.element(by.css(".is-rate-button-active")).click();
        expect(rate.element(by.css(".rate-difference")).getText()).toEqual("0");
    });
});
