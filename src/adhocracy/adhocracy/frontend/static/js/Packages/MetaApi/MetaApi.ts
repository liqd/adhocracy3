export interface IMetaApi {
    sheets : { [index: string]: ISheet };
    resources : { [index: string]: IResource };
}

export interface ISheet {
    fields : ISheetField[];

    // generated after import
    nick ?: string;
}

export interface ISheetField {
    name : string;
    valuetype : string;
    containertype ?: string;
    readable : boolean;
    editable : boolean;
    creatable : boolean;
    create_mandatory : boolean;
    targetsheet : string;
}

export interface IResource {
    sheets : string[];
    item_type : string;
    element_types : string[];

    // generated after import
    nick ?: string;
}

export interface IModuleDict {
    [index: string]: string;
}

export class MetaApiQuery {
    constructor(public data : IMetaApi) {
    }

    public resource(name : string) : IResource {
        var _self : MetaApiQuery = this;

        if (_self.data.resources.hasOwnProperty(name)) {
            return _self.data.resources[name];
        } else {
            throw "MetaApiQuery: unknown resource named " + name;
        }
    }

    public sheet(name : string) : ISheet {
        var _self : MetaApiQuery = this;

        if (_self.data.sheets.hasOwnProperty(name)) {
            return _self.data.sheets[name];
        } else {
            throw "MetaApiQuery: unknown sheet named " + name;
        }
    }

    public field(sheetName : string, fieldName : string) : ISheetField {
        var _self : MetaApiQuery = this;

        var s = _self.sheet(sheetName);
        if (s.hasOwnProperty(fieldName)) {
            return s[fieldName];
        } else {
            throw "MetaApiQuery: unknown field named " + fieldName + " in sheet " + sheetName;
        }
    }
}
