"use strict";

var path = require("path");

var shared = require("./core/shared.js");
var MercatorProposalFormPage = require("./MercatorProposalFormPage.js");


var MercatorProposalDetailPage = function() {
    this.column = element(by.tagName("adh-mercator-proposal-detail-column"));
    this.coverCommentsButton = element(by.css('.mercator-proposal-cover-show-comments'));
    this.editButton = this.column.element(by.cssContainingText("a", "edit"));

    this.getEditPage = function() {
        this.editButton.click();
        return new MercatorProposalFormPage();
    };
};

var MercatorProposalListing = function() {
    this.listing = element(by.tagName("adh-mercator-proposal-listing"));

    this.columns = element.all(by.tagName("adh-moving-column"));

    this.get = function() {
        browser.get("/r/mercator/");
        return this;
    };

    this.selectProposal = function(idx) {
        var item = this.listing.all(by.tagName("adh-mercator-proposal")).get(idx).element(by.tagName("a"));
        item.click();
    };

    this.getDetailPage = function(idx) {
        this.selectProposal(idx);
        return new MercatorProposalDetailPage();
    };
};

module.exports = MercatorProposalListing;
