/// <reference path="../lib2/types/jasmine.d.ts"/>
/// <reference path="_all.d.ts"/>

import * as JasmineHelpers from "./JasmineHelpers";

export var register = () => {
    describe("JasmineHelpers", () => {
        /**
         * This isn't strictly speaking a unit test, but rather an integration
         * test. Instead of mocking the jasmine environment, it tests whether
         * the custom matcher works within the jasmine environment.
         *
         * As this only requires jasmine and nothing else, it nevertheless
         * uses the unit test format.
         */
        describe("customMatchers", () => {
            describe("toSetEqual", () => {

                var array1 : Array<string>;
                var array1a : Array<string>;
                var array1b : Array<string>;
                var array2 : Array<string>;
                var array3 : Array<string>;
                var array4 : Array<string>;

                beforeEach(() => {

                    jasmine.addMatchers(JasmineHelpers.customMatchers);

                    array1 = ["la", "li", "lu"];
                    array1a = ["la", "li", "lu"];
                    array1b = ["lu", "la", "li"];
                    array2 = ["du", "la", "li"];
                    array3 = ["la", "li"];
                    array4 = ["la", "li", "lu", "lo"];
                });

                it("returns true if arrays are equal", () => {
                    (<any>expect(array1)).toSetEqual(array1a);
                });

                it("returns true if arrays are shuffled", () => {
                    (<any>expect(array1)).toSetEqual(array1b);
                });

                it("returns false if arrays have different elements, but same length", () => {
                    (<any>expect(array1)).not.toSetEqual(array2);
                });

                it("returns false if actual has less elements than expected", () => {
                    (<any>expect(array1)).not.toSetEqual(array3);
                });

                it("returns false if actual has more elements than expected", () => {
                    (<any>expect(array1)).not.toSetEqual(array4);
                });
            });
        });
    });
};
