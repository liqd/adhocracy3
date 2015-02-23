"use strict";

var shared = require("./core/shared.js");
var MercatorProposalFormPage = require("./MercatorProposalFormPage.js");
var MercatorProposalListing = require("./MercatorProposalListing.js");
var MercatorProposalDetailPage = require("./MercatorProposalDetailPage.js");

describe("mercator proposal form", function() {
    afterEach(function() {
        shared.logout();
    });

    it("is validated correctly", function() {
        shared.loginAnnotator();

        var page = new MercatorProposalFormPage().create();
        expect(page.isValid()).toBe(false);

        // make all good
        page.fillValid();
        expect(page.isValid()).toBe(true);

        // experience is optional
        page.experience.clear();
        expect(page.isValid()).toBe(true);

        // location is required
        page.locationLocationIsSpecific.click();
        page.locationLocationIsLinkedToRuhr.click();
        expect(page.isValid()).toBe(false);
        page.locationLocationIsLinkedToRuhr.click();
        expect(page.isValid()).toBe(true);

        // name is required
        page.userInfoFirstName.clear();
        expect(page.isValid()).toBe(false);
        page.userInfoFirstName.sendKeys("pizza");
        expect(page.isValid()).toBe(true);

        // heard_from is required
        page.heardFromColleague.click();
        expect(page.isValid()).toBe(false);
        page.heardFromColleague.click();
        expect(page.isValid()).toBe(true);

        // image has min width
        page.setImage("./proposalImageTooSmall.png");
        expect(shared.hasClass(page.form, "ng-invalid-too-narrow"));
        expect(page.isValid()).toBe(false);
        page.setImage("./proposalImageValid.png");
        expect(page.isValid()).toBe(true);
    });

    it("is submitted properly", function() {
        shared.loginAnnotator();

        var page = new MercatorProposalFormPage().create();
        page.fillValid();
        page.submitButton.click();
        expect(browser.getCurrentUrl()).not.toContain("@create");

        var detailPage = new MercatorProposalDetailPage();
        
        // proposal pitch
        expect(detailPage.getTitleText()).toContain("protitle");
        expect(detailPage.getTeaserText()).toBe("proteaser");
        expect(detailPage.getRequestedFundingText()).toContain("1,000");
        expect(detailPage.getBudgetText()).toContain("1,200");
        expect(detailPage.getLocationSpecific1Text()).toContain("Bonn");
        expect(detailPage.getLocationSpecific2Text()).toContain("Ruhr Gebiet, Germany");

        // proposal whos
        expect(detailPage.getUserInfoText()).toContain("pita pasta");
        expect(detailPage.getOrganizationNameText()).toContain("organization name");
        expect(detailPage.getOrganizationCountryText()).toContain("Chile");
        expect(detailPage.getOrganizationNonProfitText()).toContain("Non Profit");

        // proposal details
        expect(detailPage.getDescriptionText()).toBe("prodescription");
        expect(detailPage.getStoryText()).toBe("story");

        // proposal goals and vision
        expect(detailPage.getOutcomeText()).toBe("success");
        expect(detailPage.getStepsText()).toContain("plan");
        expect(detailPage.getAddedValueText()).toContain("relevance");
        expect(detailPage.getPartnersText()).toContain("partners");

        // proposal additional information
        expect(detailPage.getExperienceText()).toContain("experience");
    });

    xit("can be upvoted by the annotator", function() {
        shared.loginAnnotator();

        var list = new MercatorProposalListing().get();
        var page = list.getDetailPage(0);

        expect(page.rateDifference.getText()).toEqual("0");
        page.rateWidget.click();
        expect(page.rateDifference.getText()).toEqual("+1");
    });

    it("can be downvoted by the annotator", function() {
        shared.loginAnnotator();

        var list = new MercatorProposalListing().get();
        var page = list.getDetailPage(0);

        // annotator has upvoted once in the previous test
        expect(page.rateDifference.getText()).toEqual("+1");
        page.rateWidget.click();
        expect(page.rateDifference.getText()).toEqual("0");
    });

    it("can be upvoted and then downvoted by the annotator", function() {
        shared.loginAnnotator();

        var list = new MercatorProposalListing().get();
        var page = list.getDetailPage(0);

        expect(page.rateDifference.getText()).toEqual("0");
        page.rateWidget.click();
        expect(page.rateDifference.getText()).toEqual("+1");
        page.rateWidget.click();
    });

    it("can be upvoted by the contributor", function() {
        shared.loginContributor();

        var list = new MercatorProposalListing().get();
        var page = list.getDetailPage(0);

        expect(page.rateDifference.getText()).toEqual("0");
        page.rateWidget.click();
        expect(page.rateDifference.getText()).toEqual("+1");
    });

    it("can be downvoted by the contributor", function() {
        shared.loginContributor();

        var list = new MercatorProposalListing().get();
        var page = list.getDetailPage(0);

        // commentator has upvoted once in the previous test
        expect(page.rateDifference.getText()).toEqual("+1");
        page.rateWidget.click();
        expect(page.rateDifference.getText()).toEqual("0");
    });

    it("can be upvoted and then downvoted by the contributor", function() {
        shared.loginContributor();

        var list = new MercatorProposalListing().get();
        var page = list.getDetailPage(0);

        expect(page.rateDifference.getText()).toEqual("0");
        page.rateWidget.click();
        expect(page.rateDifference.getText()).toEqual("+1");
        page.rateWidget.click();
    });

    it("can not be rated by anonymous", function() {
        var list = new MercatorProposalListing().get();
        var page = list.getDetailPage(0);

        page.rateWidget.click();
        expect(browser.getCurrentUrl()).toContain("login");
    });

    it("allows creator to edit existing proposals (depends on submit) - fails due to #679", function() {
        shared.loginAnnotator();

        var list = new MercatorProposalListing().get();
        browser.waitForAngular();
        var form = list.getDetailPage(0).getEditPage();
        form.userInfoLastName.clear();
        expect(form.isValid()).toBe(false);
        form.userInfoLastName.sendKeys("rasta");

        form.acceptDisclaimer.click();
        form.submitButton.click();
        expect(browser.getCurrentUrl()).not.toContain("@edit");
        browser.waitForAngular();
        expect(element(by.tagName("adh-mercator-proposal-detail-view")).element(by.tagName("adh-user-meta")).getText()).toContain("pita rasta");
    });

    it("disallows anonymous to edit existing proposals (depends on submit)", function() {
        var list = new MercatorProposalListing().get();
        var editButton = list.getDetailPage(0).editButton;
        expect(editButton.isPresent()).toBe(false);
    });

    it("disallows other users to edit existing proposals (depends on submit)", function() {
        shared.loginContributor();
        var list = new MercatorProposalListing().get();
        var editButton = list.getDetailPage(0).editButton;
        expect(editButton.isPresent()).toBe(false);
    });
});

describe("column navigation (depends on created proposal)", function() {
    it("allows to navigate around", function() {
        var list = new MercatorProposalListing().get();

        var column1 = list.columns.get(0).element(by.css(".moving-column"));
        var column2 = list.columns.get(1).element(by.css(".moving-column"));
        var column3 = list.columns.get(2).element(by.css(".moving-column"));

        expect(shared.hasClass(column1, "is-show"));
        expect(shared.hasClass(column2, "is-hide"));
        expect(shared.hasClass(column3, "is-hide"));

        var proposal = list.getDetailPage(0);

        expect(shared.hasClass(column1, "is-show"));
        expect(shared.hasClass(column2, "is-show"));
        expect(shared.hasClass(column3, "is-hide"));

        expect(proposal.coverCommentsButton.isPresent()).toBe(true);
        proposal.coverCommentsButton.click();

        expect(shared.hasClass(column1, "is-collapse"));
        expect(shared.hasClass(column2, "is-show"));
        expect(shared.hasClass(column3, "is-show"));

        column3.all(by.css('.moving-column-menu-nav a')).last().click();

        expect(shared.hasClass(column1, "is-show"));
        expect(shared.hasClass(column2, "is-show"));
        expect(shared.hasClass(column3, "is-hide"));

        column2.all(by.css('.moving-column-menu-nav a')).last().click();

        expect(shared.hasClass(column1, "is-show"));
        expect(shared.hasClass(column2, "is-hide"));
        expect(shared.hasClass(column3, "is-hide"));
    });
});
