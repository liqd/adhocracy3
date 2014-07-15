/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhUser = require("./User");

export var register = () => {
    describe("Service/User", () => {
        xit("dummy", () => {
            expect(AdhUser).toBeDefined();
        });
    });
};
