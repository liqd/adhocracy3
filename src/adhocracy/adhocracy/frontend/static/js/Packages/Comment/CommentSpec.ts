/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhPreliminaryNames = require("../../Packages/PreliminaryNames/PreliminaryNames");

import AdhComment = require("./Comment");

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

            adapterMock = <any>jasmine.createSpyObj("adapterMock", ["create", "content", "refersTo", "creator", "creationDate",
                "modificationDate", "commentCount", "elemRefs", "poolPath"]);

            adhHttpMock = <any>jasmine.createSpyObj("adhHttpMock", ["postToPool", "resolve", "postNewVersion", "getNewestVersionPath"]);
            adhHttpMock.postToPool.and.returnValue(q.when(RESOURCE));
            adhHttpMock.resolve.and.returnValue(q.when(RESOURCE));
            adhHttpMock.postNewVersion.and.returnValue(q.when(RESOURCE));
            adhHttpMock.getNewestVersionPath.and.returnValue(q.when(RESOURCE));
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
                    var creationDate = "creationDate";
                    var modificationDate = "modificationDate";
                    var commentCount = 2;
                    var elemRefs = ["foo", "bar"];
                    var poolPath = "poolPath";

                    beforeEach((done) => {
                        scopeMock = {
                            path: "/some/path",
                            viemode: "list"
                        };

                        adapterMock.content.and.returnValue(content);
                        adapterMock.creator.and.returnValue(creator);
                        adapterMock.creationDate.and.returnValue(creationDate);
                        adapterMock.modificationDate.and.returnValue(modificationDate);
                        adapterMock.commentCount.and.returnValue(commentCount);
                        adapterMock.elemRefs.and.returnValue(elemRefs);
                        adapterMock.poolPath.and.returnValue(poolPath);

                        var controller = <any>directive.controller[3];
                        controller(scopeMock, adhHttpMock, done);
                    });

                    it("reads content from adapter to scope", () => {
                        expect(scopeMock.data.content).toBe(content);
                    });
                    it("reads creator from adapter to scope", () => {
                        expect(scopeMock.data.creator).toBe(creator);
                    });
                    it("reads creationDate from adapter to scope", () => {
                        expect(scopeMock.data.creationDate).toBe(creationDate);
                    });
                    it("reads modificationDate from adapter to scope", () => {
                        expect(scopeMock.data.modificationDate).toBe(modificationDate);
                    });
                    it("reads commentCount from adapter to scope", () => {
                        expect(scopeMock.data.commentCount).toBe(commentCount);
                    });
                    it("reads comments from adapter to scope", () => {
                        expect(scopeMock.data.comments).toBe(elemRefs);
                    });
                    it("reads poolPath from adapter to scope", () => {
                        expect(scopeMock.data.poolPath).toBe(poolPath);
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
