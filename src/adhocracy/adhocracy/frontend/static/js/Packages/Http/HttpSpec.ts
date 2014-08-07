/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import Util = require("../Util/Util");
import AdhHttp = require("./Http");

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

    spyOn(mock, 'field').and.callThrough();

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
                it("performs AdhHttp api calls that are triggered inside the transaction callback", () => {
                    adhHttp.withTransaction((httpTrans, done) => {
                        httpTrans.get("/some/path");
                        done();
                    });
                    expect($httpMock.get).toHaveBeenCalled();
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
            var adhMetaApiMock;

            beforeEach(() => {
                adhMetaApiMock = mkAdhMetaApiMock();
            });

            it("deletes the path", () => {
                expect(AdhHttp.exportContent(adhMetaApiMock, {content_type: "", data: {}, path: "test"}))
                    .toEqual({content_type: "", data: {}});
            });
            it("deletes read-only properties", () => {
                var x = AdhHttp.exportContent(adhMetaApiMock, adhMetaApiMock.objBefore);
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
