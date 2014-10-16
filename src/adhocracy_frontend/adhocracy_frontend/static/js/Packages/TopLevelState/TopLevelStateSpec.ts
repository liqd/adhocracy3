/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhTopLevelState = require("./TopLevelState");
var DEFAULT_FOCUS : number = 1;

export var register = () => {

    describe("TopLevelState", () => {
        describe("TopLevelState", () => {
            var adhTopLevelState : AdhTopLevelState.TopLevelState;
            var eventHandlerMockClass;
            var routeParamMock;
            var locationMock;
            var trigger;
            var off;
            var on;

            beforeEach(() => {
                on = jasmine.createSpy("on");
                off = jasmine.createSpy("off");
                trigger = jasmine.createSpy("trigger");
                locationMock = jasmine.createSpyObj("locationMock", ["url", "search"]);
                routeParamMock = jasmine.createSpyObj("routeParamMock", ["focus"]);

                eventHandlerMockClass = <any>function() {
                    this.on = on;
                    this.off = off;
                    this.trigger = trigger;
                };

                adhTopLevelState = new AdhTopLevelState.TopLevelState(eventHandlerMockClass, locationMock, routeParamMock);
            });

            describe("sets focus", () => {
                it("to 0 if focus param is 0", () => {
                    routeParamMock.focus = 0;
                    var adhTopLevelState = new AdhTopLevelState.TopLevelState(eventHandlerMockClass, locationMock, routeParamMock);
                    expect(adhTopLevelState.getFocus()).toEqual(0);
                });

                it("to 1 if focus param is 1", () => {
                    routeParamMock.focus = 1;
                    var adhTopLevelState = new AdhTopLevelState.TopLevelState(eventHandlerMockClass, locationMock, routeParamMock);
                    expect(adhTopLevelState.getFocus()).toEqual(1);
                });

                it("to 2 if focus param is 2", () => {
                    routeParamMock.focus = 2;
                    var adhTopLevelState = new AdhTopLevelState.TopLevelState(eventHandlerMockClass, locationMock, routeParamMock);
                    expect(adhTopLevelState.getFocus()).toEqual(2);
                });

                it("to default focus if focus param is not a number", () => {
                    routeParamMock.focus = "a";
                    var adhTopLevelState = new AdhTopLevelState.TopLevelState(eventHandlerMockClass, locationMock, routeParamMock);
                    expect(adhTopLevelState.getFocus()).toEqual(DEFAULT_FOCUS);
                });

                it("to default focus if focus param is a long string that is not a number", () => {
                    routeParamMock.focus = new Array(1000).join("a");
                    var adhTopLevelState = new AdhTopLevelState.TopLevelState(eventHandlerMockClass, locationMock, routeParamMock);
                    expect(adhTopLevelState.getFocus()).toEqual(DEFAULT_FOCUS);
                });

                it("to default focus if focus param is missing", () => {
                    var routeParamMock = jasmine.createSpyObj("routeParamMock", [""]);
                    var adhTopLevelState = new AdhTopLevelState.TopLevelState(eventHandlerMockClass, locationMock, routeParamMock);
                    expect(adhTopLevelState.getFocus()).toEqual(DEFAULT_FOCUS);
                });

                it("to default focus if focus param is negative int", () => {
                    routeParamMock.focus = "-1";
                    var adhTopLevelState = new AdhTopLevelState.TopLevelState(eventHandlerMockClass, locationMock, routeParamMock);
                    expect(adhTopLevelState.getFocus()).toEqual(DEFAULT_FOCUS);
                });
            });

            it("dispatches calls to setFocus to eventHandler", () => {
                adhTopLevelState.setFocus(1);
                expect(trigger).toHaveBeenCalledWith("setFocus", 1);
            });

            it("dispatches calls to onSetFocus to eventHandler", () => {
                var callback = (column) => undefined;
                adhTopLevelState.onSetFocus(callback);
                expect(on).toHaveBeenCalledWith("setFocus", callback);
            });

            it("dispatches calls to setContent2Url to eventHandler", () => {
                adhTopLevelState.setContent2Url("some/path");
                expect(trigger).toHaveBeenCalledWith("setContent2Url", "some/path");
            });

            it("dispatches calls to onSetContent2Url to eventHandler", () => {
                var callback = (url) => undefined;
                adhTopLevelState.onSetContent2Url(callback);
                expect(on).toHaveBeenCalledWith("setContent2Url", callback);
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
                topLevelStateMock = <any>jasmine.createSpyObj("topLevelStateMock", ["onSetFocus", "onSetContent2Url", "getFocus"]);
                directive = AdhTopLevelState.movingColumns(topLevelStateMock);
            });

            describe("link", () => {
                var scopeMock;
                var elementMock;

                beforeEach(() => {
                    scopeMock = {};
                    elementMock = <any>jasmine.createSpyObj("elementMock", ["addClass", "removeClass"]);

                    var link = directive.link;
                    link(scopeMock, elementMock);
                });

                describe("onSetFocus", () => {
                    var callback;

                    beforeEach(() => {
                        callback = topLevelStateMock.onSetFocus.calls.mostRecent().args[0];
                    });

                    it("adds class 'is-detail' if columns is 2", () => {
                        callback(2);
                        expect(elementMock.addClass).toHaveBeenCalledWith("is-detail");
                    });

                    it("removes class 'is-detail' if columns is 1", () => {
                        callback(1);
                        expect(elementMock.removeClass).toHaveBeenCalledWith("is-detail");
                    });

                    it("removes class 'is-detail' if columns is 0", () => {
                        callback(0);
                        expect(elementMock.removeClass).toHaveBeenCalledWith("is-detail");
                    });

                    it("does not add or remove class if columns is negative", () => {
                        callback(-1);
                        expect(elementMock.addClass).not.toHaveBeenCalled();
                        expect(elementMock.removeClass).not.toHaveBeenCalled();
                    });

                    it("does not add or remove class if columns is greater 2", () => {
                        callback(3);
                        expect(elementMock.addClass).not.toHaveBeenCalled();
                        expect(elementMock.removeClass).not.toHaveBeenCalled();
                    });


                });

                describe("onSetContent2Url", () => {
                    var callback;

                    beforeEach(() => {
                        callback = topLevelStateMock.onSetContent2Url.calls.mostRecent().args[0];
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
