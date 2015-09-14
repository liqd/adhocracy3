/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import * as AdhAngularHelpers from "./AngularHelpers";

export var register = () => {
    describe("AngularHelpers", () => {
        xit("dummy", () => {
            expect(AdhAngularHelpers).toBeDefined();
        });
    });
};
