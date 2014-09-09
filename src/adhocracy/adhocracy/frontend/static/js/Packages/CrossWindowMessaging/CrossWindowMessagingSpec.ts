/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import Config = require("../Config/Config");

import CrossWindowMessaging = require("./CrossWindowMessaging");


export var register = () => {

    describe("CrossWindowMessaging", () => {
        var windowMock;
        var rootScopeMock;

        beforeEach(() => {
            windowMock = <any>jasmine.createSpyObj("windowMock", ["addEventListener"]);
            rootScopeMock = <any>jasmine.createSpyObj("rootScopeMock", ["$watch"]);
        });

        describe("Service", () => {
            var postMessageMock;
            var service;

            beforeEach(() => {
                postMessageMock = <any>jasmine.createSpy("postMessageMock");
                service = new CrossWindowMessaging.Service(postMessageMock, windowMock, rootScopeMock);
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
                beforeEach(() => {
                    windowMock.document = {body: {clientHeight: 0}};
                });

                it("registers a resize event listener on $window that calls postMessage", () => {
                    var args = windowMock.addEventListener.calls.mostRecent().args;
                    expect(args[0]).toBe("resize");
                    args[1]();
                    expect(postMessageMock).toHaveBeenCalled();
                });

                it("registers a listener on $rootScope that calls postMessage", () => {
                    var args = rootScopeMock.$watch.calls.mostRecent().args;
                    args[1]();
                    expect(postMessageMock).toHaveBeenCalled();
                });
            });
        });

        describe("Dummy", () => {
            var dummy;

            beforeEach(() => {
                dummy = new CrossWindowMessaging.Dummy();
            });

            it("has a property 'dummy'", () => {
                expect(dummy.dummy).toBeDefined();
            });

            describe("registerMessageHandler", () => {
                it("can be called", () => {
                    expect(() => dummy.registerMessageHandler()).not.toThrow();
                });
            });
            describe("postResize", () => {
                it("can be called", () => {
                    expect(() => dummy.postResize()).not.toThrow();
                });
            });
        });

        describe("factory", () => {
            var service;
            var config : Config.Type;

            beforeEach(() => {
                config = {
                    pkg_path: "mock",
                    root_path: "mock",
                    ws_url: "mock",
                    embedded: true
                };
                windowMock.parent = <any>jasmine.createSpyObj("parentMock", ["postMessage"]);
            });

            it("returns a service instance", () => {
                service = CrossWindowMessaging.factory(config, windowMock, rootScopeMock);
                expect(service).toBeDefined();
            });
            it("returns a dummy service when not embedded", () => {
                config.embedded = false;
                service = CrossWindowMessaging.factory(config, windowMock, rootScopeMock);
                expect(service.dummy).toBeDefined();
            });
            it("returns a service instance that uses $window.parent.postMessage", () => {
                var name = "test";
                var data = {x: "y"};
                service = CrossWindowMessaging.factory(config, windowMock, rootScopeMock);
                service.postMessage(name, data);
                expect(windowMock.parent.postMessage).toHaveBeenCalled();
            });
        });
    });
};
