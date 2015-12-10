"use strict";

var fs = require("fs");
var shared = require("./core/shared.js");
var _ = require("lodash");
var ProposalPage = require("./MeinberlinBplanProposalPage.js");

describe("meinberlin bplan proposal form", function() {
    it("can be submitted and mails are received", function() {

        var mailsBeforeMessaging =
            fs.readdirSync(browser.params.mail.queue_path + "/new");
        var currentDate = Date.now().toString();
        var statement = "statement" + currentDate;
        var subject = "Ihre Stellungnahme zum Bebauungsplan";
        var godMail = "sysadmin@test.de";
        var fromMail = "noreply@mein.berlin.de"
        var participant = ProposalPage.participantValid1;
        var done = false;
        var prevMailTo = "";

        // submit proposal
        participant.statement = statement;
        ProposalPage.submitProposal(participant);
        browser.waitForAngular();
        expect(ProposalPage.isSuccessful()).toBe(true);

        // Check confirmation mails
        var flow = browser.controlFlow();
        flow.execute(function() {
            var mailsAfterMessaging =
                fs.readdirSync(browser.params.mail.queue_path + "/new");
            var newMails = _.difference(mailsAfterMessaging, mailsBeforeMessaging);
            expect(newMails.length).toEqual(2);

            var mailpath = browser.params.mail.queue_path + "/new/" + newMails[0];
            shared.parseEmail(mailpath, function(mail) {
                expect(mail.text).toContain(statement);
                expect(mail.text).toContain(participant.name);
                expect(mail.text).toContain(participant.street);
                expect(mail.text).toContain(participant.city);
                expect(mail.subject).toContain(subject);
                expect(mail.from[0].address).toEqual(fromMail);
                expect((mail.to[0].address == participant.email ||
                        mail.to[0].address == godMail) &&
                        mail.to[0].address != prevMailTo).toBe(true);
                prevMailTo = mail.to[0].address;
                done = true;
            });

            mailpath = browser.params.mail.queue_path + "/new/" + newMails[1];
            shared.parseEmail(mailpath, function(mail) {
                expect(mail.text).toContain(statement);
                expect(mail.text).toContain(participant.name);
                expect(mail.text).toContain(participant.street);
                expect(mail.text).toContain(participant.city);
                expect(mail.subject).toContain(subject);
                expect(mail.from[0].address).toEqual(fromMail);
                expect((mail.to[0].address == participant.email ||
                        mail.to[0].address == godMail) &&
                        mail.to[0].address != prevMailTo).toBe(true);
                prevMailTo = mail.to[0].address;
                done = true;
            });
        });

        // Keep browser active until mail assertions are done.
        browser.driver.wait(function() {
            return done == true;
        }, 1000)
    });
});
