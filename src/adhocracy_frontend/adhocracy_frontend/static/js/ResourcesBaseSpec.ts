/// <reference path="../lib2/types/jasmine.d.ts"/>
/// <reference path="_all.d.ts"/>

import * as JasmineHelpers from "./JasmineHelpers";

import * as ResourcesBase from "./ResourcesBase";

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
    });
};
