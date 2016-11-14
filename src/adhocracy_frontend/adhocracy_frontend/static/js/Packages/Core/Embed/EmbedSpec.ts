/// <reference path="../../../../lib2/types/jasmine.d.ts"/>

import * as AdhEmbed from "./Embed";

export var register = () => {
    describe("Embed", () => {
        var $locationMock;
        var $compileMock;
        var adhConfigMock;

        beforeEach(() => {
            $locationMock = jasmine.createSpyObj("$location", ["path", "search", "host", "port", "protocol"]);
            $locationMock.host.and.returnValue("example.com");
            $locationMock.port.and.returnValue("");
            $locationMock.protocol.and.returnValue("http");
            $locationMock.path.and.returnValue("/embed/document-workbench");
            $locationMock.search.and.returnValue({
            });
            $compileMock = jasmine.createSpy("$compileMock")
                .and.returnValue(() => undefined);
            adhConfigMock = {
                pkg_path: ""
            };
        });

        describe("Provider", () => {
            var provider;

            beforeEach(() => {
                provider = new AdhEmbed.Provider();
            });

            describe("normalizeDirective", () => {
                it("returns the original name", () => {
                    provider.registerDirective("name1");
                    expect(provider.normalizeDirective("name1")).toBe("name1");

                    provider.registerDirective("name2", ["alias1", "alias2"]);
                    expect(provider.normalizeDirective("name2")).toBe("name2");
                });
                it("resolves directive aliases", () => {
                    provider.registerDirective("name", ["alias"]);
                    expect(provider.normalizeDirective("alias")).toBe("name");
                });
                it("resolves more than one directive alias", () => {
                    provider.registerDirective("name", ["alias1", "alias2"]);
                    expect(provider.normalizeDirective("alias1")).toBe("name");
                    expect(provider.normalizeDirective("alias2")).toBe("name");
                });
            });

            describe("hasDirective", () => {
                it("returns whether a directive name has been registered", () => {
                    provider.registerDirective("name1");
                    expect(provider.hasDirective("name1")).toBe(true);

                    provider.registerDirective("name2", ["alias"]);
                    expect(provider.hasDirective("name2")).toBe(true);

                    expect(provider.hasDirective("name3")).toBe(false);
                });
            });

            describe("normalizeContext", () => {
                it("returns the original name", () => {
                    provider.registerContext("name1");
                    expect(provider.normalizeContext("name1")).toBe("name1");

                    provider.registerContext("name2", ["alias1", "alias2"]);
                    expect(provider.normalizeContext("name2")).toBe("name2");
                });
                it("resolves directive aliases", () => {
                    provider.registerContext("name", ["alias"]);
                    expect(provider.normalizeContext("alias")).toBe("name");
                });
                it("resolves more than one directive alias", () => {
                    provider.registerContext("name", ["alias1", "alias2"]);
                    expect(provider.normalizeContext("alias1")).toBe("name");
                    expect(provider.normalizeContext("alias2")).toBe("name");
                });
            });

            describe("hasContext", () => {
                it("returns whether a directive name has been registered", () => {
                    provider.registerContext("name1");
                    expect(provider.hasContext("name1")).toBe(true);

                    provider.registerContext("name2", ["alias"]);
                    expect(provider.hasContext("name2")).toBe(true);

                    expect(provider.hasContext("name3")).toBe(false);
                });
            });

            describe("$get", () => {
                it("returns a service instance", () => {
                    var fn = provider.$get[1];
                    expect(fn(adhConfigMock).constructor).toBe(AdhEmbed.Service);
                });
            });
        });

        describe("Service", () => {
            var providerMock;
            var service;

            beforeEach(() => {
                providerMock = {
                    embeddableDirectives: ["document-workbench", "empty"]
                };
                service = new AdhEmbed.Service(providerMock, adhConfigMock);
            });

            describe("location2template", () => {
                it("compiles a template from the parameters given in $location", () => {
                    var expected = "<adh-document-workbench data-path=\"/this/is/a/path\" " +
                        "data-test=\"&quot;&#39;&amp;\"></adh-document-workbench>";
                    var widget = "document-workbench";
                    var search = {
                        path: "/this/is/a/path",
                        test: "\"'&"
                    };
                    expect(service.location2template(widget, search)).toBe(expected);
                });
                it("does not include meta params as attributes", () => {
                    var expected = "<adh-document-workbench data-path=\"/this/is/a/path\"></adh-document-workbench>";
                    var widget = "document-workbench";
                    var search = {
                        path: "/this/is/a/path",
                        noheader: "",
                        nocenter: "",
                        locale: "de"
                    };
                    expect(service.location2template(widget, search)).toBe(expected);
                });
                it("returns '' if widget is 'empty'", () => {
                    var expected = "";
                    var widget = "empty";
                    var search =  {};
                    expect(service.location2template(widget, search)).toBe(expected);
                });

            });

            describe("route", () => {
                it("throws if $location does not specify a widget", () => {
                    $locationMock.path.and.returnValue("/embed/");
                    expect(() => service.route($locationMock)).toThrow();
                });
                it("throws if the requested widget is not available for embedding", () => {
                    $locationMock.path.and.returnValue("/embed/do-not-embed");
                    expect(() => service.route($locationMock)).toThrow();
                });
            });
        });

        describe("normalizeInternalUrl", () => {
            it("does not change relative URLs", () => {
                var url = "/foo/bar";
                var actual = AdhEmbed.normalizeInternalUrl(url, $locationMock);
                expect(actual).toEqual(url);
            });
            it("preserves query arguments on relative URLs", () => {
                var url = "/foo/bar?foo=1&bar=baz";
                var actual = AdhEmbed.normalizeInternalUrl(url, $locationMock);
                expect(actual).toEqual(url);
            });
            it("removes the host from absolute URLs", () => {
                var url = "http://example.com/foo/bar";
                var actual = AdhEmbed.normalizeInternalUrl(url, $locationMock);
                expect(actual).toEqual("/foo/bar");
            });
            it("removes the host from absolute URLs if host has a non-standard port", () => {
                $locationMock.port.and.returnValue("1234");
                var url = "http://example.com:1234/foo/bar";
                var actual = AdhEmbed.normalizeInternalUrl(url, $locationMock);
                expect(actual).toEqual("/foo/bar");
            });
            it("does not change external URLs", () => {
                var url = "http://external.com/foo/bar";
                var actual = AdhEmbed.normalizeInternalUrl(url, $locationMock);
                expect(actual).toEqual(url);
            });
        });

        describe("isInternalUrl", () => {
            it("returns True for relative URLs", () => {
                var url = "/foo/bar";
                var actual = AdhEmbed.isInternalUrl(url, $locationMock);
                expect(actual).toBe(true);
            });
            it("returns true for internal absolute URLs", () => {
                var url = "http://example.com/foo/bar";
                var actual = AdhEmbed.isInternalUrl(url, $locationMock);
                expect(actual).toBe(true);
            });
            it("returns true for internal absolute URLs if host has a non-standard port", () => {
                $locationMock.port.and.returnValue("1234");
                var url = "http://example.com:1234/foo/bar";
                var actual = AdhEmbed.isInternalUrl(url, $locationMock);
                expect(actual).toBe(true);
            });
            it("return false for external URLs", () => {
                var url = "http://external.com/foo/bar";
                var actual = AdhEmbed.isInternalUrl(url, $locationMock);
                expect(actual).toBe(false);
            });
        });
    });
};
