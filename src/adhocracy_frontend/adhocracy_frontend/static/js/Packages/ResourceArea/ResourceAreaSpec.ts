/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import * as q from "q";

import * as AdhResourceArea from "./ResourceArea";


export var register = () => {
    describe("ResourceArea", () => {
        describe("Service", () => {
            var providerMock;
            var adhHttpMock;
            var adhConfigMock;
            var adhCredentialsMock;
            var adhEmbedMock;
            var $injectorMock;
            var $locationMock;
            var adhResourceUrlFilterMock;
            var service;

            beforeEach(() => {
                providerMock = {
                    defaults: {},
                    specifics: {},
                    templates: {},
                    customHeaders: {},
                };

                adhHttpMock = jasmine.createSpyObj("adhHttp", ["get", "withTransaction"]);
                adhHttpMock.get.and.returnValue(q.when({
                    content_type: "content_type",
                    data: {}
                }));
                adhHttpMock.withTransaction.and.returnValue(q.when([]));

                $injectorMock = jasmine.createSpyObj("$injector", ["invoke"]);

                $locationMock = jasmine.createSpyObj("$location", ["path"]);

                adhConfigMock = {
                    rest_url: "rest_url"
                };

                adhCredentialsMock = jasmine.createSpyObj("adhCredentialsMock", ["loggedIn"]);

                adhEmbedMock = jasmine.createSpyObj("adhEmbed", ["getContext"]);
                adhEmbedMock.getContext.and.returnValue("");

                adhResourceUrlFilterMock = (path) => path;

                service = new AdhResourceArea.Service(
                    providerMock,
                    <any>q,
                    $injectorMock,
                    $locationMock,
                    adhHttpMock,
                    adhConfigMock,
                    adhCredentialsMock,
                    adhEmbedMock, adhResourceUrlFilterMock
                );
            });

            describe("route", () => {
                beforeEach(() => {
                    spyOn(service, "getProcess").and.returnValue(q.when(""));
                    spyOn(service, "conditionallyRedirectVersionToLast").and.returnValue(q.when(false));
                });

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
                        expect(data["resourceUrl"]).toBe("rest_url/platform/wlog/");
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
