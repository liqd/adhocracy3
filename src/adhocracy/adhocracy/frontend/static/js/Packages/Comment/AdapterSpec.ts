/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhCommentAdapter = require("./Adapter");

export var register = () => {
    describe("CommentAdapter", () => {
        var resource;
        var adapter;

        beforeEach(() => {
            resource = {
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
            beforeEach(() => {
                resource = adapter.create();
            });

            it("returns an adhocracy_sample.resources.comment.ICommentVersion resource", () => {
                expect(resource.content_type).toBe("adhocracy_sample.resources.comment.ICommentVersion");
            });

            it("creates an empty adhocracy_sample.sheets.comment.IComment sheet", () => {
                expect(resource.data["adhocracy_sample.sheets.comment.IComment"]).toBeDefined();
            });
        });

        describe("content", () => {
            it("gets content from adhocracy_sample.sheets.comment.IComment", () => {
                expect(adapter.content(resource)).toBe("content");
            });
            it("sets content from adhocracy_sample.sheets.comment.IComment", () => {
                adapter.content(resource, "content2");
                expect(resource.data["adhocracy_sample.sheets.comment.IComment"].content).toBe("content2");
            });
            it("returns resource when used as a setter", () => {
                var result = adapter.content(resource, "content2");
                expect(result.data["adhocracy_sample.sheets.comment.IComment"].content).toBe("content2");
            });
        });

        describe("refersTo", () => {
            it("gets refers_to from adhocracy_sample.sheets.comment.IComment", () => {
                expect(adapter.refersTo(resource)).toBe("refersTo");
            });
            it("sets refers_to from adhocracy_sample.sheets.comment.IComment", () => {
                adapter.refersTo(resource, "refersTo2");
                expect(resource.data["adhocracy_sample.sheets.comment.IComment"].refers_to).toBe("refersTo2");
            });
            it("returns resource when used as a setter", () => {
                var result = adapter.refersTo(resource, "refersTo2");
                expect(result.data["adhocracy_sample.sheets.comment.IComment"].refers_to).toBe("refersTo2");
            });
        });

        describe("creator", () => {
            it("gets creator from adhocracy.sheets.metadata.IMetadata", () => {
                expect(adapter.creator(resource)).toBe("creator");
            });
        });
    });
};