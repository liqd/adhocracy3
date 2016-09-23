/// <reference path="../../../../lib2/types/jasmine.d.ts"/>

import * as AdhPreliminaryNames from "./PreliminaryNames";

export var register = () => {
    describe("PreliminaryNames", () => {
        var pn : AdhPreliminaryNames.Service;

        beforeEach(() => {
            pn = new AdhPreliminaryNames.Service();
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
            it("returns outputs that start no more than one '@'", () => {
                expect(pn.nextPreliminary()[1]).not.toEqual("@");
            });
        });

        describe("isPreliminary", () => {
            it("if string starts with exactly one '@', return yes", () => {
                expect(pn.isPreliminary("@3u")).toBe(true);
            });
            it("if string starts with more than one '@', return no", () => {
                expect(pn.isPreliminary("@@yqt")).toBe(false);
            });
            it("if string starts with anything other than '@', return no", () => {
                expect(pn.isPreliminary("3u")).toBe(false);
            });
        });
    });
};
