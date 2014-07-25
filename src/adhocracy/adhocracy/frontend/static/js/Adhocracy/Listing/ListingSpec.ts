/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../_all.d.ts"/>

// This is only used at compile time and will be stripped by the compiler
import Config = require("../Config/Config");

import q = require("q");

// the module under test
import Listing = require("./Listing");


var config : Config.Type = {
    template_path: "mock",
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
        describe("AbstractListingContainerAdapter", () => {
            describe("elemRefs", () => {
                it("always returns an empty list", () => {
                    var adapter = new Listing.AbstractListingContainerAdapter();
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
                var directive: ng.IDirective = listing.createDirective(config);

                registerDirectiveSpec(directive);

                it("should transclude", () => {
                    expect(directive.transclude).toBe(true);
                });

                describe("controller", () => {
                    var adhHttpMock;
                    var scope;

                    beforeEach((done) => {
                        adhHttpMock = createAdhHttpMock();
                        adhHttpMock.get.and.callFake(() => q.when(container));

                        scope = {
                            container: undefined,
                            elements: undefined
                        };

                        var controller = directive.controller[4];
                        controller(scope, adhHttpMock, adhWebSocketMock, done);
                    });

                    it("sets scope.container", () => {
                        expect(scope.container).toEqual(container);
                    });

                    it("sets scope.elements", () => {
                        expect(scope.elements).toEqual(elements);
                    });
                });
            });
        });
    });
};
