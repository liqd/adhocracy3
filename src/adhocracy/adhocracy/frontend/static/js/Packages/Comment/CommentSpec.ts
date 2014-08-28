/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhComment = require("./Comment");
import AdhPreliminaryNames = require("../../Packages/PreliminaryNames/PreliminaryNames");

var RESOURCE = {
    path: "path",
    content_type: "",
    data: {}
};

export var register = () => {
    describe("Comment", () => {
        var adhConfigMock;
        var adapterMock;
        var adhHttpMock;

        beforeEach(() => {
            adhConfigMock = {
                pkg_path: "mock"
            };

            adapterMock = <any>jasmine.createSpyObj("adapterMock", ["create", "content", "refersTo", "creator"]);

            adhHttpMock = <any>jasmine.createSpyObj("adhHttpMock", ["postToPool", "resolve", "postNewVersion", "getNewestVersionPath"]);
            adhHttpMock.postToPool.and.returnValue(q.when(RESOURCE));
            adhHttpMock.resolve.and.returnValue(q.when(RESOURCE));
            adhHttpMock.postNewVersion.and.returnValue(q.when(RESOURCE));
            adhHttpMock.getNewestVersionPath.and.returnValue(q.when(RESOURCE));
        });

        describe("ListingCommentableAdapter", () => {
            var adapter;

            beforeEach(() => {
                adapter = new AdhComment.ListingCommentableAdapter();
            });

            describe("elemRefs", () => {
                var generateResource = () => {
                    return {
                        data: {
                            "adhocracy_sample.sheets.comment.ICommentable": {
                                comments: [
                                    "/asd/version2",
                                    "/asd/version3",
                                    "/foo/version1",
                                    "/bar/version1",
                                    "/asd/version1",
                                    "/foo/version2"
                                ]
                            }
                        }
                    };

                };

                it("returns only the most recent versions from the adhocracy_sample.sheets.comment.ICommentable sheet", () => {
                    var resource = generateResource();
                    var result = adapter.elemRefs(resource);
                    expect(result).toContain("/asd/version3");
                    expect(result).toContain("/foo/version2");
                    expect(result).toContain("/bar/version1");
                    expect(result.length).toBe(3);
                });

                it("does not modify the resource", () => {
                    var resource = generateResource();
                    adapter.elemRefs(resource);
                    expect(resource).toEqual(generateResource());
                });
            });

            describe("poolPath", () => {
                it("returns the parent path of the container path", () => {
                    var resource = {
                        path: "some/path/parent"
                    };

                    expect(adapter.poolPath(resource)).toEqual("some/path");
                });
            });
        });

        describe("CommentCreate", () => {
            var commentCreate;

            beforeEach(() => {
                commentCreate = new AdhComment.CommentCreate(adapterMock);
            });

            describe("createDirective", () => {
                var directive;

                beforeEach(() => {
                    directive = commentCreate.createDirective(adhConfigMock);
                });

                describe("controller", () => {
                    var scopeMock;

                    beforeEach(() => {
                        scopeMock = {
                            refersTo: "refersTo"
                        };

                        var controller = <any>directive.controller[3];
                        controller(scopeMock, adhHttpMock, new AdhPreliminaryNames());
                    });

                    describe("create", () => {
                        // FIXME: all http interaction is currently untested as it is
                        // likely to change in the near future

                        var resource = {foo: "bar"};
                        var content = "content";

                        beforeEach((done) => {
                            scopeMock.content = content;
                            scopeMock.onNew = jasmine.createSpy("onNew");
                            adapterMock.create.and.returnValue(resource);
                            scopeMock.create().then(done);
                        });

                        it("creates a new resource using the adapter", () => {
                            expect(adapterMock.create.calls.count()).toBe(1);
                            expect(adapterMock.content.calls.count()).toBe(1);
                            expect(adapterMock.refersTo.calls.count()).toBe(1);
                            expect(adapterMock.content.calls.first().args[1]).toBe(content);
                            expect(adapterMock.refersTo.calls.first().args[1]).toBe("refersTo");
                        });

                        it("calls the onNew callback", () => {
                            expect(scopeMock.onNew).toHaveBeenCalled();
                        });
                    });
                });
            });
        });

        describe("CommentDetail", () => {
            var commentDetail;

            beforeEach(() => {
                commentDetail = new AdhComment.CommentDetail(adapterMock);
            });

            describe("createDirective", () => {
                var directive;

                beforeEach(() => {
                    directive = commentDetail.createDirective(adhConfigMock);
                });

                describe("controller", () => {
                    var scopeMock;
                    var content = "content";
                    var creator = "creator";

                    beforeEach((done) => {
                        scopeMock = {
                            path: "/some/path",
                            viemode: "list"
                        };

                        adapterMock.content.and.returnValue(content);
                        adapterMock.creator.and.returnValue(creator);

                        var controller = <any>directive.controller[3];
                        controller(scopeMock, adhHttpMock, done);
                    });

                    it("reads content and creator from adapter to scope", () => {
                        expect(scopeMock.data.content).toBe(content);
                        expect(scopeMock.data.creator).toBe(creator);
                    });

                    describe("edit", () => {
                        beforeEach(() => {
                            scopeMock.edit();
                        });

                        it("changes viewmode to 'edit'", () => {
                            expect(scopeMock.viewmode).toBe("edit");
                        });
                    });

                    describe("cancel", () => {
                        beforeEach(() => {
                            scopeMock.cancel();
                        });

                        it("changes viewmode to 'list'", () => {
                            expect(scopeMock.viewmode).toBe("list");
                        });

                        it("clears all errors", () => {
                            expect(scopeMock.errors).toEqual([]);
                        });
                    });

                    describe("save", () => {
                        it("updates the resource using the adapter", (done) => {
                            scopeMock.data = {
                                content: content
                            };
                            scopeMock.save().then(() => {
                                expect(adapterMock.content).toHaveBeenCalledWith(RESOURCE, content);
                                expect(adhHttpMock.postNewVersion).toHaveBeenCalled();
                                done();
                            });
                        });

                        it("sets scope.errors when something goes wrong", (done) => {
                            var errors = "errors";
                            adhHttpMock.postNewVersion.and.returnValue(q.reject(errors));
                            scopeMock.data = {
                                content: content
                            };
                            scopeMock.save().then(() => null, () => {
                                expect(scopeMock.errors).toBe(errors);
                                done();
                            });
                        });
                    });
                });
            });
        });
    });
};
