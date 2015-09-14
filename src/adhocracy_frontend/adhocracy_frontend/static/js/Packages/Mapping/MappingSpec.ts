/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import * as AdhMapping from "./Mapping";


export var register = () => {
    describe("Mapping", () => {
        xit("exists", () => {
            expect(AdhMapping).toBeDefined();
        });
    });
};
