/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhProcess = require("./Process");

export var register = () => {
    describe("Tracking", () => {
        xit("is defined", () => {
            expect(AdhProcess).toBeDefined();
        });
    });
};
