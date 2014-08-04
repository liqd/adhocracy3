/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhCommentAdapter = require("./Adapter");

export var register = () => {
    describe("CommentAdapter", () => {
        var res;
        var adapter;

        beforeEach(() => {
            res = {
                data: {
                    "adhocracy_sample.sheets.comment.IComment": {
                        refers_to: "refersTo",
                        content: "content"
                    },
                    "adhocracy.sheets.metadata.IMetadata": {
                        creator: "creator"
                    }
                }
            };
            adapter = new AdhCommentAdapter.CommentAdapter();
        });

        describe("create", () => {
            it("returns an empty adhocracy_sample.sheets.comment.IComment resource", () => {
                expect(adapter.create()).toEqual({
                    content_type: "adhocracy_sample.resources.comment.ICommentVersion",
                    data: {
                        "adhocracy_sample.sheets.comment.IComment": {
                            content: undefined,
                            refers_to: undefined
                        }
                    }
                });
            });
        });

        describe("content", () => {
            it("gets content from adhocracy_sample.sheets.comment.IComment", () => {
                expect(adapter.content(res)).toBe("content");
            });
            it("sets content from adhocracy_sample.sheets.comment.IComment", () => {
                adapter.content(res, "content2");
                expect(res.data["adhocracy_sample.sheets.comment.IComment"].content).toBe("content2");
            });
            it("returns res when used as a setter", () => {
                var result = adapter.content(res, "content2");
                expect(result.data["adhocracy_sample.sheets.comment.IComment"].content).toBe("content2");
            });
        });

        describe("refersTo", () => {
            it("gets refers_to from adhocracy_sample.sheets.comment.IComment", () => {
                expect(adapter.refersTo(res)).toBe("refersTo");
            });
            it("sets refers_to from adhocracy_sample.sheets.comment.IComment", () => {
                adapter.refersTo(res, "refersTo2");
                expect(res.data["adhocracy_sample.sheets.comment.IComment"].refers_to).toBe("refersTo2");
            });
            it("returns res when used as a setter", () => {
                var result = adapter.refersTo(res, "refersTo2");
                expect(result.data["adhocracy_sample.sheets.comment.IComment"].refers_to).toBe("refersTo2");
            });
        });

        describe("creator", () => {
            it("gets creator from adhocracy.sheets.metadata.IMetadata", () => {
                expect(adapter.creator(res)).toBe("creator");
            });
        });
    });
};
