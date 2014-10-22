import _ = require("lodash");

import AdhUtil = require("./Packages/Util/Util");


export interface ISheetMetaApi {
    // meta api flags
    readable : string[];
    editable : string[];
    creatable : string[];
    create_mandatory : string[];

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

    constructor(public content_type: string) {
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


/**
 * Create an IDag<Resource> out of given resources.
 *
 * FIXME: this should probably go into something like ResourcesUtil or Packages/Resources/Util
 */
export function sortResourcesTopologically(resources : Resource[], adhPreliminaryNames) : Resource[] {
    "use strict";

    // prepare DAG
    // sources are resource paths without incoming references
    var dag : AdhUtil.IDag<Resource> = (<any>_).object(_.map(resources, (resource) => [resource.path, {
            content: resource, incoming: [], outgoing: [], done: false
    }]));
    var sources : string[] = [];

    // fill edges, determine possible starter sources
    _.forEach(dag, (vertex : AdhUtil.IVertex<Resource>, key, l) => {
        var references = vertex.content.getReferences();

        if (typeof vertex.content.parent !== "undefined") {
            references.push(vertex.content.parent);
        }

        references = _.uniq(references);
        references = _.filter(references, adhPreliminaryNames.isPreliminary);

        dag[key].incoming = references;

        if (_.isEmpty(references)) {
            sources.push(key);
        }

        _.forEach(references, (reference) => {
            dag[reference].outgoing.push(key);
        });
    });

    return AdhUtil.sortDagTopologically(dag, sources);
}
