/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhProposal = require("./Proposal");

export var register = () => {
    describe("Proposal", () => {
        xit("dummy", () => {
            expect(AdhProposal).toBeDefined();
        });
    });
};

