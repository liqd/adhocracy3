/// <reference path="../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import Util = require("./Util");

export var register = () => {
    describe("Util", () => {
        describe("parentPath", () => {
            it("should return '/foo' for '/foo/bar'", () => {
                expect(Util.parentPath("/foo/bar")).toBe("/foo");
            });
            it("should return '' for '/'", () => {
                expect(Util.parentPath("/")).toBe("");
            });
            it("FAIL", () => {
                expect(true).toBe(false);
            });
        });
    });
};
