/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import * as AdhProcess from "./Process";

export var register = () => {
    describe("Process", () => {
        xit("is defined", () => {
            expect(AdhProcess).toBeDefined();
        });
    });
};
