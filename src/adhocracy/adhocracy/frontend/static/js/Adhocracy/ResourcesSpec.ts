/// <reference path="../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../lib/DefinitelyTyped/q/Q.d.ts"/>

import Util = require("./Util");
import q = require("q");

import Resources = require("./Resources");

// FIXME: DefinitelyTyped is not yet compatible with jasmine 2.0.0
declare var beforeEach : (any) => void;


var createAdhHttpMock = () => {
    var mock = <any>jasmine.createSpyObj("adhHttpMock", ["get", "postToPool"]);
    mock.get.and.returnValue(Util.mkPromise(q, {}));
    mock.postToPool.and.returnValue(Util.mkPromise(q, {}));
    return mock;
};

export var register = () => {
    describe("Resources", () => {
        describe("Service", () => {
            var adhResources : Resources.Service;
            var adhHttpMock;

            beforeEach(() => {
                adhHttpMock = createAdhHttpMock();
                adhResources = new Resources.Service(adhHttpMock, q);
            });

            describe("postProposal", () => {
                var scope = {};

                beforeEach((done) => {
                    adhResources.postProposal("/path", "TestProposal", scope).then(done);
                });

                it("writes proposal into the scope", () => {
                    expect((<any>scope).proposal).toBeDefined();
                });
            });

            describe("postSection", () => {
                var scope = {};

                beforeEach((done) => {
                    adhResources.postSection("/path", "TestSection", scope).then(done);
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
                    adhResources.postParagraph("/path", "TestParagraph", scope).then(done);
                });

                it("writes paragraph into scope.paragraphs", () => {
                    expect((<any>scope).paragraphs.TestParagraph).toBeDefined();
                });
            });
        });
    });
};
