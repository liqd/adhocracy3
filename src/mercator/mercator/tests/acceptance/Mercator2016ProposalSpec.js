"use strict";

var fs = require("fs");
var EC = protractor.ExpectedConditions;
var shared = require("./core/shared.js");
var _ = require("lodash");
var MercatorProposalFormPage = require("./MercatorProposalFormPage2016.js");

describe("mercator proposal form", function() {

    it("is validated correctly", function() {
        //shared.loginParticipant();

        var page = new MercatorProposalFormPage().create();
        expect(page.isValid()).toBe(false);

        // make all good
        page.fillValid();
        expect(page.isValid()).toBe(true);

        // date only accepts yyyy
        page.organizationInfoDate.clear();
        page.organizationInfoDate.sendKeys("xyz");
        expect(page.isValid()).toBe(false);
        page.organizationInfoDate.clear();
        page.organizationInfoDate.sendKeys("000");

        // Check other org info fields
        page.organizationInfoStatusEnum2.click();
        page.organizationInfoCity.sendKeys("city");
        page.organizationInfoDate.sendKeys("12-1972");
        expect(page.isValid()).toBe(true);

        // website is optional
        page.organizationInfoWebsite.clear();
        expect(page.isValid()).toBe(true);

        page.organizationInfoStatusEnum3.click();
        page.organizationHelp.sendKeys("Help me please");
        expect(page.isValid()).toBe(true);

        page.organizationInfoStatusEnum4.click();
        page.organizationOther.sendKeys("Other");
        expect(page.isValid()).toBe(true);

        // image has min width
        page.setImage("./proposalImageTooSmall.png");
        expect(shared.hasClass(page.form, "ng-invalid-too-narrow"));
        expect(page.isValid()).toBe(false);
        page.setImage("./proposalImageValid.png");
        expect(page.isValid()).toBe(true);

        // No more than 2 topics
        page.topic3.click();
        expect(page.isValid()).toBe(false);

        // Must be at least 1 topics
        page.topic1.click();
        page.topic2.click();
        page.topic3.click();
        expect(page.isValid()).toBe(false);


        browser.pause();

    });
});
