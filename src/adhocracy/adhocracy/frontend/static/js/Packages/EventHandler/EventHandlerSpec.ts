/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhEventHandler = require("./EventHandler");

export var register = () => {
    describe("EventHandler", () => {
        var eventHandler : AdhEventHandler.EventHandler;

        beforeEach(() => {
            eventHandler = new AdhEventHandler.EventHandler();
        });

        it("allows to set handlers for events", () => {
            var spy = jasmine.createSpy("spy");
            eventHandler.on("test", spy);
            eventHandler.trigger("test");
            expect(spy).toHaveBeenCalled();
        });

        it("allow to pass a single argument on trigger", () => {
            var spy = jasmine.createSpy("spy");
            eventHandler.on("test", spy);
            eventHandler.trigger("test", "testArg");
            expect(spy).toHaveBeenCalledWith("testArg");
        });

        it("allows to unregister a single handler", () => {
            var spy1 = jasmine.createSpy("spy1");
            var spy2 = jasmine.createSpy("spy2");
            var id1 = eventHandler.on("test", spy1);
            eventHandler.on("test", spy2);
            eventHandler.off("test", id1);
            eventHandler.trigger("test");
            expect(spy1).not.toHaveBeenCalled();
            expect(spy2).toHaveBeenCalled();
        });

        it("allows to clear all handlers for a single event", () => {
            var spy1 = jasmine.createSpy("spy1");
            var spy2 = jasmine.createSpy("spy2");
            eventHandler.on("test1", spy1);
            eventHandler.on("test2", spy2);
            eventHandler.off("test1");
            eventHandler.trigger("test1");
            eventHandler.trigger("test2");
            expect(spy1).not.toHaveBeenCalled();
            expect(spy2).toHaveBeenCalled();
        });

        it("allows to clear all handlers for all events", () => {
            var spy1 = jasmine.createSpy("spy1");
            var spy2 = jasmine.createSpy("spy2");
            eventHandler.on("test1", spy1);
            eventHandler.on("test2", spy2);
            eventHandler.off();
            eventHandler.trigger("test1");
            eventHandler.trigger("test2");
            expect(spy1).not.toHaveBeenCalled();
            expect(spy2).not.toHaveBeenCalled();
        });
    });
};
