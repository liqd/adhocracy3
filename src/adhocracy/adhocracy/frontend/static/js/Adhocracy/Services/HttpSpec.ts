/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhHttp = require("./Http");

export var register = () => {
    describe("Service/Http", () => {
        describe("Service", () => {
            var $httpMock;
            var adhHttp;

            beforeEach(() => {
                $httpMock = jasmine.createSpyObj("$httpMock", ["get", "post", "put"]);
                $httpMock.get.and.returnValue(q.when({data: {}}));
                $httpMock.post.and.returnValue(q.when({data: {}}));
                $httpMock.put.and.returnValue(q.when({data: {}}));

                adhHttp = new AdhHttp.Service($httpMock, q);
            });

            describe("get", () => {
                it("calls $http.get", () => {
                    adhHttp.get("/some/path");
                    expect($httpMock.get).toHaveBeenCalled();
                });
            });
            describe("post", () => {
                it("calls $http.post", () => {
                    adhHttp.post("/some/path", {data: {}});
                    expect($httpMock.post).toHaveBeenCalled();
                });
            });
            describe("put", () => {
                it("calls $http.put", () => {
                    adhHttp.put("/some/path", {data: {}});
                    expect($httpMock.put).toHaveBeenCalled();
                });
            });
            describe("postNewVersion", () => {
                it("posts to the parent pool and adds a adhocracy.sheets.versions.IVersionable sheet with the right follows field", () => {
                    adhHttp.postNewVersion("/some/path", {data: {}});
                    expect($httpMock.post).toHaveBeenCalledWith("/some", {
                        data: {
                            "adhocracy.sheets.versions.IVersionable": {
                                follows: ["/some/path"]
                            }
                        }
                    });
                });
                it("adds a root_versions field if rootVersions is passed", () => {
                    adhHttp.postNewVersion("/some/path", {data: {}}, ["foo", "bar"]);
                    expect($httpMock.post).toHaveBeenCalledWith("/some", {
                        data: {
                            "adhocracy.sheets.versions.IVersionable": {
                                follows: ["/some/path"]
                            }
                        },
                        root_versions: ["foo", "bar"]
                    });
                });
            });
            describe("postToPool", () => {
                it("calls $http.post", () => {
                    adhHttp.postToPool("/some/path", {data: {}});
                    expect($httpMock.post).toHaveBeenCalled();
                });
            });
            describe("resolve", () => {
                it("gets the resource if called with a path", (done) => {
                    var path = "/some/path";
                    var content = {
                        content_type: "mock2",
                        data: {}
                    };
                    adhHttp.get = jasmine.createSpy("adhHttp.get")
                        .and.returnValue(q.when(content));

                    adhHttp.resolve(path).then((ret) => {
                        expect(ret).toEqual(content);
                        expect(adhHttp.get).toHaveBeenCalledWith(path);
                        done();
                    });
                });
                it("promises the resource if called with a resource", (done) => {
                    var content = {
                        content_type: "mock2",
                        data: {}
                    };

                    adhHttp.resolve(content).then((ret) => {
                        expect(ret).toEqual(content);
                        done();
                    });
                });
            });
        });

        describe("importContent", () => {
            it("returns response.data if it is an object", () => {
                var obj = {
                    content_type: "ct",
                    path: "p",
                    data: {},
                };
                var response = {
                    data: obj
                };
                expect(AdhHttp.importContent(response)).toBe(obj);
            });
            it("throws if response.data is not an object", () => {
                var obj = <any>"foobar";
                var response = {
                    data: obj
                };
                expect(() => AdhHttp.importContent(response)).toThrow();
            });
        });

        describe("exportContent", () => {
            it("deletes the path", () => {
                expect(AdhHttp.exportContent({content_type: "", data: {}, path: "test"}))
                    .toEqual({content_type: "", data: {}});
            });
            it("deletes read-only properties", () => {
                expect(AdhHttp.exportContent({content_type: "", data: {"adhocracy.propertysheets.interfaces.IVersions": "test"}}))
                    .toEqual({content_type: "", data: {}});
            });
        });

        describe("logBackendError", () => {
            var origConsoleLog;

            beforeEach(() => {
                origConsoleLog = console.log;
                console.log = jasmine.createSpy("consoleLogMock");
            });

            it("always throws an exception", () => {
                var backendError = {
                    status: "error",
                    errors: []
                };
                expect(() => AdhHttp.logBackendError({ data: backendError })).toThrow();
            });

            it("logs the raw backend error to console", () => {
                var backendError = {
                    status: "error",
                    errors: []
                };
                var response = {
                    data: backendError
                };
                expect(() => AdhHttp.logBackendError(response)).toThrow();
                expect(console.log).toHaveBeenCalledWith(backendError);
            });

            it("logs all individual errors to console", () => {
                var backendError = {
                    status: "error",
                    errors: [
                        { name: "where0.0", location: "where0.1", description: "what0" },
                        { name: "where1.0", location: "where1.1", description: "what1" }
                    ]
                };
                expect(() => AdhHttp.logBackendError({ data: backendError })).toThrow();
                expect(console.log).toHaveBeenCalledWith("error #0");
                expect(console.log).toHaveBeenCalledWith("where: where0.0, where0.1");
                expect(console.log).toHaveBeenCalledWith("what:  what0");
                expect(console.log).toHaveBeenCalledWith("error #1");
                expect(console.log).toHaveBeenCalledWith("where: where1.0, where1.1");
                expect(console.log).toHaveBeenCalledWith("what:  what1");
            });

            afterEach(() => {
                console.log = origConsoleLog;
            });
        });
    });
};
