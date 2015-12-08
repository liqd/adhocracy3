"use strict";

var path = require("path");

var shared = require("./core/shared.js");


var MercatorProposalFormPage = function() {

    this.form = element(by.css("adh-mercator-2016-proposal-create form"));
    this.userInfoFirstName = this.form.element(by.model("data.user_info.first_name"));
    this.userInfoLastName = this.form.element(by.model("data.user_info.last_name"));

    // NOTE: Due to angular magic used in ng-options, the value which is
    // stored in the respective ng-model (e.g. 'DE') isn't reflected in the
    // DOM, and an index is used instead.
    this.organizationInfoStatusEnum1 = this.form.element(by.css("input[value=registered_nonprofit]"));
    this.organizationInfoStatusEnum2 = this.form.element(by.css("input[value=planned_nonprofit]"));
    this.organizationInfoStatusEnum3 = this.form.element(by.css("input[value=support_needed]"));
    this.organizationInfoStatusEnum4 = this.form.element(by.css("input[name=organization-info-status-enum][value=other]"));
    this.organizationInfoName = this.form.element(by.model("data.organization_info.name"));
    this.organizationInfoCountry = this.form.element(by.model("data.organization_info.country"));
    this.organizationInfoCity = this.form.element(by.model("data.organization_info.city"));
    this.organizationInfoWebsite = this.form.element(by.model("data.organization_info.website"));
    this.organizationInfoEmail = this.form.element(by.model("data.organization_info.email"));
    this.organizationInfoDate = this.form.element(by.model("data.organization_info.date_of_registration"));
    this.organizationInfoDateForseen = this.form.element(by.model("data.organization_info.date_of_foreseen_registration"));
    this.organizationOther = this.form.element(by.model("data.organization_info.status_other"));
    this.organizationHelp = this.form.element(by.model("data.organization_info.how_can_we_help_you"));

    this.title = this.form.element(by.model("data.title"));
    this.introductionTeaser = this.form.element(by.model("data.introduction.teaser"));
    this.image = this.form.element(by.css("input[type=\"file\"]"));
    this.partners = this.form.element(by.model("data.partners"));
    this.topic1 = this.form.element(by.css("[name=introduction-topic-democracy]"));
    this.topic2 = this.form.element(by.css("[name=introduction-topic-culture]"));
    this.topic3 = this.form.element(by.css("[name=introduction-topic-environment]"));
    this.duration = this.form.element(by.model("data.duration"));
    this.locationLocationIsSpecific = this.form.element(by.model("data.location.location_is_specific"));
    this.locationLocationSpecific1 = this.form.element(by.model("data.location.location_specific_1"));
    this.status = this.form.all(by.model("data.status")).first();
    this.impactChallenge = this.form.element(by.model("data.impact.challenge"));
    this.impactAim = this.form.element(by.model("data.impact.aim"));
    this.impactPlan = this.form.element(by.model("data.impact.plan"));
    this.impactTarget = this.form.element(by.model("data.impact.targetgroup"));
    this.impactTeam = this.form.element(by.model("data.impact.team"));
    this.impactElse = this.form.element(by.model("data.impact.whatelse"));
    this.strengthen = this.form.element(by.model("data.strengthen"));
    this.different = this.form.element(by.model("data.different"));
    this.practical = this.form.element(by.model("data.practical"));
    this.financeBudget = this.form.element(by.model("data.finance.budget"));
    this.financeRequestedFunding = this.form.element(by.model("data.finance.requested_funding"));
    this.major = this.form.element(by.model("data.major"));
    this.personalContact = this.form.element(by.model("data.heard_from.personal_contact"));
    this.accept = this.form.element(by.model("data.accept_disclaimer"));

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
        this.introductionTeaser.sendKeys("proteaser");
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
