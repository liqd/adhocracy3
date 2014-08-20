/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import Util = require("../Util/Util");
import AdhHttp = require("./Http");
import AdhConvert = require("./Convert");

var mkHttpMock = () => {
    var mock = jasmine.createSpyObj("$httpMock", ["get", "post", "put"]);
    mock.get.and.returnValue(q.when({data: {}}));
    mock.post.and.returnValue(q.when({data: {}}));
    mock.put.and.returnValue(q.when({data: {}}));
    return mock;
};

var mkAdhMetaApiMock = () => {
    var mock = {
        objBefore: {
            content_type: "",
            data: {
                readWriteSheet: {
                    readOnlyField: 3,
                    readWriteField: 8
                },
                readOnlySheet: {
                    readOnlyField2: 9,
                }
            }
        },

        objAfter: {
            content_type: "",
            data: {
                readWriteSheet: {
                    readWriteField: 8
                }
            }
        },

        // used by exportContent.
        field: (sheet, field) => {
            switch (sheet + "/" + field) {
            case "readWriteSheet/readOnlyField":
                return { editable: false };
            case "readWriteSheet/readWriteField":
                return { editable: true };
            case "readOnlySheet/readOnlyField2":
                return { editable: false };
            default:
                return { editable: true };  // by default, don't delete anything.
            }
        }
    };

    spyOn(mock, "field").and.callThrough();

    return mock;
};


export var register = () => {
    describe("Http", () => {
        describe("Service", () => {
            var $httpMock;
            var adhMetaApiMock;
            var adhHttp;

            beforeEach(() => {
                $httpMock = mkHttpMock();
                adhMetaApiMock = mkAdhMetaApiMock();
                adhHttp = new AdhHttp.Service($httpMock, q, adhMetaApiMock);
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
            describe("getNewestVersionPath", () => {
                it("promises the first path from the LAST tag", () => {
                    var path = "path";
                    var returnPath1 = "path1";
                    var returnPath2 = "path2";

                    $httpMock.get.and.returnValue(q.when({
                        data: {
                            "adhocracy.sheets.tags.ITag": {
                                elements: [returnPath1, returnPath2]
                            }
                        }
                    }));

                    adhHttp.getNewestVersionPath(path).then((ret) => {
                        expect(ret).toBe(returnPath1);
                        expect($httpMock.get).toHaveBeenCalledWith(path + "/LAST");
                    });
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
            describe("withTransaction", () => {
                var get;
                var put;
                var post1;
                var post2;
                var get2;
                var request;
                var response;
                var _httpTrans;

                beforeEach((done) => {
                    $httpMock.post.and.returnValue(q.when([
                        "get response",
                        "put response",
                        "post1 response",
                        "post2 response",
                        "get2 response"
                    ]));

                    adhHttp.withTransaction((httpTrans) => {
                        _httpTrans = httpTrans;

                        get = httpTrans.get("/get/path");
                        put = httpTrans.put("/put/path", {
                            content_type: "content_type"
                        });
                        post1 = httpTrans.post("/post/path/1", {
                            content_type: "content_type"
                        });
                        post2 = httpTrans.post("/post/path/2", {
                            content_type: "content_type"
                        });
                        get2 = httpTrans.get(post1.path);
                        return httpTrans.commit();
                    }).then((_response) => {
                        response = _response;
                        done();
                    });
                });

                it("posts to /batch", () => {
                    expect($httpMock.post).toHaveBeenCalled();
                    var args = $httpMock.post.calls.mostRecent().args;
                    expect(args[0]).toBe("/batch");
                    request = args[1];
                });

                it("assigns different preliminary paths to different post requests", () => {
                    expect(post1.path).not.toEqual(post2.path);
                });

                it("assigns preliminary first_version_paths on post requests", () => {
                    expect(post1.first_version_path).toBeDefined();
                });

                it("prefixes preliminary paths with a single '@'", () => {
                    expect(post1.path[0]).toBe("@");
                    expect(post1.path[1]).not.toBe("@");
                });

                it("prefixes preliminary first_version_paths with '@@'", () => {
                    expect(post1.first_version_path[0]).toBe("@");
                    expect(post1.first_version_path[1]).toBe("@");
                    expect(post1.first_version_path[2]).not.toBe("@");
                });

                it("adds a result_path to post requests", () => {
                    expect(request[post1.index].result_path).toBeDefined();
                    expect("@" + request[post1.index].result_path).toBe(post1.path);

                    expect(request[post2.index].result_path).toBeDefined();
                    expect("@" + request[post2.index].result_path).toBe(post2.path);
                });

                it("maps preliminary data to responses via `index`", () => {
                    expect(response[get.index]).toBe("get response");
                    expect(response[put.index]).toBe("put response");
                    expect(response[post1.index]).toBe("post1 response");
                    expect(response[post2.index]).toBe("post2 response");
                    expect(response[get2.index]).toBe("get2 response");
                });

                it("throws if you try to use the transaction after commit", () => {
                    expect(() => _httpTrans.get("/some/path")).toThrow();
                });
            });
        });

        describe("importContent", () => {
            it("returns response.data if it is an object", () => {
                var obj = {
                    content_type: "ct",
                    path: "p",
                    data: {}
                };
                var response = {
                    data: obj
                };
                expect(AdhConvert.importContent(response)).toBe(obj);
            });
            it("throws if response.data is not an object", () => {
                var obj = <any>"foobar";
                var response = {
                    data: obj
                };
                expect(() => AdhConvert.importContent(response)).toThrow();
            });
        });

        describe("exportContent", () => {
            var adhMetaApiMock;

            beforeEach(() => {
                adhMetaApiMock = mkAdhMetaApiMock();
            });

            it("deletes the path", () => {
                expect(AdhConvert.exportContent(adhMetaApiMock, {content_type: "", data: {}, path: "test"}))
                    .toEqual({content_type: "", data: {}});
            });
            it("deletes read-only properties", () => {
                var x = AdhConvert.exportContent(adhMetaApiMock, adhMetaApiMock.objBefore);
                var y = adhMetaApiMock.objAfter;
                expect(Util.deepeq(x, y)).toBe(true);
                expect(adhMetaApiMock.field).toHaveBeenCalled();
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
