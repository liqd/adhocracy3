/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import * as AdhResourceUtil from "./ResourceUtil";


export var register = () => {
    describe("ResourceUtil", () => {
        describe("sortResourcesTopologically", () => {
            var r1;
            var r2;
            var r3;
            var r4;
            var r5;
            var adhPreliminaryNamesMock;

            beforeEach(() => {
                r1 = {
                    path: "r1"
                };
                r1.getReferences = jasmine.createSpy("getReferences").and.returnValue([]);
                r2 = {
                    path: "r2"
                };
                r2.getReferences = jasmine.createSpy("getReferences").and.returnValue(["r1"]);
                r3 = {
                    path: "r3"
                };
                r3.getReferences = jasmine.createSpy("getReferences").and.returnValue(["r2"]);
                r4 = {
                    path: "r4"
                };
                r4.getReferences = jasmine.createSpy("getReferences").and.returnValue(["r1", "r3"]);

                adhPreliminaryNamesMock = jasmine.createSpyObj("adhPreliminaryNames", ["isPreliminary"]);
                adhPreliminaryNamesMock.isPreliminary.and.returnValue(true);
            });

            it("should call getReferences on all given resources", () => {
                AdhResourceUtil.sortResourcesTopologically([r2, r3, r4, r1], adhPreliminaryNamesMock);
                expect(r1.getReferences).toHaveBeenCalled();
                expect(r2.getReferences).toHaveBeenCalled();
                expect(r3.getReferences).toHaveBeenCalled();
                expect(r4.getReferences).toHaveBeenCalled();
            });

            it("should return the references sorted topologically", () => {
                var result = AdhResourceUtil.sortResourcesTopologically([r2, r3, r4, r1], adhPreliminaryNamesMock);
                expect(result).toEqual([r1, r2, r3, r4]);
            });

            it("doesn't matter if there are duplicate refernces", () => {
                r4.getReferences = jasmine.createSpy("getReferences").and.returnValue(["r1", "r3", "r1"]);
                var result = AdhResourceUtil.sortResourcesTopologically([r2, r3, r4, r1], adhPreliminaryNamesMock);
                expect(result).toEqual([r1, r2, r3, r4]);
            });

            it("considers parent as just another reference", () => {
                r5 = {
                    path: "r5",
                    parent: "r4"
                };
                r5.getReferences = jasmine.createSpy("getReferences").and.returnValue([]);

                var result = AdhResourceUtil.sortResourcesTopologically([r2, r3, r4, r5, r1], adhPreliminaryNamesMock);
                expect(result).toEqual([r1, r2, r3, r4, r5]);
            });
        });

        describe("derive", () => {
            var oldResource;
            var resource;
            var testResource = function(settings) {
                this.data = {};
                this.content_type = "test.resource";
            };
            var testSheet = function(settings) {
                this.foo = "bar";
            };

            beforeEach(() => {
                oldResource = new testResource({});
                oldResource.path = "/old/path";
                oldResource.data["test.sheet"] = new testSheet({});
                resource = AdhResourceUtil.derive(oldResource, {});
            });

            it("sets the right content type", () => {
                expect(resource.content_type).toBe("test.resource");
            });

            it("clones all sheets", () => {
                expect(resource.data["test.sheet"]).toBeDefined();
                expect(resource.data["test.sheet"].foo).toBe("bar");
            });

            it("creates a follos entry referencing the old version", () => {
                expect(resource.data["adhocracy_core.sheets.versions.IVersionable"].follows).toEqual(["/old/path"]);
            });
        });
    });
};
