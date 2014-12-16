/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhAngularHelpers = require("./AngularHelpers");

export var register = () => {
    describe("AngularHelpers", () => {
        xit("dummy", () => {
            expect(AdhAngularHelpers).toBeDefined();
        });
    });
};
