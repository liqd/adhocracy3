/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhMetaApi = require("./MetaApi");

var sampleMetaApi : AdhMetaApi.IMetaApi = {
    "resources" : {
        "adhocracy.resources.root.IRootPool" : {
            "sheets" : [
                "adhocracy.sheets.name.IName",
                "adhocracy.sheets.pool.IPool",
                "adhocracy.sheets.metadata.IMetadata"
            ],
            "element_types" : [
                "adhocracy.interfaces.IPool"
            ]
        }
    },
    "sheets" : {
        "adhocracy.sheets.metadata.IMetadata" : {
            "fields" : [
                {
                    "name" : "creator",
                    "readable" : true,
                    "editable" : false,
                    "create_mandatory" : false,
                    "valuetype" : "adhocracy.schema.AbsolutePath",
                    "targetsheet" : "adhocracy.sheets.user.IUserBasic",
                    "containertype" : "list",
                    "creatable" : false
                },
                {
                    "create_mandatory" : false,
                    "creatable" : false,
                    "readable" : true,
                    "editable" : false,
                    "valuetype" : "adhocracy.schema.DateTime",
                    "name" : "creation_date"
                },
                {
                    "editable" : false,
                    "readable" : true,
                    "create_mandatory" : false,
                    "creatable" : false,
                    "valuetype" : "adhocracy.schema.DateTime",
                    "name" : "modification_date"
                }
            ]
        },
        "adhocracy.sheets.name.IName" : {
            "fields" : [
                {
                    "readable" : true,
                    "editable" : false,
                    "create_mandatory" : true,
                    "creatable" : true,
                    "valuetype" : "adhocracy.schema.Name",
                    "name" : "name"
                }
            ]
        },
        "adhocracy.sheets.pool.IPool" : {
            "fields" : [
                {
                    "name" : "elements",
                    "create_mandatory" : false,
                    "readable" : true,
                    "editable" : false,
                    "valuetype" : "adhocracy.schema.AbsolutePath",
                    "targetsheet" : "adhocracy.interfaces.ISheet",
                    "containertype" : "list",
                    "creatable" : false
                }
            ]
        }
    }
};


export var register = () => {
    describe("MetaApi", () => {
        var adhMetaApi : AdhMetaApi.MetaApiQuery;

        beforeEach(() => {
            adhMetaApi = new AdhMetaApi.MetaApiQuery(sampleMetaApi);
        });

        it("works!", () => {
            expect(adhMetaApi.field("adhocracy.sheets.pool.IPool", "elements").name).toBe("elements");
            expect(adhMetaApi.field("adhocracy.sheets.pool.IPool", "elements").editable).toBe(false);
        });
    });
};
