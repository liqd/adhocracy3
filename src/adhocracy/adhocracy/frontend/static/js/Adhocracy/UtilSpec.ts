/// <reference path="../../submodules/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import Util = require("./Util");

export var register = () => {
    describe("Util", () => {
        describe("cutArray", () => {
            it("should remove single items", () => {
                expect(Util.cutArray([1, 2, 3, 4], 0)).toEqual([2, 3, 4]);
                expect(Util.cutArray([1, 2, 3, 4], 1)).toEqual([1, 3, 4]);
                expect(Util.cutArray([1, 2, 3, 4], -1)).toEqual([1, 2, 3]);
                expect(Util.cutArray([1, 2, 3, 4], -2)).toEqual([1, 2, 4]);
            });
            it("should remove single items if 'from' and 'to' are equal", () => {
                expect(Util.cutArray([1, 2, 3, 4], 0, 0)).toEqual([2, 3, 4]);
                expect(Util.cutArray([1, 2, 3, 4], 1, 1)).toEqual([1, 3, 4]);
                expect(Util.cutArray([1, 2, 3, 4], -1, -1)).toEqual([1, 2, 3]);
                expect(Util.cutArray([1, 2, 3, 4], -2, -2)).toEqual([1, 2, 4]);
            });
            it("should remove ranges", () => {
                expect(Util.cutArray([1, 2, 3, 4], 0, -1)).toEqual([]);
                expect(Util.cutArray([1, 2, 3, 4], 0, 3)).toEqual([]);
                expect(Util.cutArray([1, 2, 3, 4], 1, 3)).toEqual([1]);
                expect(Util.cutArray([1, 2, 3, 4], 0, 2)).toEqual([4]);
                expect(Util.cutArray([1, 2, 3, 4], 1, -2)).toEqual([1, 4]);
                expect(Util.cutArray([1, 2, 3, 4], -3, -2)).toEqual([1, 4]);
            });
        });

        describe("isInfixOf", () => {
            it("should return false for an empty list", () => {
                expect(Util.isInfixOf(0, [])).toBe(false);
            });
            it("should return false if needle is not in hay", () => {
                expect(Util.isInfixOf("needle", ["hay", "stack"])).toBe(false);
                expect(Util.isInfixOf(0, [1, 2, 3])).toBe(false);
            });
            it("should return true if needle is in hay", () => {
                expect(Util.isInfixOf("hay", ["hay", "stack"])).toBe(true);
                expect(Util.isInfixOf(2, [1, 2, 3])).toBe(true);
            });
            it("should not return true for list properties that are not list items (such as length)", () => {
                expect(Util.isInfixOf("length", ["hay", "stack"])).toBe(false);
                expect(Util.isInfixOf(0, ["hay", "stack"])).toBe(false);
            });
        });

        describe("parentPath", () => {
            it("should return '/foo' for '/foo/bar'", () => {
                expect(Util.parentPath("/foo/bar")).toBe("/foo");
            });
            it("should return '' for '/'", () => {
                expect(Util.parentPath("/")).toBe("");
            });
        });

        describe("deepcp", () => {
            var samples = [
                null,
                1,
                "test",
                [1, 2, "test"],
                {
                    foo: 1,
                    bar: 2,
                    point: {
                        x: 0,
                        y: 0
                    }
                }
            ];

            it("should output something that equals input", () => {
                samples.forEach((ob) => {
                    expect(Util.deepcp(ob)).toEqual(ob);
                });
            });
            it("should output an object that shares no members with the input object", () => {
                var input = samples[samples.length - 1];
                var output = Util.deepcp(input);
                output.point.x = 1;
                expect(input.point.x).not.toBe(1);
            });
        });

        describe("deepoverwrite", () => {
            it("should copy all properties of source to target", () => {
                var source = {
                    foo: 2,
                    bar: 3
                };
                var _target = {
                    foo: 1,
                    baz: 4
                };
                Util.deepoverwrite(source, _target);
                expect(_target.foo).toBe(2);
                expect(_target.bar).toBe(3);
                expect(_target.baz).toBeUndefined();
            });
            xit("should crash if target is not an object", () => {
                expect(() => Util.deepoverwrite({}, 1)).toThrow();
                expect(() => Util.deepoverwrite({}, "test")).toThrow();
                expect(() => Util.deepoverwrite({}, [])).toThrow();
            });
        });

        describe("deepeq", () => {
            var samples = [
                null,
                1,
                "test",
                [1, 2, "test"],
                {
                    foo: 1,
                    bar: 2,
                    point: {
                        x: 0,
                        y: 0
                    }
                }
            ];

            it("should report an object to be equal to itself", () => {
                samples.forEach((ob) => {
                    expect(Util.deepeq(ob, ob)).toBe(true);
                });
            });
            it("should report an object to not be equal to something completely different", () => {
                samples.forEach((ob) => {
                    expect(Util.deepeq(ob, "completelyDifferent")).toBe(false);
                });
            });
            it("should return false for equal objects that are not identical", () => {
                var a = {
                    point: {
                        x: 0,
                        y: 1
                    },
                    foo: "bar"
                };
                var b = {
                    point: {
                        x: 0,
                        y: 1
                    },
                    foo: "bar"
                };
                expect(Util.deepeq(a, b)).toBe(false);
            });
            it("should return false for similar objects with differing values", () => {
                var a = {
                    point: {
                        x: 0,
                        y: 1
                    },
                    foo: "bar"
                };
                var b = {
                    point: {
                        x: 0,
                        y: 2
                    },
                    foo: "bar"
                };
                expect(Util.deepeq(a, b)).toBe(false);
            });
            it("should return false for similar objects with missing keys", () => {
                var a = {
                    point: {
                        x: 0,
                        y: 1
                    },
                    foo: "bar"
                };
                var b = {
                    point: {
                        x: 0,
                    },
                    foo: "bar"
                };
                expect(Util.deepeq(a, b)).toBe(false);
            });
            it("should return false for similar objects with additional keys", () => {
                var a = {
                    point: {
                        x: 0,
                        y: 1
                    },
                    foo: "bar"
                };
                var b = {
                    point: {
                        x: 0,
                        y: 1,
                        z: 1
                    },
                    foo: "bar"
                };
                expect(Util.deepeq(a, b)).toBe(false);
            });
        });

        describe("normalizeName", () => {
            it("should return 'foo_bar' for 'Foo Bar'", () => {
                expect(Util.normalizeName("Foo Bar")).toBe("foo_bar");
            });
            it("should be idempotent", () => {
                ["asdkj", "#!8 sajd ksalkjad\n", "foo bar", "Foo Bar", "foo_bar"].forEach((s) => {
                    var normalized = Util.normalizeName(s);
                    expect(Util.normalizeName(normalized)).toBe(normalized);
                });
            });
        });
    });
};
