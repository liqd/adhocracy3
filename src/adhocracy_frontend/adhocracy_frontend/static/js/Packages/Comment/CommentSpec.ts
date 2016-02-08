/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import * as AdhComment from "./Comment";

export var register = () => {
    describe("Comment", () => {
        xit("dummy", () => {
            expect(AdhComment).toBeDefined();
        });
    });
};
