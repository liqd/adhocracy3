/// <reference path="../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhDirectives = require("./Directives");

export var register = () => {
    describe("Service/Directives", () => {
        xit("dummy", () => {
            expect(AdhDirectives).toBeDefined();
        });
    });
};
