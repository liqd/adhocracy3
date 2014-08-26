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

        describe("nextPreliminary", () => {
            it("returns strings, not null", () => {
                expect(typeof pn.nextPreliminary()).toEqual("string");
            });
            it("returns outputs that are never equal", () => {
                expect(pn.nextPreliminary()).not.toEqual(pn.nextPreliminary());
                expect(pn.nextPreliminary()).not.toBe(pn.nextPreliminary());
            });
            it("returns outputs that start with '@'", () => {
                expect(pn.nextPreliminary()[0]).toEqual("@");
            });
        });

        describe("isPreliminary", () => {
            it("if string starts with '@', return yes", () => {
                expect(pn.isPreliminary("@3u")).toBe(true);
            });
            it("if string starts with anything other than '@', return no", () => {
                expect(pn.isPreliminary("3u")).toBe(false);
            });
        });
    });
};
