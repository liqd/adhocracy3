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


export interface IResourceClass {
    /* tslint:disable:variable-name */
    content_type : string;
    super_types : string[];
    sheets : string[];
    /* tslint:enable:variable-name */
}


export interface IResource {
    data : Object;
    path : string;
    parent : string;
    first_version_path : string;
    root_versions : string[];

    isInstanceOf(resourceType : string) : boolean;
}


export class Resource implements IResource {
    public data : Object;

    // these path attributes may be undefined or null.
    /* tslint:disable:variable-name */
    public path : string;
    public parent : string;
    public first_version_path : string;
    public root_versions : string[];
    public static super_types : string[];
    public static sheets : string[];

    constructor(public content_type : string) {
        this.data = {};
    }
    /* tslint:enable:variable-name */

    public isInstanceOf(resourceType : string) : boolean {
        var _class : IResourceClass = <any>this.constructor;

        if (resourceType === this.content_type) {
            return true;
        } else if (_.includes(_class.super_types, resourceType)) {
            return true;
        } else {
            return false;
        }
    }
}
