"use strict";

var shared = require("./shared.js");
var UserPages = require("./UserPages.js");

describe("user page", function() {
    it("displays the correct name for each user", function() {
        var usersListing = new UserPages.UsersListing();

        usersListing.get();
        var annotatorPage = usersListing.getUserPage("annotator");
        expect(annotatorPage.getUserName()).toBe("annotator");

        usersListing.get();
        var contributorPage = usersListing.getUserPage("contributor");
        expect(contributorPage.getUserName()).toBe("contributor");

        usersListing.get();
        var reviewerPage = usersListing.getUserPage("reviewer");
        expect(reviewerPage.getUserName()).toBe("reviewer");
    });

});