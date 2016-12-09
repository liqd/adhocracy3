"use strict";

var shared = require("./shared.js");


var EmbeddedCommentsPage = function(referer) {
    this.referer = referer;
    this.poolPath = shared.restUrl + 'adhocracy/';
    this.url = "/embed/create-or-show-comment-listing"
        + "?key=" + referer + "&pool-path=" + this.poolPath;

    this.listing = element(by.tagName("adh-comment-listing"));
    this.firstComment = this.listing.all(by.tagName("adh-comment")).first();
    this.allComments = this.listing.all(by.tagName("adh-comment"));
    this.listingCreateForm = this.listing.element(by.css(".listing-create-form"));
    this.commentInput = this.listingCreateForm.element(by.model("data.content"));
    this.submitButton = this.listingCreateForm.element(by.css("input[type=\"submit\"]"));


    this.getUrl = function() {
        return browser.get(this.url);
    };

    this.get = function() {
        this.getUrl();
        return this;
    };

    this.fillComment = function(content) {
        browser.wait(this.listingCreateForm.isDisplayed());
        browser.wait(this.commentInput.isDisplayed());
        this.commentInput.sendKeys(content);
    };

    this.createComment = function(content) {
        this.fillComment(content);
        this.submitButton.click();
        var new_comment = element(by.cssContainingText('.comment-content', content));
        browser.wait(new_comment.isDisplayed());
        // FIXME: Return created comment
        return this.firstComment;
    };

     this.createEmptyComment = function() {
         this.submitButton.click();
     }

    this.getReplyLink = function(comment) {
        return comment.element(by.css(".icon-reply"));
    };

    this.getEditLink = function(comment) {
        return comment.element(by.xpath("(.//*[@data-ng-click=\"edit()\"])[1]"));
    };

    this.createReply = function(parent, content) {
        this.getReplyLink(parent).click();
        parent.element(by.model("data.content")).sendKeys(content);
        parent.element(by.css("input[type=\"submit\"]")).click();
        var new_comment = element(by.cssContainingText('.comment-content', content));
        browser.wait(new_comment.isDisplayed());
        return parent.all(by.css('.comment-children .comment')).first();
    };

    this.editComment = function(comment, keys) {
        this.getEditLink(comment).click();
        var textarea = comment.element(by.model("data.content"));
        textarea.sendKeys.apply(textarea, keys);
        var content = textarea.getAttribute('value');
        comment.element(by.css("input[type=\"submit\"]")).click();
        var edited_comment = element(by.cssContainingText('.comment-content', content));
        browser.wait(edited_comment.isDisplayed());
        return comment;
    };

    this.getCommentText = function(comment) {
        return comment.all(by.css(".comment-content")).first().getText();
    };

    this.getCommentAuthor = function(comment) {
        return comment.element(by.css("adh-user-meta span")).getText();
    };

    this.getRateWidget = function(comment) {
        return comment.element(by.tagName("adh-rate"));
    };
};

module.exports = EmbeddedCommentsPage;
