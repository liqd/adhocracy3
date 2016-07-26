"use strict";

var EmbeddedCommentsPage = require("./core/EmbeddedCommentsPage.js");
var MercatorProposalFormPage = require("./Mercator2015ProposalFormPage.js");

var MercatorProposalDetailPage = function() {
    this.coverCommentsButton = element(by.css(".mercator-proposal-cover-show-comments"));
    this.editButton = element(by.cssContainingText("a", "edit"));
    this.rateWidget = element(by.css(".meta-list-item-rate"));
    this.rateDifference = this.rateWidget.element(by.css(".like-difference"));
    this.detailContainer = element(by.css("adh-mercator-2015-proposal-detail-view .jump-navigation-wrapper"));
    this.proposalDetails = this.detailContainer.all(by.css(".chapter")).get(2);
    this.goalsAndVision = this.detailContainer.all(by.css(".chapter")).get(3);
    this.title = element.all(by.css("adh-mercator-2015-proposal-detail-view .section-jump-cover-header")).get(1);
    this.teaser = this.detailContainer.all(by.css(".chapter section p")).first();
    this.requestedFunding = this.detailContainer.element(by.css(".mercator-proposal-budget-col.requested"));
    this.budget = this.detailContainer.all(by.css(".mercator-proposal-budget-col")).get(1);
    this.locationSpecific1 = this.detailContainer.all(by.css(".mercator-proposal-budget-row .badge")).first();
    this.locationSpecific2 = this.detailContainer.all(by.css(".mercator-proposal-budget-row .badge")).get(1);
    this.userInfo = this.detailContainer.element(by.css("adh-user-meta"));
    this.organizationName = this.detailContainer.all(by.css(".mercator-proposal-detail-orgs-columns li")).first();
    this.organizationCountry = this.detailContainer.all(by.css(".mercator-proposal-detail-orgs-columns li")).get(1);
    this.organizationNonProfit = this.detailContainer.all(by.css(".mercator-proposal-detail-orgs-columns li")).last();
    this.description = this.proposalDetails.all(by.css("section p")).first();
    this.story = this.proposalDetails.all(by.css("section p")).last();
    this.outcome = this.goalsAndVision.all(by.css("section p")).first();
    this.steps = this.goalsAndVision.all(by.css("section p")).get(1);
    this.addedValue = this.goalsAndVision.all(by.css("section p")).get(2);
    this.partners = this.goalsAndVision.all(by.css("section p")).last();
    this.experience = this.detailContainer.all(by.css("#mercator-detail-view-additional p")).get(0);

    this.getEditPage = function() {
        this.editButton.click();
        return new MercatorProposalFormPage();
    };

    this.getCommentPage = function(section) {
        var path = "//a[contains(@href, '@comments:" + section + "')]";
        var bubbleButton = element(by.xpath(path));
        bubbleButton.click();
        return new EmbeddedCommentsPage("");
    };

    this.sendAbuseComplaint = function(content) {
        var reportButton = element(by.xpath("//a[text() = \"report\"]"));
        reportButton.click();
        element(by.css(".report-abuse textarea")).sendKeys(content);
        element(by.css(".report-abuse input.button-cta")).click();
    };

};

module.exports = MercatorProposalDetailPage;