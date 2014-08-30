/// <reference path="../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="_all.d.ts"/>

import JasmineHelpers = require("./JasmineHelpers");
import ResourcesBase = require("./ResourcesBase");

class Sheet1 extends ResourcesBase.Sheet {
    public static _meta : ResourcesBase.ISheetMetaApi = {
        readable: ["comments"],
        editable: [],
        creatable: [],
        create_mandatory: [],
        references: ["ref1", "ref2"]
    };
}

class Sheet2 extends ResourcesBase.Sheet {
    public static _meta : ResourcesBase.ISheetMetaApi = {
        readable: ["comments"],
        editable: [],
        creatable: [],
        create_mandatory: [],
        references: ["ref1", "ref4"]
    };
}

export var register = () => {
    describe("ResourcesBase", () => {
        describe("Resource.getReferences", () => {
            var resource : ResourcesBase.Resource;

            beforeEach(() => {
                jasmine.addMatchers(JasmineHelpers.customMatchers);

                resource = new ResourcesBase.Resource("sometype");

                resource.data = {
                    sheet1: new Sheet1(),
                    sheet2: new Sheet2()
                };
            });

            it("returns the union of all references in all sheets", () => {
                (<any>expect(resource.getReferences())).toSetEqual(["ref1", "ref2", "ref4"]);
            });
        });

        describe("sortResourcesTopologically", () => {
            var r1;
            var r2;
            var r3;
            var r4;

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
            });

            it("should call getReferences on all given resources", () => {
                ResourcesBase.sortResourcesTopologically([r2, r3, r4, r1]);
                expect(r1.getReferences).toHaveBeenCalled();
                expect(r2.getReferences).toHaveBeenCalled();
                expect(r3.getReferences).toHaveBeenCalled();
                expect(r4.getReferences).toHaveBeenCalled();
            });

            it("should return the references sorted topologically", () => {
                var result = ResourcesBase.sortResourcesTopologically([r2, r3, r4, r1]);
                expect(result).toEqual([r1, r2, r3, r4]);
            });
        });
    });
};
