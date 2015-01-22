/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhConfig = require("../Config/Config");
import AdhWebSocket = require("../WebSocket/WebSocket");


var config: AdhConfig.IService = <any>{
    pkg_path: "mock",
    rest_url: "mock",
    rest_platform_path: "mock",
    ws_url: "mock",
    embedded: false,
    trusted_domains: []
};

export var register = () => {
    describe("WebSocket", () => {
        describe("Service", () => {
            var service;
            var adhEventHandlerClassMock;
            var adhEventHandlerMock;
            var adhRawWebSocketMock;

            beforeEach(() => {
                adhEventHandlerClassMock = function() {
                    this.on = jasmine.createSpy("adhEventHandler.on");
                    this.off = jasmine.createSpy("adhEventHandler.off");
                    this.trigger = jasmine.createSpy("adhEventHandler.trigger");
                    adhEventHandlerMock = this;
                };
                adhRawWebSocketMock = jasmine.createSpyObj("adhRawWebSocketFactory", ["send", "addEventListener"]);

                service = new AdhWebSocket.Service(config, adhEventHandlerClassMock, () => adhRawWebSocketMock);
            });

            it("calls the send method of web socket on every register to different resources", () => {
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(0);
                service.register("/adhocracy", () => null);
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(1);
                service.register("/adhocracy/somethingelse", () => null);
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(2);
            });

            it("sends only one subscription for multiple registrations to same resource", () => {
                var resource = "/adhocracy/sidty";
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(0);
                service.register(resource, () => null);
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(1);
                service.register(resource, () => null);
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(1);
            });

            it("sends an unsubscription if all registrations have been unregistered", () => {
                var resource = "/adhocracy/sidty";
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(0);
                var id1 = service.register(resource, () => null);
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(1);
                var id2 = service.register(resource, () => null);
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(1);
                service.unregister(resource, id1);
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(1);
                service.unregister(resource, id2);
                expect(adhRawWebSocketMock.send.calls.count()).toEqual(2);
            });

            it("throws on unregistration of a not-subscribed resource", () => {
                console.log((<any>service).registrations);
                expect(() => service.unregister("/adhocracy/somethingelse", 0)).toThrow();
            });

            it("calls eventHandler.trigger on event", () => {
                var resource = "/adhocracy/sidty";
                var msg = {
                    resource: resource,
                    event: "new_child",
                    child: resource + "/fiyudt8y"
                };

                adhRawWebSocketMock.onmessage({
                    data: JSON.stringify(msg)
                });
                expect(adhEventHandlerMock.trigger).toHaveBeenCalledWith(resource, msg);
            });

            it("throws an exception on error", () => {
                expect(() => adhRawWebSocketMock.onmessage({
                    data: JSON.stringify({
                        error: "some_error"
                    })
                })).toThrow();

                expect(() => adhRawWebSocketMock.onmessage({
                    data: JSON.stringify({
                        error: "unknown_action"
                    })
                })).toThrow();

                expect(adhEventHandlerMock.trigger).not.toHaveBeenCalled();
            });

            it("resends all subscriptions on WebSocket open", () => {
                var id1 = service.register("resource1", () => null);
                service.unregister("resource1", id1);
                service.register("resource2", () => null);
                service.register("resource2", () => null);

                var calls = adhRawWebSocketMock.send.calls.count();

                adhRawWebSocketMock.onopen();

                expect(adhRawWebSocketMock.send.calls.count()).toBe(calls + 1);
            });
        });
    });
};
