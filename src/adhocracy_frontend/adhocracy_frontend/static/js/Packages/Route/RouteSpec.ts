/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhRoute = require("./Route");


export var register = () => {
    describe("Route", () => {
        xit("dummy", () => {
            expect(AdhRoute).toBeDefined();
        });
    });
};
