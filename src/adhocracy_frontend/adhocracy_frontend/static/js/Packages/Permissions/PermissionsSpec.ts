/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import * as AdhPermissions from "./Permissions";

export var register = () => {
    describe("Permissions", () => {
        xit("dummy", () => {
            expect(AdhPermissions).toBeDefined();
        });
    });
};
