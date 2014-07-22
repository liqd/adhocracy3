/// <reference path="../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhFilters = require("./Filters");

export var register = () => {
    describe("Filters", () => {
        describe("filterDocumentTitle", () => {
            it("returns the title field from the adhocracy.sheets.document.IDocument sheet", () => {
                var filter = AdhFilters.filterDocumentTitle();
                var title = "a good title";
                var resource = {
                    data: {
                        "adhocracy.sheets.document.IDocument": {
                            title: title
                        }
                    }
                };
                expect(filter(resource)).toBe(title);
            });
        });
    });
};
