export interface Content<Data> {
    content_type: string;
    path?: string;
    first_version_path?: string;
    data: Data;
}
