/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import CrossWindowMessaging = require("./CrossWindowMessaging");

export var register = () => {

    describe("Services/CrossWindowMessaging", () => {
        var windowMock;
        var intervalMock;

        beforeEach(() => {
            windowMock = <any>jasmine.createSpyObj("windowMock", ["addEventListener"]);
            intervalMock = jasmine.createSpy("intervalMock");
        });

        describe("Service", () => {
            var postMessageMock;
            var service;

            beforeEach(() => {
                postMessageMock = <any>jasmine.createSpy("postMessageMock");
                service = new CrossWindowMessaging.Service(postMessageMock, windowMock, intervalMock);
            });

            describe("registerMessageHandler", () => {
                var callbackMock;
                var args;

                beforeEach(() => {
                    callbackMock = jasmine.createSpy("callbackMock");
                    service.registerMessageHandler("test", callbackMock);

                    args = windowMock.addEventListener.calls.mostRecent().args;
                });

                it("registers a message event handler", () => {
                    expect(args[0]).toBe("message");
                });

                it("calls callback with message.data when event is triggered", () => {
                    var data = {x: "y"};
                    var message = {
                        name: "test",
                        data: data
                    };
                    var event = {
                        origin: "*",
                        data: JSON.stringify(message)
                    };

                    args[1](event);
                    expect(callbackMock).toHaveBeenCalledWith(data);
                });
            });

            describe("postMessage", () => {
                it("calls window.postMessage with given resize parameters", () => {

                    service.postResize(280);
                    var args = postMessageMock.calls.mostRecent().args;
                    expect(JSON.parse(args[0])).toEqual({
                        name: "resize",
                        data: {height: 280}
                    });
                });
            });

            describe("setup", () => {
                it("sets up the service", () => {
                    var embedderOrigin = "http://embedder.lan";
                    service.setup({embedderOrigin: embedderOrigin});
                    expect(service.embedderOrigin).toBe(embedderOrigin);
                });
                it("ignores subsequent calls", () => {
                    var embedderOrigin1 = "http://embedder.lan";
                    var embedderOrigin2 = "http://evil.lan";
                    service.setup({embedderOrigin: embedderOrigin1});
                    service.setup({embedderOrigin: embedderOrigin2});
                    expect(service.embedderOrigin).toBe(embedderOrigin1);
                });
            });

            describe("manageResize", () => {
                it("registers a callback to be executed every 100 msec", () => {
                    service.manageResize();
                    var args = intervalMock.calls.mostRecent().args;
                    expect(args[1]).toBe(100);
                });

                describe("postResizeIfChange", () => {
                    beforeEach(() => {
                        service.postResize = jasmine.createSpy("postResize");
                        windowMock.document = {body: {clientHeight: 0}};
                    });

                    var run = () => {
                        service.manageResize();
                        var args = intervalMock.calls.mostRecent().args;
                        args[0]();
                    };

                    it("does not call postResize if body height has not changed", () => {
                        run();
                        expect(service.postResize).not.toHaveBeenCalled();
                    });

                    it("calls postResize if body height has changed", () => {
                        windowMock.document.body.clientHeight++;
                        run();
                        expect(service.postResize).toHaveBeenCalled();
                    });
                });
            });
        });

        describe("factory", () => {
            var service;

            beforeEach(() => {
                windowMock.parent = <any>jasmine.createSpyObj("parentMock", ["postMessage"]);
                service = CrossWindowMessaging.factory(windowMock, intervalMock);
            });

            it("returns a service instance", () => {
                expect(service).toBeDefined();
            });
            it("returns a service instance that uses $window.parent.postMessage", () => {
                var name = "test";
                var data = {x: "y"};
                service.postMessage(name, data);
                expect(windowMock.parent.postMessage).toHaveBeenCalled();
            });
        });
    });
};
