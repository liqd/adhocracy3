"use strict";

var path = require("path");

var shared = require("./core/shared.js");


var MercatorProposalFormPage = function() {

    this.form = element(by.css("adh-mercator-2016-proposal-create form"));
    this.userInfoFirstName = this.form.element(by.model("data.userInfo.firstName"));
    this.userInfoLastName = this.form.element(by.model("data.userInfo.lastName"));

    // NOTE: Due to angular magic used in ng-options, the value which is
    // stored in the respective ng-model (e.g. 'DE') isn't reflected in the
    // DOM, and an index is used instead.
    this.organizationInfoStatusEnum1 = this.form.element(by.css("input[value=registered_nonprofit]"));
    this.organizationInfoStatusEnum2 = this.form.element(by.css("input[value=planned_nonprofit]"));
    this.organizationInfoStatusEnum3 = this.form.element(by.css("input[value=support_needed]"));
    this.organizationInfoStatusEnum4 = this.form.element(by.css("input[name=organization-info-status][value=other]"));
    this.organizationInfoName = this.form.element(by.model("data.organizationInfo.name"));
    this.organizationInfoCountry = this.form.element(by.model("data.organizationInfo.country"));
    this.organizationInfoCity = this.form.element(by.model("data.organizationInfo.city"));
    this.organizationInfoWebsite = this.form.element(by.model("data.organizationInfo.website"));
    this.organizationInfoEmail = this.form.element(by.model("data.organizationInfo.email"));
    this.organizationInfoDate = this.form.element(by.model("data.organizationInfo.registrationDate"));
    this.organizationOther = this.form.element(by.model("data.organizationInfo.otherText"));
    this.organizationHelp = this.form.element(by.model("data.organizationInfo.helpRequest"));

    this.title = this.form.element(by.model("data.title"));
    this.introductionPitch = this.form.element(by.model("data.introduction.pitch"));
    this.image = this.form.element(by.css("input[type=\"file\"]"));
    this.partners = this.form.element(by.model("data.partners.hasPartners"));
    this.topic1 = this.form.element(by.css("[name=introduction-topic-democracy]"));
    this.topic2 = this.form.element(by.css("[name=introduction-topic-culture]"));
    this.topic3 = this.form.element(by.css("[name=introduction-topic-environment]"));
    this.duration = this.form.element(by.model("data.duration"));
    this.locationLocationIsSpecific = this.form.element(by.model("data.location.location_is_specific"));
    this.locationLocationSpecific1 = this.form.element(by.model("data.location.location_specific_1"));
    this.status = this.form.all(by.model("data.status")).first();
    this.impactChallenge = this.form.element(by.model("data.impact.challenge"));
    this.impactAim = this.form.element(by.model("data.impact.goal"));
    this.impactPlan = this.form.element(by.model("data.impact.plan"));
    this.impactTarget = this.form.element(by.model("data.impact.target"));
    this.impactTeam = this.form.element(by.model("data.impact.team"));
    this.impactElse = this.form.element(by.model("data.impact.extraInfo"));
    this.strengthen = this.form.element(by.model("data.criteria.strengthen"));
    this.different = this.form.element(by.model("data.criteria.difference"));
    this.practical = this.form.element(by.model("data.criteria.practical"));
    this.financeBudget = this.form.element(by.model("data.finance.budget"));
    this.financeRequestedFunding = this.form.element(by.model("data.finance.requestedFunding"));
    this.major = this.form.element(by.model("data.finance.major"));
    this.personalContact = this.form.element(by.model("data.heardFrom.personal_contact"));
    this.accept = this.form.element(by.model("data.acceptDisclaimer"));

    this.submitButton = this.form.element(by.css("input[type=\"submit\"]"));

    this.setImage = function(filename) {
        var fileToUpload = filename;
        var imagePath = path.resolve(__dirname, fileToUpload);
        this.image.sendKeys(imagePath);
    };

    this.fillValid = function() {
        this.userInfoFirstName.sendKeys("pita");
        this.userInfoLastName.sendKeys("pasta");;
        this.organizationInfoStatusEnum1.click();
        this.organizationInfoName.sendKeys("organization name");
        this.organizationInfoCountry.element(by.cssContainingText("option", "France")).click();
        this.organizationInfoWebsite.sendKeys("http://example.org");
        this.organizationInfoEmail.sendKeys("test@hotmail.com");
        this.organizationInfoDate.sendKeys("1972");
        this.title.sendKeys("protitle");
        this.introductionPitch.sendKeys("proteaser");
        this.setImage("./proposalImageValid.png");
        this.partners.element(by.cssContainingText("option", "yes")).click();
        this.topic1.click();
        this.topic2.click();
        this.duration.sendKeys("20");
        this.locationLocationIsSpecific.click();
        this.locationLocationSpecific1.sendKeys("Bonn");
        this.status.click();
        this.impactChallenge.sendKeys("impact challenge");
        this.impactAim.sendKeys("impact aim");
        this.impactPlan.sendKeys("impact plan");
        this.impactTarget.sendKeys("impact target");
        this.impactTeam.sendKeys("impact team");
        this.impactElse.sendKeys("impact else");
        this.strengthen.sendKeys("strengthen");
        this.different.sendKeys("different");
        this.practical.sendKeys("practical");
        this.financeBudget.sendKeys("1200");
        this.financeRequestedFunding.sendKeys("1000");
        this.major.sendKeys("1000 EUR, travel and accommodation");
        this.personalContact.click();
        this.accept.click();
    };

    this.create = function() {
        browser.get("/embed/mercator-2016-proposal-create?nocenter&locale=en");
        return this;
    };

    this.createProposal = function(content) {
        this.fillValid();
        this.submitButton.click();
        // FIXME: Return created comment
        return this.listing.element(by.tagName("adh-comment"));

        /*
        return all.reduce(function(acc, elem) {
            return protractor.promise.all(
                acc.getAttribute("data-path"),
                elem.getAttribute("data-path")
            ).then(function(paths) {
                return (path[0] > path[1] ? acc : elem);
            })
        });*/
    };

    this.isValid = function() {
        return (shared.hasClass(this.form, "ng-valid"));
    }

    this.getEditLink = function(comment) {
        return comment.element(by.css("[data-ng-click=\"edit()\"]"));
    };
};

module.exports = MercatorProposalFormPage;
