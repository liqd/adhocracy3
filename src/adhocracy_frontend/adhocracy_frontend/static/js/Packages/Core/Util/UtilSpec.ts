/// <reference path="../../../../lib2/types/jasmine.d.ts"/>

import * as q from "q";

import * as AdhUtil from "./Util";

export var register = () => {
    describe("Util", () => {
        describe("parentPath", () => {
            it("returns '/foo' for '/foo/bar'", () => {
                expect(AdhUtil.parentPath("/foo/bar")).toBe("/foo");
            });
            it("returns '/foo/' for '/foo/bar/'", () => {
                expect(AdhUtil.parentPath("/foo/bar/")).toBe("/foo/");
            });
            it("returns '/' for '/'", () => {
                expect(AdhUtil.parentPath("/")).toBe("/");
            });
            it("returns '/' for 'bla'", () => {
                expect(AdhUtil.parentPath("bla")).toBe("/");
            });
            it("returns '/' for ''", () => {
                expect(AdhUtil.parentPath("")).toBe("/");
            });
            it("works with URLs", () => {
                expect(AdhUtil.parentPath("http://example.com/foo/bar")).toBe("http://example.com/foo");
                expect(AdhUtil.parentPath("https://example.com/foo/bar")).toBe("https://example.com/foo");
                expect(AdhUtil.parentPath("http://example.com/foo/bar/")).toBe("http://example.com/foo/");
                expect(AdhUtil.parentPath("http://example.com")).toBe("http://example.com/");
            });
        });

        describe("normalizeName", () => {
            it("is idempotent", () => {
                ["asdkj", "#!8 sajd ksalkjad\n", "foo bar", "Foo Bar", "foo_bar"].forEach((s) => {
                    var normalized = AdhUtil.normalizeName(s);
                    expect(AdhUtil.normalizeName(normalized)).toBe(normalized);
                });
            });

            it("preserves ascii", () => {
                expect(AdhUtil.normalizeName("asdASD123")).toBe("asdASD123");
            });

            it("replaces german umlauts", () => {
                expect(AdhUtil.normalizeName("äüÄÖß")).toBe("aeueAeOess");
            });

            it("replaces spaces by underscores", () => {
                expect(AdhUtil.normalizeName(" ")).toBe("_");
            });

            it("strips chars that are not allowed in an URI component", () => {
                expect(AdhUtil.normalizeName("$%&/?")).toBe("");
            });

            it("strips non-ascii", () => {
                expect(AdhUtil.normalizeName("…")).toBe("");
            });
        });

        describe("formatString", () => {
            it("formats a string", () => {
                expect(AdhUtil.formatString("Hello {0} from {1}", "World", "Bernd")).toBe("Hello World from Bernd");
            });
            it("does not replace {n} if there is no n-th parameter", () => {
                expect(AdhUtil.formatString("Hello {0} from {1}", "World")).toBe("Hello World from {1}");
            });
        });

        describe("sortDagTopologically", () => {

            it("sorts a given dag topologically", () => {
                var dag : AdhUtil.IDag<string> = {
                    "A": {
                        "content": "AA",
                        "incoming": [],
                        "outgoing": ["B", "D"],
                        "done": false
                    },
                    "B": {
                        "content": "BB",
                        "incoming": ["A"],
                        "outgoing": ["C"],
                        "done": false
                    },
                    "C": {
                        "content": "CC",
                        "incoming": ["B"],
                        "outgoing": ["D"],
                        "done": false
                    },
                    "D": {
                        "content": "DD",
                        "incoming": ["A", "C"],
                        "outgoing": [],
                        "done": false
                    }
                };

                var result = AdhUtil.sortDagTopologically(dag, ["A"]);
                expect(result).toEqual(["AA", "BB", "CC", "DD"]);
            });

            it("throws a cycle detected error if the given graph contains cycles", () => {
                var dag : AdhUtil.IDag<string> = {
                    "A": {
                        "content": "AA",
                        "incoming": [],
                        "outgoing": ["B"],
                        "done": false
                    },
                    "B": {
                        "content": "BB",
                        "incoming": ["A", "C"],
                        "outgoing": ["C"],
                        "done": false
                    },
                    "C": {
                        "content": "CC",
                        "incoming": ["B"],
                        "outgoing": ["B"],
                        "done": false
                    }
                };

                expect(() => AdhUtil.sortDagTopologically(dag, ["A"])).toThrow();
            });
        });

        describe("qFilter", () => {
            it("works mostly like $q.all", (done) => {
                AdhUtil.qFilter([q.when("a"), q.when("b"), q.when("c")], <any>q)
                    .then((result) => {
                        expect(result).toEqual(["a", "b", "c"]);
                        done();
                    });
            });

            it("filters out any rejected promises", (done) => {
                AdhUtil.qFilter([q.when("a"), q.reject("b"), q.when("c")], <any>q)
                    .then((result) => {
                        expect(result).toEqual(["a", "c"]);
                        done();
                    });
            });

            it("promises empty list if empty list was passed", (done) => {
                AdhUtil.qFilter([], <any>q)
                    .then((result) => {
                        expect(result).toEqual([]);
                        done();
                    });
            });
        });
    });
};
