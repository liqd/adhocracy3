/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhWebSocket = require("./LocalSocket");


export var register = () => {
    describe("WebSocket", () => {
        xit("exists", () => {
            expect(AdhWebSocket).toBeDefined();
        });
    });
};
