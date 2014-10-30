/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhTopLevelState = require("./TopLevelState");


export var register = () => {

    describe("TopLevelState", () => {
        describe("Service", () => {
            var adhTopLevelState : AdhTopLevelState.Service;
            var eventHandlerMockClass;
            var locationMock;
            var rootScopeMock;
            var trigger;
            var off;
            var on;

            beforeEach(() => {
                on = jasmine.createSpy("on");
                off = jasmine.createSpy("off");
                trigger = jasmine.createSpy("trigger");
                locationMock = jasmine.createSpyObj("locationMock", ["url", "search"]);
                rootScopeMock = jasmine.createSpyObj("rootScopeMock", ["$watch"]);

                eventHandlerMockClass = <any>function() {
                    this.on = on;
                    this.off = off;
                    this.trigger = trigger;
                };

                adhTopLevelState = new AdhTopLevelState.Service(
                    null, eventHandlerMockClass, locationMock, rootScopeMock, null, q, null, null);

                spyOn(adhTopLevelState, "toLocation");
            });

            it("dispatches calls to set() to eventHandler", () => {
                adhTopLevelState.set("content2Url", "some/path");
                expect(trigger).toHaveBeenCalledWith("content2Url", "some/path");
            });

            it("dispatches calls to on() to eventHandler", () => {
                var callback = (url) => undefined;
                adhTopLevelState.on("content2Url", callback);
                expect(on).toHaveBeenCalledWith("content2Url", callback);
            });

            describe("cameFrom", () => {
                it("getCameFrom reads what setCameFrom wrote", () => {
                    var msg : string;
                    msg = "wefoidsut";
                    adhTopLevelState.setCameFrom(msg);
                    expect(adhTopLevelState.getCameFrom()).toBe(msg);
                    msg = ".3587";
                    adhTopLevelState.setCameFrom(msg);
                    expect(adhTopLevelState.getCameFrom()).toBe(msg);
                    expect(adhTopLevelState.getCameFrom()).toBe(msg);
                });

                it("before first setCameFrom, getCameFrom reads 'undefined'", () => {
                    expect(typeof adhTopLevelState.getCameFrom()).toBe("undefined");
                });

                it("clearCameFrom clears the stored value", () => {
                    var msg : string;
                    msg = "wefoidsut";
                    adhTopLevelState.setCameFrom(msg);
                    adhTopLevelState.clearCameFrom();
                    expect(adhTopLevelState.getCameFrom()).not.toBeDefined();
                });

                describe("redirectToCameFrom", () => {
                    it("does nothing if neither cameFrom nor default are set", () => {
                        adhTopLevelState.redirectToCameFrom();
                        expect(locationMock.url).not.toHaveBeenCalled();
                    });

                    it("redirects to cameFrom if cameFrom is set and default is not", () => {
                        adhTopLevelState.setCameFrom("foo");
                        adhTopLevelState.redirectToCameFrom();
                        expect(locationMock.url).toHaveBeenCalledWith("foo");
                    });

                    it("redirects to cameFrom both if cameFrom and default are set", () => {
                        adhTopLevelState.setCameFrom("foo");
                        adhTopLevelState.redirectToCameFrom("bar");
                        expect(locationMock.url).toHaveBeenCalledWith("foo");
                    });

                    it("redirects to default if default is set but cameFrom not", () => {
                        adhTopLevelState.redirectToCameFrom("bar");
                        expect(locationMock.url).toHaveBeenCalledWith("bar");
                    });
                });
            });
        });

        describe("MovingColumns", () => {
            var directive;
            var topLevelStateMock;

            beforeEach(() => {
                topLevelStateMock = <any>jasmine.createSpyObj("topLevelStateMock", ["on", "get"]);
                directive = AdhTopLevelState.movingColumns(topLevelStateMock);
                topLevelStateMock.get.and.callFake((key) => {
                    return {
                        space: "space",
                        movingColumns: "initial"
                    }[key];
                });
            });

            describe("link", () => {
                var scopeMock;
                var elementMock;
                var attrsMock;

                beforeEach(() => {
                    scopeMock = {};
                    attrsMock = {
                        space: "space"
                    };
                    elementMock = <any>jasmine.createSpyObj("elementMock", ["addClass", "removeClass"]);

                    var link = directive.link;
                    link(scopeMock, elementMock, attrsMock);
                });

                describe("on MovingColumns", () => {
                    var callback;

                    beforeEach(() => {
                        callback = topLevelStateMock.on.calls.argsFor(1)[1];
                    });

                    it("adds class 'is-collapse-show-show' if state is collapse-show-show", () => {
                        callback("is-collapse-show-show");
                        expect(elementMock.addClass).toHaveBeenCalledWith("is-collapse-show-show");
                    });

                    it("removes class 'is-collapse-show-show' if columns is show-show-hide", () => {
                        callback("is-collapse-show-show");
                        callback("is-show-show-hide");
                        expect(elementMock.removeClass).toHaveBeenCalledWith("is-collapse-show-show");
                    });

                    it("adds class 'is-show-show-hide' if state is show-show-hide", () => {
                        callback("is-show-show-hide");
                        expect(elementMock.addClass).toHaveBeenCalledWith("is-show-show-hide");
                    });

                    it("removes class 'is-show-show-hide' if columns is show-show-hide", () => {
                        callback("is-show-show-hide");
                        callback("is-collapse-show-show");
                        expect(elementMock.removeClass).toHaveBeenCalledWith("is-show-show-hide");
                    });
                });

                describe("on Content2Url", () => {
                    var callback;

                    beforeEach(() => {
                        callback = topLevelStateMock.on.calls.argsFor(0)[1];
                    });

                    it("sets content2Url in scope", () => {
                        callback("some/path");
                        expect(scopeMock.content2Url).toBe("some/path");
                    });
                });
            });
        });
    });
};
