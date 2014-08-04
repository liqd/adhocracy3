/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhComment = require("./Comment");

export var register = () => {
    describe("Comment", () => {
        xit("dummy", () => {
            expect(AdhComment).toBeDefined();
        });
    });
};
