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
