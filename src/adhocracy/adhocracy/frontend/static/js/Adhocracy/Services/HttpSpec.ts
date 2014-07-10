/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhHttp = require("./Http");

export var register = () => {
    describe("Service/Http", () => {
        xit("dummy", () => {
            expect(AdhHttp).toBeDefined();
        });
    });
};
