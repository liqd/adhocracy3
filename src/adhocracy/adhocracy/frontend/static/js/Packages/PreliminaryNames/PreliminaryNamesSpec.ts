/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhPreliminaryNames = require("./PreliminaryNames");

export var register = () => {
    describe("PreliminaryNames", () => {
        var pn : AdhPreliminaryNames;

        beforeEach(() => {
            pn = new AdhPreliminaryNames();
        });

        describe("next", () => {
            it("returns strings, not null", () => {
                expect(typeof pn.next()).toEqual("string");
            });
            it("returns outputs that are never equal", () => {
                expect(pn.next()).not.toEqual(pn.next());
                expect(pn.next()).not.toBe(pn.next());
            });
        });
    });
};
