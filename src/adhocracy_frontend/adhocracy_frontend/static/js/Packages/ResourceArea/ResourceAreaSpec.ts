/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhResourceArea = require("./ResourceArea");


export var register = () => {
    describe("ResourceArea", () => {
        describe("Service", () => {
            var providerMock;
            var adhHttpMock;
            var adhConfigMock;
            var $injectorMock;
            var service;

            beforeEach(() => {
                providerMock = {
                    defaults: {},
                    specifics: {}
                };

                adhHttpMock = jasmine.createSpyObj("adhHttp", ["get"]);
                adhHttpMock.get.and.returnValue(q.when({
                    content_type: "content_type"
                }));

                $injectorMock = jasmine.createSpyObj("$injector", ["invoke"]);

                adhConfigMock = {
                    rest_url: "rest_url"
                };

                service = new AdhResourceArea.Service(providerMock, q, $injectorMock, adhHttpMock, adhConfigMock);
            });

            describe("route", () => {
                it("sets view field if specified", (done) => {
                    service.route("/platform/wlog/@blarg", {}).then((data) => {
                        expect(data["view"]).toBe("blarg");
                        done();
                    });
                    service.route("/platform/wlog/@blarg/", {}).then((data) => {
                        expect(data["view"]).toBe("blarg");
                        done();
                    });
                });

                it("does not set view field if not specified", (done) => {
                    service.route("/platform/blarg", {}).then((data) => {
                        expect(data["view"]).toBeFalsy();
                        done();
                    });
                    service.route("/platform/blarg/", {}).then((data) => {
                        expect(data["view"]).toBeFalsy();
                        done();
                    });
                });

                it("sets contentType", (done) => {
                    service.route("/platform/wlog/@blarg", {}).then((data) => {
                        expect(data["contentType"]).toBe("content_type");
                        done();
                    });
                });

                it("sets resourceUrl", (done) => {
                    service.route("/platform/wlog/@blarg", {}).then((data) => {
                        expect(data["resourceUrl"]).toBe("rest_url/platform/wlog");
                        done();
                    });
                });
            });

            describe("reverse", () => {
                it("renders view correctly if specified", () => {
                    var answer = service.reverse({ resourceUrl: "rest_url/platform/wlog", view: "blarg" });
                    expect(answer.path).toMatch(/\/@blarg$/);
                });

                it("uses resourceUrl for path, but without rest_url", () => {
                    var answer = service.reverse({ resourceUrl: "rest_url/platform/wlog" });
                    expect(answer.path).toBe("/platform/wlog/");
                });
            });
        });
    });
};
