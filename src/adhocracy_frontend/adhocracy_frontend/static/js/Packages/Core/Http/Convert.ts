/// <reference path="../../../../lib2/types/lodash.d.ts"/>

import * as _ from "lodash";

import * as AdhMetaApi from "../MetaApi/MetaApi";
import * as AdhPreliminaryNames from "../PreliminaryNames/PreliminaryNames";

import * as ResourcesBase from "../../../ResourcesBase";

import * as SIMetadata from "../../../Resources_/adhocracy_core/sheets/metadata/IMetadata";
import * as SIPool from "../../../Resources_/adhocracy_core/sheets/pool/IPool";

import * as AdhCache from "./Cache";


var sanityCheck = (obj : ResourcesBase.IResource, adhMetaApi : AdhMetaApi.Service) : void => {
    if (typeof obj !== "object") {
        throw ("unexpected type: " + (typeof obj).toString() + "\nin object:\n" + JSON.stringify(obj, null, 2));
    }

    if (!obj.hasOwnProperty("content_type")) {
        throw ("resource has no content_type field:\n" + JSON.stringify(obj, null, 2));
    }

    if (!adhMetaApi.resourceExists(obj.content_type)) {
        throw ("unknown content_type: " + obj.content_type + "\nin object:\n" + JSON.stringify(obj, null, 2));
    }
};

var importField = (value, field : AdhMetaApi.ISheetField) => {
    var toBoolean = (v) => _.isString(v) ? (v === "true") : v;
    var toInt = (v) => _.isString(v) ? parseInt(v, 10) : v;
    var toFloat = (v) => _.isString(v) ? parseFloat(v) : v;

    var parser = (v) => v;

    // This code should be consistent with the types generated in mkResources
    switch (field.valuetype) {
        case "adhocracy_core.schema.Boolean":
            parser = toBoolean;
            break;
        case "Integer":
        case "adhocracy_core.schema.Integer":
        case "adhocracy_core.schema.Rate":
            parser = toInt;
            break;
        case "adhocracy_core.schema.CurrencyAmount":
        case "adhocracy_core.sheets.geo.WebMercatorLongitude":
        case "adhocracy_core.sheets.geo.WebMercatorLatitude":
            parser = toFloat;
            break;
        case "adhocracy_core.sheets.geo.Point":
            parser = (point) => _.map(point, toFloat);
            break;
        case "adhocracy_core.sheets.geo.Polygon":
            parser = (polygon) => _.map(polygon, (line) => _.map(line, toFloat));
            break;
    }

    if (field.containertype) {
        var singleParser = parser;

        if (field.containertype === "list") {
            parser = (v) => _.map(v, singleParser);
        } else {
            throw new Error("Unknown containertype: " + field.containertype);
        }
    }

    return parser(value);
};

/**
 * transform objects on the way in (all request methods)
 */
export var importResource = (
    response : {data : ResourcesBase.IResource},
    metaApi : AdhMetaApi.Service,
    preliminaryNames : AdhPreliminaryNames.Service,
    adhCache : AdhCache.Service,
    warmupPoolCache : boolean = false,
    originalElements : string = "omit"
) : ResourcesBase.IResource => {
    "use strict";

    var obj = _.cloneDeep(response.data);
    sanityCheck(obj, metaApi);

    if (!obj.hasOwnProperty("path")) {
        throw ("resource has no path field: " + JSON.stringify(obj, null, 2));
    }

    _.forOwn(obj.data, (jsonSheet, sheetName) => {
        if (!metaApi.sheetExists(sheetName)) {
            throw ("unknown property sheet: " + sheetName + " " + JSON.stringify(obj, null, 2));
        }

        if (warmupPoolCache && (sheetName === SIPool.nick)) {
            var elementsPaths = [];

            _.forEach(jsonSheet.elements, (rawSubresource : ResourcesBase.IResource) => {
                var pseudoResponse = {
                    data: rawSubresource
                };
                var subresource = importResource(pseudoResponse, metaApi, preliminaryNames, adhCache);
                adhCache.putCached(rawSubresource.path, "", subresource);
                elementsPaths.push(rawSubresource.path);
            });

            if (originalElements === "content") {
                // do nothing
            } else if (originalElements === "paths") {
                jsonSheet.elements = elementsPaths;
            } else {
                jsonSheet.elements = [];
            }
        }

        _.forOwn(jsonSheet, (value, fieldName : string) => {
            // Some fields are not listed in the meta API
            // See https://github.com/liqd/adhocracy3/issues/261
            if (metaApi.fieldExists(sheetName, fieldName)) {
                var field = metaApi.field(sheetName, fieldName);
                jsonSheet[fieldName] = importField(value, field);
            }
        });
    });

    return obj;
};


/**
 * transform batch request response into resource array
 *
 * NOTE: The single batched http requests listed in the response array
 * of the batch request confusingly call the response body 'body',
 * while $http calls it 'data'.  `logBackendBatchError` and
 * `importBatchResources` are (the only two) places where this requires
 * writing a few lines of awkward code.  Fixing it would require
 * changes to /docs/source/rest_api.rst, backend, and these two
 * functions simultaneously and has not been deemed worthwhile so
 * far.
 */
export var importBatchResources = (
    requests : any[],
    responses,
    metaApi : AdhMetaApi.Service,
    preliminaryNames : AdhPreliminaryNames.Service,
    adhCache : AdhCache.Service
) : any[] => {

    return responses.map((response, index) => {
        if (requests[index].method === "DELETE") {
            return { path: requests[index].path };
        }
        response.data = response.body;
        delete response.body;
        return importResource(response, metaApi, preliminaryNames, adhCache);
    });
};


/**
 * prepare object for post or put.  remove all fields that are none of
 * editable, creatable, create_mandatory.  remove all sheets that have
 * no fields after this.
 *
 * FIXME: there is a difference between put and post.  namely, fields
 * that may be created but not edited should be treated differently.
 * also, fields with create_mandatory should not be missing from the
 * posted object.
 */
export var exportResource = <R extends ResourcesBase.IResource>(
    adhMetaApi : AdhMetaApi.Service,
    obj : R,
    keepMetadata : boolean = false
) : R => {
    "use strict";

    sanityCheck(obj, adhMetaApi);
    var newobj : R = _.cloneDeep(obj);

    // remove some fields from newobj.data[*] and empty sheets from
    // newobj.data.
    for (var sheetName in newobj.data) {
        if (newobj.data.hasOwnProperty(sheetName) && adhMetaApi.sheetExists(sheetName)) {
            var sheet : AdhMetaApi.ISheet = newobj.data[sheetName];
            var keepSheet : boolean = false;

            for (var fieldName in sheet) {
                if (sheet.hasOwnProperty(fieldName) && adhMetaApi.fieldExists(sheetName, fieldName)) {
                    var fieldMeta : AdhMetaApi.ISheetField = adhMetaApi.field(sheetName, fieldName);

                    if (fieldMeta.editable || fieldMeta.creatable || fieldMeta.create_mandatory) {
                        keepSheet = true;
                    } else {
                        delete sheet[fieldName];
                    }
                    // workaround, as normal users can not set `hidden` field
                    // FIXME: use more appropriate place, e.g. expose in meta api
                    if (!keepMetadata && sheetName === SIMetadata.nick && fieldName === "hidden") {
                        delete sheet[fieldName];
                    }
                }
            }

            if (!keepSheet) {
                delete newobj.data[sheetName];
            }
        }
    }

    delete newobj.path;
    return newobj;
};
