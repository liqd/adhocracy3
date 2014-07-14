/// <reference path="../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import Embed = require("./Embed");

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
                        test: "\"&"
                    }
                }
            };
            // FIXME DefinitelyTyped does not yet know of `and`.
            $compileMock = (<any>jasmine.createSpy("$compileMock"))
                .and.returnValue(() => undefined);
        });

        describe("route2template", () => {
            it("compiles a template from the parameters given in $route", () => {
                var expected = "<adh-document-workbench data-path=\"&#x27;/this/is/a/path&#x27;\" " +
                    "data-test=\"&#x27;&quot;&amp;&#x27;\"></adh-document-workbench>";
                expect(Embed.route2template($routeMock)).toBe(expected);
            });
        });

        describe("factory", () => {
            it("calls $compile", () => {
                var directive = Embed.factory($compileMock, $routeMock);
                directive.link(undefined, {
                    contents: () => undefined,
                    html: () => undefined
                });
                expect($compileMock).toHaveBeenCalled();
            });
        });
    });
};
