/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../_all.d.ts"/>

// This is only used at compile time and will be stripped by the compiler
import Config = require("../Config/Config");

import q = require("q");

// the module under test
import Listing = require("./Listing");


var config : Config.Type = {
    pkg_path: "mock",
    root_path: "mock",
    ws_url: "mock",
    embedded: false
};

var createAdhHttpMock = () => {
    return <any>jasmine.createSpyObj("adhHttpMock", ["get"]);

    // FIXME: typescript should know from description file that
    // jasmine has this method!  (there are other instances of the
    // same issue further down.)
};

var registerDirectiveSpec = (directive: ng.IDirective): void => {
    it("has an isolated scope", () => {
        expect(directive.scope).toBeDefined();
    });
    it("is restricted to element", () => {
        expect(directive.restrict).toBe("E");
    });
};


export var register = () => {
    describe("Listing", () => {
        describe("ListingPoolAdapter", () => {
            describe("elemRefs", () => {
                it("returns the elements from the adhocracy.sheets.pool.IPool sheet", () => {
                    var elements = ["foo", "bar", "baz"];
                    var container = {
                        data: {
                            "adhocracy.sheets.pool.IPool": {
                                elements: elements
                            }
                        }
                    };
                    var adapter = new Listing.ListingPoolAdapter();
                    expect(adapter.elemRefs(<any>container)).toEqual(elements);
                });
            });
        });

        describe("Listing", () => {
            it("has property 'templateUrl'", () => {
                expect(Listing.Listing.templateUrl).toBeDefined();
            });

            describe("createDirective", () => {
                var elements = ["foo", "bar", "baz"];
                var container = {
                    data: {
                        "adhocracy.sheets.pool.IPool": {
                            elements: elements
                        }
                    }
                };

                var adhWebSocketMock = <any>jasmine.createSpyObj("WebSocketMock", ["register", "unregister"]);

                var adapter = <any>jasmine.createSpyObj("adapter", ["elemRefs"]);
                adapter.elemRefs.and.returnValue(elements);

                var listing = new Listing.Listing(adapter);
                var directive: ng.IDirective = listing.createDirective(config, adhWebSocketMock);

                registerDirectiveSpec(directive);

                it("should transclude", () => {
                    expect(directive.transclude).toBe(true);
                });

                describe("controller", () => {
                    var adhHttpMock;
                    var scope;

                    beforeEach(() => {
                        adhHttpMock = createAdhHttpMock();
                        adhHttpMock.get.and.callFake(() => q.when(container));

                        scope = {
                            // arbitrary values
                            container: 3,
                            elements: 2,
                            $watch: jasmine.createSpy("$watch")
                        };

                        var controller = directive.controller[2];
                        controller(scope, adhHttpMock);
                    });

                    it("defines scope.show", () => {
                        expect(scope.show).toBeDefined();
                    });

                    it("defines scope.show.createForm", () => {
                        expect(scope.show.createForm).toBeDefined();
                    });

                    it("watches scope.path", () => {
                        expect(scope.$watch).toHaveBeenCalled();
                        expect(scope.$watch.calls.mostRecent().args[0]).toBe("path");
                    });

                    describe("scope.clear", () => {
                        it("clears scope.container", () => {
                            scope.clear();
                            expect(scope.container).not.toBeDefined();
                        });

                        it("clears scope.elements", () => {
                            scope.clear();
                            expect(scope.elements).toEqual([]);
                        });
                    });

                    describe("scope.update", () => {
                        var path = "some/path";

                        beforeEach((done) => {
                            scope.path = path;
                            scope.update().then(done);
                        });

                        it("updates scope.container from server", () => {
                            expect(adhHttpMock.get).toHaveBeenCalledWith(path);
                            expect(scope.container).toBe(container);
                        });

                        it("updates scope.elements using adapter from container", () => {
                            expect(adapter.elemRefs).toHaveBeenCalledWith(container);
                            expect(scope.elements).toBe(elements);
                        });
                    });

                    describe("$watch(path)", () => {
                        var callback;

                        beforeEach(() => {
                            spyOn(scope, "update");
                            spyOn(scope, "clear");
                            callback = scope.$watch.calls.mostRecent().args[1];
                        });

                        it("unregisters old websocket when path changes", () => {
                            scope.wshandle = "wshandle";
                            callback("new/path", "old/path");
                            expect(adhWebSocketMock.unregister).toHaveBeenCalledWith("old/path", "wshandle");
                        });

                        it("registers new websocket when path changes", () => {
                            callback("new/path", "old/path");
                            expect(adhWebSocketMock.register).toHaveBeenCalledWith("new/path", scope.update);
                        });

                        it("calls scope.update on new path", () => {
                            callback("new/path", "old/path");
                            expect(scope.update).toHaveBeenCalled();
                        });

                        it("calls scope.clear on path clear", () => {
                            callback("", "old/path");
                            expect(scope.clear).toHaveBeenCalled();
                        });
                    });

                    it("intializes scope.show.createForm to false", () => {
                        expect(scope.show).toBeDefined();
                        expect(scope.show.createForm).toBeDefined();
                        expect(scope.show.createForm).toBe(false);
                    });

                    describe("showCreateForm", () => {
                        it("sets $scope.show.createForm to true", () => {
                            expect(scope.showCreateForm).toBeDefined();
                            scope.showCreateForm();
                            expect(scope.show.createForm).toBe(true);
                        });
                    });

                    describe("hideCreateForm", () => {
                        it("sets $scope.show.createForm to false", () => {
                            expect(scope.hideCreateForm).toBeDefined();
                            scope.hideCreateForm();
                            expect(scope.show.createForm).toBe(false);
                        });
                    });
                });
            });
        });
    });
};
