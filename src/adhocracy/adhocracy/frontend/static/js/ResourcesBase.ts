export class Resource {
    public data : Object;

    // these path attributes may be undefined or null.
    /* tslint:disable:variable-name */
    public path : string;
    public first_version_path : string;
    public root_versions : string;
    /* tslint:enable:variable-name */

    constructor(public content_type: string) {
        this.data = {};
    }
}
