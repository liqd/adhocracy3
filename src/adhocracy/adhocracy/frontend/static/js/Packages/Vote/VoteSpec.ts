/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhVote = require("./Vote");


export var register = () => {
    describe("Vote", () => {
        xit("dummy", () => {
            expect(AdhVote).toBeDefined();
        });
    });
};
