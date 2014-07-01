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

        xit("un-registration of a existing handle makes callback vanish", () => {
            // register spy object as callback
            // trigger event
            // ask spy object for callback count
            // trigger event
            // ask spy object for callback count again
            // both counts should be 1
        });

        xit("un-registration of a non-existing handle triggers an exception", () => {
            expect(ws.unregister("/adhocracy/somethingelse", '81')).toThrow();
        });
    });
};
