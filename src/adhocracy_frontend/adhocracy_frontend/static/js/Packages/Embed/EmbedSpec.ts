/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhEmbed = require("./Embed");

export var register = () => {
    describe("Embed", () => {
        var $routeMock;
        var $compileMock;

        beforeEach(() => {
            $routeMock = {
                current: {
                    params: {
                        widget: "document-workbench",
                        path: "/this/is/a/path",
                        test: "\"'&"
                    }
                }
            };
            $compileMock = jasmine.createSpy("$compileMock")
                .and.returnValue(() => undefined);
        });

        describe("route2template", () => {
            it("compiles a template from the parameters given in $route", () => {
                var expected = "<adh-document-workbench data-path=\"/this/is/a/path\" " +
                    "data-test=\"&quot;&#39;&amp;\"></adh-document-workbench>";
                expect(AdhEmbed.route2template($routeMock)).toBe(expected);
            });
            it("throws if $route does not specify a widget", () => {
                delete $routeMock.current.params.widget;
                expect(() => AdhEmbed.route2template($routeMock)).toThrow();
            });
            it("throws if the requested widget is not available for embedding", () => {
                $routeMock.current.params.widget = "do-not-embed";
                expect(() => AdhEmbed.route2template($routeMock)).toThrow();
            });
        });

        describe("factory", () => {
            it("calls $compile", () => {
                var directive = AdhEmbed.factory($compileMock, $routeMock);
                directive.link(undefined, {
                    contents: () => undefined,
                    html: () => undefined
                });
                expect($compileMock).toHaveBeenCalled();
            });
        });
    });
};
