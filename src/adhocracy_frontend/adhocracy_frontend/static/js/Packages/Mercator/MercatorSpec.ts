/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhMercator = require("./Mercator");


export var register = () => {
    describe("Mercator", () => {
        xit("dummy", () => {
            expect(AdhMercator).toBeDefined();
        });
    });
};
