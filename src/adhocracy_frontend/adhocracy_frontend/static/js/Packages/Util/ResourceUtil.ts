import _ = require("lodash");

import ResourcesBase = require("../../ResourcesBase");

import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

import AdhUtil = require("./Util");


/**
 * Create a new version following an existing one.
 */
export var derive = function<R extends ResourcesBase.Resource>(oldVersion : R, settings) : R {
    var resource = new (<any>oldVersion).constructor(settings);

    _.forOwn(oldVersion.data, (sheet, key) => {
        resource.data[key] = new sheet.constructor(settings);

        _.forOwn(sheet, (value, field) => {
            resource.data[key][field] = _.cloneDeep(value);
        });
    });

    resource.data[SIVersionable.nick] = new SIVersionable.Sheet({follows: [oldVersion.path]});

    return resource;
};


export var hasEqualContent = function<R extends ResourcesBase.Resource>(resource1 : R, resource2 : R) : boolean {
    // note: this assumes that both resources share the same set of sheets, as it's currently
    // always used after derive.

    var equal = true;
    _.forOwn(resource1.data, (sheet, key) => {
        var sheet2 = resource2.data[key];

        if (key !== "adhocracy_core.sheets.versions.IVersionable") {
            _.forOwn(sheet, (value, field) => {
                if (!_.isEqual(value, sheet2[field])) {
                    equal = false;
                }
            });
        }
    });
    return equal;
};


/**
 * Create an IDag<Resource> out of given resources.
 *
 * FIXME: this should probably go into something like ResourcesUtil or Packages/Resources/Util
 */
export function sortResourcesTopologically(resources : ResourcesBase.Resource[], adhPreliminaryNames) : ResourcesBase.Resource[] {
    "use strict";

    // prepare DAG
    // sources are resource paths without incoming references
    var dag : AdhUtil.IDag<ResourcesBase.Resource> = (<any>_).object(_.map(resources, (resource) => [resource.path, {
            content: resource, incoming: [], outgoing: [], done: false
    }]));
    var sources : string[] = [];

    // fill edges, determine possible starter sources
    _.forEach(dag, (vertex : AdhUtil.IVertex<ResourcesBase.Resource>, key, l) => {
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
