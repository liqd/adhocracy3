/// <reference path="../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhFilters = require("./Filters");

export var register = () => {
    describe("Filters", () => {
        xit("dummy", () => {
            expect(AdhFilters).toBeDefined();
        });
    });
};
