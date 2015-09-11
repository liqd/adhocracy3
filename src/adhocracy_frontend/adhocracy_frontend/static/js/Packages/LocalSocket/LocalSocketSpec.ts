/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import * as AdhWebSocket from "./LocalSocket";


export var register = () => {
    describe("WebSocket", () => {
        xit("exists", () => {
            expect(AdhWebSocket).toBeDefined();
        });
    });
};
