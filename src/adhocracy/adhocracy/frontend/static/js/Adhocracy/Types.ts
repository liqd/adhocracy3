export interface Content {
    content_type: string;
    path?: string;
    data?: Object;  // FIXME: should this field be mandatory?
    reference_colour?: string;
}

export interface Reference {
    content_type: string;
    path: string;
    reference_colour?: string;
}
