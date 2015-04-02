/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhMapping = require("./Mapping");


export var register = () => {
    describe("Mapping", () => {
        xit("exists", () => {
            expect(AdhMapping).toBeDefined();
        });
    });
};
