"use strict";

var shared = require("./core/shared.js");

var participantValid1 = {
    name: "Participant1",
    street: "Street1",
    city: "City1",
    email: "participant1@example.com",
    statement: "",
};

var ProposalPage = function() {
    this.path = shared.restUrl + "organisation/bplan20";
    this.url = "/embed/mein-berlin-bplaene-proposal-embed?path=" + this.path;
    this.nameInput = element(by.model("data.name"));
    this.streetInput = element(by.model("data.street"));
    this.cityInput = element(by.model("data.city"));
    this.emailInput = element(by.model("data.email"));
    this.statementInput = element(by.model("data.statement"));
    this.submitButton = element(by.css("input[type=\"submit\"]"));

    this.get = function() {
        browser.get(this.url);
        return this;
    }

    this.submit = function(participant) {
        this.nameInput.sendKeys(participant.name);
        this.streetInput.sendKeys(participant.street);
        this.cityInput.sendKeys(participant.city);
        this.emailInput.sendKeys(participant.email);
        this.statementInput.sendKeys(participant.statement);
        this.submitButton.click();
    }
};

var submitProposal = function(participant) {
    var proposalPage = new ProposalPage().get();
    proposalPage.submit(participant);
}

var isSuccessful = function() {
    return element(by.css(".meinberlin-bplan-proposal-success.ng-scope")).isPresent();
}

module.exports = {
    submitProposal: submitProposal,
    participantValid1: participantValid1,
    isSuccessful: isSuccessful
}
