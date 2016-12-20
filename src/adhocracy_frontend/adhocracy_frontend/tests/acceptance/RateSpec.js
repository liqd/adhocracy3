"use strict";

var shared = require("./shared.js");
var EmbeddedCommentsPage = require("./EmbeddedCommentsPage.js");


describe("ratings", function() {
    var page;

    beforeAll(function() {
        shared.loginParticipant();
    });

    beforeEach(function() {
        page = new EmbeddedCommentsPage("c1").get();
    });

    it("can upvote", function() {
        var comment = page.createComment("c1");
        var rate = page.getRateWidget(comment);
        rate.element(by.css(".rate-pro")).click();
        expect(rate.element(by.css(".rate-pro")).getText()).toEqual("1");
        expect(rate.element(by.css(".rate-contra")).getText()).toEqual("0");
    });

    it("can downvote", function() {
        var comment = page.createComment("c2");
        var rate = page.getRateWidget(comment);
        rate.element(by.css(".rate-contra")).click();
        expect(rate.element(by.css(".rate-pro")).getText()).toEqual("0");
        expect(rate.element(by.css(".rate-contra")).getText()).toEqual("1");
    });

    it("can remove vote", function() {
        var comment = page.createComment("c3");
        var rate = page.getRateWidget(comment);
        rate.element(by.css(".rate-pro")).click();
        expect(rate.element(by.css(".rate-pro")).getText()).toEqual("1");
        rate.element(by.css(".rate-pro")).click();
        expect(rate.element(by.css(".rate-pro")).getText()).toEqual("0");
    });

    it("can change vote by clicking on the other button", function() {
        var comment = page.createComment("c3");
        var rate = page.getRateWidget(comment);
        rate.element(by.css(".rate-pro")).click();
        expect(rate.element(by.css(".rate-pro")).getText()).toEqual("1");
        expect(rate.element(by.css(".rate-contra")).getText()).toEqual("0");
        rate.element(by.css(".rate-contra")).click();
        expect(rate.element(by.css(".rate-pro")).getText()).toEqual("0");
        expect(rate.element(by.css(".rate-contra")).getText()).toEqual("1");
    });

    xit("is not affected by the edition of the comment", function() {
        var page = new EmbeddedCommentsPage("c2").get();
        var comment = page.createComment("c4");
        var rate = page.getRateWidget(comment);

        rate.element(by.css(".rate-pro")).click();

        var changedComment = page.editComment(comment, ["c4 - edited"]);
        var rate2 = page.getRateWidget(changedComment);
        expect(rate.element(by.css(".rate-pro")).getText()).toEqual("1");
    });
});
