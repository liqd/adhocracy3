/// <reference path="../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../lib/DefinitelyTyped/q/Q.d.ts"/>

// This is only used at compile time and will be stripped by the compiler
import Config = require("./Services/Config");

import Util = require("./Util");
import q = require("q");

// the module under test
import Widgets = require("./Widgets");


var config : Config.Type = {
    templatePath: "mock",
    jsonPrefix: "mock",
    wsuri: "mock"
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
    describe("Widgets", () => {
        describe("AbstractListingContainerAdapter", () => {
            describe("elemRefs", () => {
                it("always returns an empty list", () => {
                    var adapter = new Widgets.AbstractListingContainerAdapter();
                    expect(adapter.elemRefs(undefined)).toEqual([]);
                    expect(adapter.elemRefs({"a": true})).toEqual([]);
                });
            });
        });

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
                    var adapter = new Widgets.ListingPoolAdapter();
                    expect(adapter.elemRefs(<any>container)).toEqual(elements);
                });
            });
        });

        describe("Listing", () => {
            it("has property 'templateUrl'", () => {
                expect(Widgets.Listing.templateUrl).toBeDefined();
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

                var adapter = <any>jasmine.createSpyObj("adapter", ["elemRefs"]);
                adapter.elemRefs.andReturn(elements);

                var listing = new Widgets.Listing(adapter);
                var directive: ng.IDirective = listing.createDirective(config);

                registerDirectiveSpec(directive);

                it("should transclude", () => {
                    expect(directive.transclude).toBe(true);
                });

                describe("controller", () => {
                    var adhHttpMock = createAdhHttpMock();
                    adhHttpMock.get.andCallFake(() => Util.mkPromise(q, container));

                    it("sets scope.container", () => {
                        var asyncFlag = false;

                        var scope = {
                            container: undefined,
                            elements: undefined
                        };

                        runs(() => {
                            var controller = directive.controller[3];
                            controller(scope, adhHttpMock, () => {
                                asyncFlag = true;
                            });
                        });

                        waitsFor(() => asyncFlag, "timed out", 20);

                        runs(() => {
                            expect(scope.container).toEqual(container);
                        });
                    });

                    it("sets scope.elements", () => {
                        var asyncFlag = false;

                        var scope = {
                            container: undefined,
                            elements: undefined
                        };

                        runs(() => {
                            var controller = directive.controller[3];
                            controller(scope, adhHttpMock, () => {
                                asyncFlag = true;
                            });
                        });

                        waitsFor(() => asyncFlag, "timed out", 20);

                        runs(() => {
                            expect(scope.elements).toEqual(elements);
                        });
                    });
                });
            });
        });

        describe("AbstractListingElementAdapter", () => {
            var adapter = new Widgets.AbstractListingElementAdapter(q);

            describe("name", () => {
                it("always promises ''", () => {
                    var asyncFlag = false;
                    var ret;

                    runs(() => {
                        adapter.name({}).then((value) => {
                            ret = value;
                            asyncFlag = true;
                        });
                    });

                    waitsFor(() => asyncFlag, "timed out", 20);

                    runs(() => {
                        expect(ret).toBe("");
                    });
                });
            });

            describe("path", () => {
                it("always returns ''", () => {
                    expect(adapter.path({})).toBe("");
                });
            });
        });

        describe("ListingElementAdapter", () => {
            var adapter = new Widgets.ListingElementAdapter(q);

            var element = {
                path: "/this/is/a/path",
                content_type: "test",
                data: undefined
            };

            describe("name", () => {
                it("promises the right name", () => {
                    var asyncFlag = false;
                    var ret;

                    runs(() => {
                        adapter.name(element).then((value) => {
                            ret = value;
                            asyncFlag = true;
                        });
                    });

                    waitsFor(() => asyncFlag, "timed out", 20);

                    runs(() => {
                        expect(ret).toBe("[content type test, resource /this/is/a/path]");
                    });
                });
            });

            describe("path", () => {
                it("returns the right path", () => {
                    expect(adapter.path(element)).toBe(element.path);
                });
            });
        });

        describe("ListingElementTitleAdapter", () => {
            var _title = "foobar";
            var latestVersionPath = "latest/version/path";
            var resource = {
                path: "/this/is/a/path",
                content_type: "test",
                data: {
                    "adhocracy.sheets.versions.IVersions": {
                        elements: [latestVersionPath]
                    }
                }
            };
            var version = {
                path: "/this/is/a/path",
                content_type: "test",
                data: {
                    "adhocracy.sheets.document.IDocument": {
                        "title": _title
                    }
                }
            };

            describe("name", () => {
                it("promises the title of the last document version", () => {
                    var asyncFlag = false;
                    var ret;

                    var adhHttpMock = createAdhHttpMock();
                    adhHttpMock.get.andReturn(Util.mkPromise(q, version));

                    var adapter = new Widgets.ListingElementTitleAdapter(q, adhHttpMock);

                    runs(() => {
                        adapter.name(resource).then((value) => {
                            ret = value;
                            asyncFlag = true;
                        });
                    });

                    waitsFor(() => asyncFlag, "timed out", 20);

                    runs(() => {
                        expect(ret).toBe(_title);
                        expect(adhHttpMock.get).toHaveBeenCalledWith(latestVersionPath);
                    });
                });
            });

            describe("path", () => {
                it("returns the right path", () => {
                    var adhHttpMock = createAdhHttpMock();
                    var adapter = new Widgets.ListingElementTitleAdapter(q, adhHttpMock);

                    expect(adapter.path(<any>resource)).toBe(resource.path);
                });
            });
        });

        describe("ListingElement", () => {
            it("has property 'templateUrl'", () => {
                expect(Widgets.ListingElement.templateUrl).toBeDefined();
            });
            describe("createDirective", () => {
                var elementAdapterMock = <any>jasmine.createSpyObj("elementAdapterMock", ["name"]);
                elementAdapterMock.name.andCallFake((path) => path);

                var listingElement = new Widgets.ListingElement(<any>elementAdapterMock);
                var directive: ng.IDirective = listingElement.createDirective(config);

                registerDirectiveSpec(directive);

                describe("controller", () => {
                    it("sets name in scope", () => {
                        var asyncFlag = false;

                        var path = "/this/is/a/path";
                        var scope = {
                            path: path,
                            name: ""
                        };

                        var adhHttpMock = createAdhHttpMock();
                        adhHttpMock.get.andReturn(Util.mkPromise(q, path));

                        runs(() => {
                            var controller = <any>directive.controller[3];
                            controller(scope, adhHttpMock, () => {
                                asyncFlag = true;
                            });
                        });

                        waitsFor(() => asyncFlag, "timed out", 20);

                        runs(() => {
                            expect(scope.name).toEqual(path);
                            expect(adhHttpMock.get).toHaveBeenCalledWith(path);
                        });
                    });
                });
            });
        });
    });
};
