"use strict";

var EmbeddedCommentsPage = require("./core/EmbeddedCommentsPage.js");

var MercatorProposalDetailPage = function() {
    this.column = element(by.tagName("adh-mercator-proposal-detail-column"));
    this.coverCommentsButton = element(by.css('.mercator-proposal-cover-show-comments'));
    this.editButton = this.column.element(by.cssContainingText("a", "edit"));
    this.rateWidget = element(by.css(".mercator-proposal-detail-view .mercator-propsal-detail-meta-item-rate"));
    this.rateDifference = this.rateWidget.element(by.css(".like-difference"));
    this.detailContainer = element(by.css("adh-mercator-proposal-detail-view .mercator-proposal-detail-container"));
    this.proposalDetails = this.detailContainer.all(by.css(".chapter")).get(2);
    this.goalsAndVision = this.detailContainer.all(by.css(".chapter")).get(3);
    
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

    this.getTitleText = function() {
        return element(by.css("adh-mercator-proposal-detail-view .mercator-proposal-cover-header"))
               .getText();
    };

    this.getTeaserText = function() {
        return this.detailContainer.all(by.css(".chapter section p")).first()
               .getText();
    };

    this.getRequestedFundingText = function() {
        return this.detailContainer.element(by.css(".mercator-proposal-budget-col.requested"))
               .getText();
    };

    this.getBudgetText = function() {
        return this.detailContainer.all(by.css(".mercator-proposal-budget-col")).get(1)
               .getText();
    };

    this.getLocationSpecific1Text = function() {
        return this.detailContainer.all(by.css(".inline-boxes li")).first()
               .getText();
    };

    this.getLocationSpecific2Text = function() {
        return this.detailContainer.all(by.css(".inline-boxes li")).get(1)
               .getText();
    };

    this.getUserInfoText = function() {
        return this.detailContainer.element(by.css("adh-user-meta"))
               .getText();
    };

    this.getOrganizationNameText = function() {
        return this.detailContainer.all(by.css(".mercator-proposal-detail-orgs-columns li")).first()
               .getText();
    };

    this.getOrganizationCountryText = function() {
        return this.detailContainer.all(by.css(".mercator-proposal-detail-orgs-columns li")).get(1)
               .getText();
    };

    this.getOrganizationNonProfitText = function() {
        return this.detailContainer.all(by.css(".mercator-proposal-detail-orgs-columns li")).last()
               .getText();
    };

    this.getDescriptionText = function() {
        return this.proposalDetails.all(by.css("section p")).first()
               .getText();
    };

    this.getStoryText = function() {
        return this.proposalDetails.all(by.css("section p")).last()
               .getText();
    };

    this.getOutcomeText = function() {
        return this.goalsAndVision.all(by.css("section p")).first()
               .getText();
    };

    this.getStepsText = function() {
        return this.goalsAndVision.all(by.css("section p")).get(1)
               .getText();
    };

    this.getAddedValueText = function() {
        return this.goalsAndVision.all(by.css("section p")).get(2)
               .getText();
    };

    this.getPartnersText = function() {
        return this.goalsAndVision.all(by.css("section p")).last()
               .getText();
    };

    this.getExperienceText = function() {
        return this.detailContainer.element(by.css("#mercator-detail-view-additional p"))
               .getText();
    };
};

module.exports = MercatorProposalDetailPage;