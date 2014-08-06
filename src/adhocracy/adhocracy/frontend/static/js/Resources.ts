/* tslint:disable:no-unused-variable */
import Resources_ = require("Resources_");
/* tslint:enable:no-unused-variable */

export interface Content<Data> {
    content_type: string;
    path?: string;
    first_version_path?: string;
    root_versions?: string;
    data: Data;
}
