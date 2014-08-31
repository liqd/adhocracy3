/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhResourceWidgets = require("./ResourceWidgets");


var getArgsByFirst = (spy, needle) => {
    var haystack = spy.calls.allArgs();
    return haystack.filter((args) => args[0] === needle);
};

export var register = () => {
    describe("ResourceWidgets", () => {
        describe("resourceWrapper", () => {
            var directive;

            beforeEach(() => {
                directive = AdhResourceWidgets.resourceWrapper(q);
            });

            describe("link", () => {
                var scopeMock;

                beforeEach(() => {
                    scopeMock = jasmine.createSpyObj("scope", ["$on", "$broadcast"]);
                    directive.link(scopeMock);
                });

                it("does not pollute the scope", () => {
                    expect(scopeMock).toEqual({
                        $on: jasmine.any(Function),
                        $broadcast: jasmine.any(Function)
                    });
                });

                describe("on registerResourceDirective", () => {
                    var fn;
                    var ev;

                    beforeEach(() => {
                        fn = getArgsByFirst(scopeMock.$on, "registerResourceDirective")[0][1];
                        ev = jasmine.createSpyObj("event", ["stopPropagation"]);
                    });

                    it("stops event propagation", () => {
                        fn(ev, "promise");
                        expect(ev.stopPropagation).toHaveBeenCalled();
                    });

                    xit("stores the passed promise", () => {
                        throw "untestable";
                    });
                });

                describe("on triggerSubmit", () => {
                    var ev;

                    beforeEach(() => {
                        var fn = getArgsByFirst(scopeMock.$on, "triggerSubmit")[0][1];
                        ev = jasmine.createSpyObj("event", ["stopPropagation"]);
                        fn(ev);
                    });

                    it("stops event propagation", () => {
                        expect(ev.stopPropagation).toHaveBeenCalled();
                    });

                    it("broadcasts a 'submit' event", () => {
                        expect(scopeMock.$broadcast).toHaveBeenCalledWith("submit");
                    });
                });

                describe("on triggerCancel", () => {
                    var ev;

                    beforeEach(() => {
                        var fn = getArgsByFirst(scopeMock.$on, "triggerCancel")[0][1];
                        ev = jasmine.createSpyObj("event", ["stopPropagation"]);
                        fn(ev);
                    });

                    it("stops event propagation", () => {
                        expect(ev.stopPropagation).toHaveBeenCalled();
                    });

                    it("broadcasts a 'cancel' event", () => {
                        expect(scopeMock.$broadcast).toHaveBeenCalledWith("cancel");
                    });
                });

                describe("on triggerSetMode", () => {
                    var ev;

                    beforeEach(() => {
                        var fn = getArgsByFirst(scopeMock.$on, "triggerSetMode")[0][1];
                        ev = jasmine.createSpyObj("event", ["stopPropagation"]);
                        fn(ev, "mode");
                    });

                    it("stops event propagation", () => {
                        expect(ev.stopPropagation).toHaveBeenCalled();
                    });

                    it("broadcasts a 'setMode' event with mode as first parameter", () => {
                        expect(scopeMock.$broadcast).toHaveBeenCalledWith("setMode", "mode");
                    });
                });
            });
        });

        describe("ResourceWidget", () => {
            var adhHttpMock;
            var adhPreliminaryNamesMock;
            var resourceWidget;

            beforeEach(() => {
                adhHttpMock = jasmine.createSpyObj("adhHttp", ["get"]);
                adhHttpMock.get.and.returnValue(q.when());

                adhPreliminaryNamesMock = jasmine.createSpyObj("adhPreliminaryNames", ["isPreliminary"]);
                adhPreliminaryNamesMock.isPreliminary.and.returnValue(false);

                resourceWidget = new AdhResourceWidgets.ResourceWidget(adhHttpMock, adhPreliminaryNamesMock, q);
            });

            describe("constructor", () => {
                it("sets this.deferred", () => {
                    expect(resourceWidget.deferred).toBeDefined();
                });
            });

            describe("createDirective", () => {
                var directive;

                beforeEach(() => {
                    resourceWidget.templateUrl = "templateUrl";
                    directive = resourceWidget.createDirective();
                });

                it("sets the templateUrl", () => {
                    expect(directive.templateUrl).toBe("templateUrl");
                });

                describe("link", () => {
                    var scopeMock;

                    beforeEach(() => {
                        scopeMock = jasmine.createSpyObj("scope", ["$on", "$emit", "$broadcast"]);
                        resourceWidget.update = jasmine.createSpy("update").and.returnValue(q.when());
                        resourceWidget.setMode = jasmine.createSpy("setMode").and.returnValue(q.when());
                        resourceWidget._handleDelete = jasmine.createSpy("_handleDelete").and.returnValue(q.when());
                        resourceWidget._provide = jasmine.createSpy("_provide").and.returnValue(q.when());
                        directive.link(scopeMock);
                    });

                    it("calls update", () => {
                        expect(resourceWidget.update).toHaveBeenCalled();
                    });

                    describe("on $delete", () => {
                        it("resolves the promise that is registered with resourceWrapper with an empty list", () => {
                            var fn = getArgsByFirst(scopeMock.$on, "$delete")[0][1];
                            resourceWidget.deferred.resolve = jasmine.createSpy("resolve");
                            fn("event");
                            expect(resourceWidget.deferred.resolve).toHaveBeenCalledWith([]);
                        });
                    });

                    describe("on submit", () => {
                        it("calls provide and resolves the promise with the result", (done) => {
                            var fn = getArgsByFirst(scopeMock.$on, "submit")[0][1];
                            resourceWidget._provide.and.returnValue(q.when("provided"));

                            fn().then(() => {
                                expect(resourceWidget._provide).toHaveBeenCalled();

                                resourceWidget.deferred.promise.then((promised) => {
                                    expect(promised).toBe("provided");
                                    done();
                                });
                            });
                        });
                    });

                    describe("on cancel", () => {
                        var fn;

                        beforeEach(() => {
                            fn = getArgsByFirst(scopeMock.$on, "cancel")[0][1];
                        });

                        it("resets scope and sets mode to display if scope.mode is edit", (done) => {
                            scopeMock.mode = AdhResourceWidgets.Mode.edit;
                            fn().then(() => {
                                expect(resourceWidget.update.calls.count()).toBe(2);
                                expect(resourceWidget.setMode).toHaveBeenCalled();
                                done();
                            });
                        });

                        it("does not call update and does not change mode if mode is not edit", (done) => {
                            scopeMock.mode = "foo";
                            fn().then(() => {
                                expect(resourceWidget.update.calls.count()).toBe(1);
                                expect(resourceWidget.setMode).not.toHaveBeenCalled();
                                done();
                            });
                        });
                    });

                    describe("on setMode", () => {
                        it("calls setMode with first parameter", () => {
                            var fn = getArgsByFirst(scopeMock.$on, "setMode")[0][1];
                            fn("event", "mode");
                            expect(resourceWidget.setMode).toHaveBeenCalledWith(scopeMock, "mode");
                        });
                    });

                    describe("on triggerDelete", () => {
                        it("calls _handleDelete with first parameter", () => {
                            var fn = getArgsByFirst(scopeMock.$on, "triggerDelete")[0][1];
                            fn("event", "path");
                            expect(resourceWidget._handleDelete).toHaveBeenCalledWith(scopeMock, "path");
                        });
                    });

                    describe("edit", () => {
                        it("uses setMode to switch to edit mode", () => {
                            scopeMock.edit();
                            expect(resourceWidget.setMode).toHaveBeenCalledWith(scopeMock, AdhResourceWidgets.Mode.edit);
                        });
                    });

                    describe("submit", () => {
                        it("emits a 'triggerSubmit' event", () => {
                            scopeMock.submit();
                            expect(scopeMock.$emit).toHaveBeenCalledWith("triggerSubmit");
                        });
                    });

                    describe("cancel", () => {
                        it("emits a 'triggerCancel' event", () => {
                            scopeMock.cancel();
                            expect(scopeMock.$emit).toHaveBeenCalledWith("triggerCancel");
                        });
                    });

                    describe("delete", () => {
                        it("emits a 'triggerDelete' event with scope.path as first parameter", () => {
                            scopeMock.path = "/some/path";
                            scopeMock.delete();
                            expect(scopeMock.$emit).toHaveBeenCalledWith("triggerDelete", "/some/path");
                        });
                    });
                });
            });

            describe("setMode", () => {
                var scopeMock;

                beforeEach(() => {
                    scopeMock = jasmine.createSpyObj("scope", ["$emit"]);
                });

                it("sets scope.mode", () => {
                    resourceWidget.setMode(scopeMock, 15);
                    expect((<any>scopeMock).mode).toBe(15);
                });

                it("allows to set mode by string", () => {
                    resourceWidget.setMode(scopeMock, "edit");
                    expect((<any>scopeMock).mode).toBe(1);
                });

                it("defults to display mode", () => {
                    resourceWidget.setMode(scopeMock);
                    expect((<any>scopeMock).mode).toBe(0);
                });

                it("resolves the promise that is registered with resourceWrapper with an empty list", () => {
                    resourceWidget.deferred.resolve = jasmine.createSpy("resolve");
                    resourceWidget.setMode(scopeMock, AdhResourceWidgets.Mode.display);
                    expect(resourceWidget.deferred.resolve).toHaveBeenCalledWith([]);
                });

                it("creates a new promise and registers it with resourceWrapper using a 'registerResourceDirective' event", () => {
                    spyOn(q, "defer").and.callThrough();
                    resourceWidget.setMode(scopeMock, AdhResourceWidgets.Mode.edit);
                    expect(q.defer).toHaveBeenCalled();
                    expect(scopeMock.$emit).toHaveBeenCalledWith("registerResourceDirective", jasmine.any(Object));
                });
            });

            describe("update", () => {
                var scopeMock;

                beforeEach(() => {
                    scopeMock = {};
                    resourceWidget._update = jasmine.createSpy("_update");
                });

                it("does not call adhHttp.get or _update when scope.path is preliminary", (done) => {
                    adhPreliminaryNamesMock.isPreliminary.and.returnValue(true);
                    resourceWidget.update(scopeMock).then(() => {
                        expect(adhHttpMock.get).not.toHaveBeenCalled();
                        expect(resourceWidget._update).not.toHaveBeenCalled();
                        done();
                    });
                });

                it("does get scope.path from server and feed it to _update", (done) => {
                    adhPreliminaryNamesMock.isPreliminary.and.returnValue(false);
                    scopeMock.path = "/some/path";
                    resourceWidget.update(scopeMock).then(() => {
                        expect(adhHttpMock.get).toHaveBeenCalledWith("/some/path");
                        expect(resourceWidget._update).toHaveBeenCalled();

                        done();
                    });
                });
            });

            describe("_handleDelete", () => {
                it("raises an 'not implemented' exception", () => {
                    expect(() => resourceWidget._handleDelete({}, "path")).toThrow();
                });
            });

            describe("_update", () => {
                it("raises an 'not implemented' exception", () => {
                    expect(() => resourceWidget._update({}, "path")).toThrow();
                });
            });

            describe("_provide", () => {
                it("raises an 'not implemented' exception", () => {
                    expect(() => resourceWidget._provide({}, "path")).toThrow();
                });
            });
        });
    });
};
