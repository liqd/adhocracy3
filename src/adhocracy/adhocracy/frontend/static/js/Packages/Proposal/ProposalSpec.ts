/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import q = require("q");

import AdhProposal = require("./Proposal");
import AdhPreliminaryNames = require("../../Packages/PreliminaryNames/PreliminaryNames");


var createAdhHttpMock = () => {
    var mock = <any>jasmine.createSpyObj("adhHttpMock", ["get", "postToPool"]);
    mock.get.and.returnValue(q.when({}));
    mock.postToPool.and.returnValue(q.when({}));
    return mock;
};


export var register = () => {
    describe("Proposal", () => {
        describe("Service", () => {
            var adhProposal : AdhProposal.Service;
            var adhHttpMock;

            beforeEach(() => {
                adhHttpMock = createAdhHttpMock();
                adhProposal = new AdhProposal.Service(adhHttpMock, new AdhPreliminaryNames(), q);
            });

            describe("postProposal", () => {
                var scope = {};

                beforeEach((done) => {
                    (<any>adhProposal).postProposal("/path", "TestProposal", scope).then(done);
                });

                it("writes proposal into the scope", () => {
                    expect((<any>scope).proposal).toBeDefined();
                });
            });

            describe("postSection", () => {
                var scope = {};

                beforeEach((done) => {
                    (<any>adhProposal).postSection("/path", "TestSection", scope).then(done);
                });

                it("writes section into the scope", () => {
                    expect((<any>scope).section).toBeDefined();
                });
            });

            describe("postParagraph", () => {
                var scope = {
                    paragraphs: {}
                };

                beforeEach((done) => {
                    (<any>adhProposal).postParagraph("/path", "TestParagraph", scope).then(done);
                });

                it("writes paragraph into scope.paragraphs", () => {
                    expect((<any>scope).paragraphs.TestParagraph).toBeDefined();
                });
            });
        });
    });
};
