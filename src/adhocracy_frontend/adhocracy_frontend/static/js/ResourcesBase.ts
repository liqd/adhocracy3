export interface ISheetMetaApi {
    // meta api flags
    readable : string[];
    editable : string[];
    creatable : string[];
    /* tslint:disable:variable-name */
    create_mandatory : string[];
    /* tslint:enable:variable-name */

    // computed information
    references : string[];
}


export class Sheet {
    public getMeta() : ISheetMetaApi {
        return (<any>this).constructor._meta;
    }
}


export class Resource {
    public data : Object;

    // these path attributes may be undefined or null.
    /* tslint:disable:variable-name */
    public path : string;
    public parent : string;
    public first_version_path : string;
    public root_versions : string[];
    /* tslint:enable:variable-name */

    constructor(public content_type : string) {
        this.data = {};
    }

    public getReferences() : string[] {
        var _self = this;
        var result : string[] = [];

        for (var x in _self.data) {
            if (_self.data.hasOwnProperty(x)) {
                var sheet = _self.data[x];
                result.push.apply(result, sheet.getMeta().references);
            }
        }

        return result;
    }
}
