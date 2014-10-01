/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhPermissions = require("./Permissions");

export var register = () => {
    describe("Permissions", () => {
        xit("dummy", () => {
            expect(AdhPermissions).toBeDefined();
        });
    });
};
