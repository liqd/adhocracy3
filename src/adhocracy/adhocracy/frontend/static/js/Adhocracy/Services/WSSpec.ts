/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/q/Q.d.ts"/>

import Config = require("./Config");
import Util = require("../Util");
import WS = require("./WS");

declare var beforeEach : (any) => void;

export var register = () => {
    describe("Services/WS", () => {
        var config: Config.Type = {
            templatePath: "mock",
            jsonPrefix: "mock",
            wsuri: "mock"
        };

        // constructor for a mock raw web socket that leaks the
        // constructee for inspection.
        var wsRaw: any;
        var constructRawWebSocket = (uri: string): WS.RawWebSocket => {
            wsRaw = <any>jasmine.createSpyObj("RawWebSocketMock", ["send", "onmessage", "onerror", "onopen", "onclose"]);
            return wsRaw;
        };

        var ws = WS.factory(config, constructRawWebSocket);

        it("at this point, the send method of web socket should never have been called", () => {
            expect(wsRaw.send.calls.any()).toEqual(false);
        });

        it("first registration yields '0' as callback handle", () => {
            expect(ws.register("/adhocracy", () => null)).toEqual("0");
        });

        it("second registration yields '1' as callback handle", () => {
            expect(ws.register("/adhocracy/somethingelse", () => null)).toEqual("1");
        });

        it("at this point, the send method of web socket should have been called twice", () => {
            expect(wsRaw.send.calls.count()).toEqual(2);
        });

        it("callbacks should be called only between being registered and being unregistered", () => {
            // register spy object as callback
            var cb = {
                cb: (event) => null
            };
            (<any>spyOn(cb, "cb")).and.callThrough();
            var handle = ws.register("/adhocracy/somethingactive", cb.cb);

            expect((<any>cb.cb).calls.count()).toEqual(0);

            // trigger event
            wsRaw.onmessage({ data: JSON.stringify({
                resource: "/adhocracy/somethingactive",
                event: "new_child",
                child: "/adhocracy/somethingactive/fiyudt8y"
            }, null, 2)});

            expect((<any>cb.cb).calls.count()).toEqual(1);

            // unregister callback
            ws.unregister("/adhocracy/somethingactive", handle);

            // trigger another event
            wsRaw.onmessage({ data: JSON.stringify({
                resource: "/adhocracy/somethingactive",
                event: "new_child",
                child: "/adhocracy/somethingactive/q2u7"
            }, null, 2)});

            expect((<any>cb.cb).calls.count()).toEqual(1);
        });

        xit("un-registration of a non-existing handle triggers an exception", () => {
            expect(ws.unregister("/adhocracy/somethingelse", '81')).toThrow();
        });
    });
};
