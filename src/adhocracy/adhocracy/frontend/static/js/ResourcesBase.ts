export interface ISheetMetaApi {
    // meta api flags
    readable : string[];
    editable : string[];
    creatable : string[];
    create_mandatory : string[];

    // computed information
    references : string[];
}


export interface ISheet {
    getMeta() : ISheetMetaApi;
}


export class Resource {
    public data : Object;

    // these path attributes may be undefined or null.
    /* tslint:disable:variable-name */
    public path : string;
    public first_version_path : string;
    public root_versions : string[];
    /* tslint:enable:variable-name */

    constructor(public content_type: string) {
        this.data = {};
    }

    public getReferences() : string[] {
        throw "not implemented";

        /*

           FIXME: traverse all sheets in the resource, call getMeta
           on each, and compute the union of all references.

         */
    }
}
