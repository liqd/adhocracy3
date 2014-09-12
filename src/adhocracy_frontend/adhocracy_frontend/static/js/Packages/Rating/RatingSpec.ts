/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhRating = require("./Rating");


export var register = () => {
    describe("Rating", () => {
        xit("dummy", () => {
            expect(AdhRating).toBeDefined();
        });
    });
};
