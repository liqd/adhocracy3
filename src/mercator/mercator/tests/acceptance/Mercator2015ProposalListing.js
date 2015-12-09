"use strict";

var path = require("path");

var shared = require("./core/shared.js");
var MercatorProposalFormPage = require("./Mercator2015ProposalFormPage.js");
var EmbeddedCommentsPage = require("./core/EmbeddedCommentsPage.js");
var MercatorProposalDetailPage = require("./Mercator2015ProposalDetailPage.js");

var MercatorProposalListing = function() {
    this.listing = element(by.tagName("adh-mercator-2015-proposal-listing"));

    this.get = function() {
        browser.get("/r/mercator/");
        return this;
    };

    this.selectProposal = function(idx) {
        var item = this.listing.all(by.tagName("adh-mercator-2015-proposal")).get(idx).element(by.tagName("a"));
        item.click();
    };

    this.getDetailPage = function(idx) {
        this.selectProposal(idx);
        return new MercatorProposalDetailPage();
    };
};

module.exports = MercatorProposalListing