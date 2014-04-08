export interface Content {
    content_type: string;
    path?: string;
    first_version_path?: string;
    data?: Object;
    reference_colour?: string;
}

export interface Reference {
    content_type: string;
    path: string;
    reference_colour?: string;
}
