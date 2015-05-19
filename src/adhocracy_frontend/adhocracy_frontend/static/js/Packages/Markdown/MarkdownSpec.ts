/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhMarkdown = require("./Markdown");


export var register = () => {
    describe("Markdown", () => {
        xit("exists", () => {
            expect(AdhMarkdown).toBeDefined();
        });
    });
};
