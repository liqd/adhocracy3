/* tslint:disable:variable-name */
/// <reference path="../../../lib/DefinitelyTyped/lodash/lodash.d.ts"/>

import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");

import ResourcesBase = require("../../ResourcesBase");

import AdhCache = require("./Cache");
import AdhConvert = require("./Convert");
import AdhError = require("./Error");
import AdhHttp = require("./Http");
import AdhMetaApi = require("./MetaApi");

export interface ITransactionResult {
    index : number;
    path : string;
    first_version_path? : string;
}


/**
 * Http Transaction.
 *
 * This should be used via adhHttp.withTransaction.
 */
export class Transaction {
    // FIXME: importContent, exportContent and logBackendError need yet to be
    // incorporated.

    private requests : any[];
    private committed : boolean;

    constructor(
        private adhHttp : AdhHttp.Service<any>,
        private adhCache : AdhCache.Service,
        private adhMetaApi : AdhMetaApi.MetaApiQuery,
        private adhPreliminaryNames : AdhPreliminaryNames.Service,
        private adhConfig : AdhConfig.IService
    ) {
        this.requests = [];
        this.committed = false;
    }

    private checkNotCommitted() : void {
        if (this.committed) {
            throw("Tried to use an already committed transaction");
        }
    }

    public get(path : string) : ITransactionResult {
        this.checkNotCommitted();
        this.requests.push({
            method: "GET",
            path: path
        });
        return {
            index: this.requests.length - 1,
            path: path
        };
    }

    public put(path : string, obj : ResourcesBase.Resource) : ITransactionResult {
        this.checkNotCommitted();
        this.requests.push({
            method: "PUT",
            path: path,
            body: AdhConvert.exportContent(this.adhMetaApi, obj)
        });
        return {
            index: this.requests.length - 1,
            path: path
        };
    }

    public post(path : string, obj : ResourcesBase.Resource) : ITransactionResult {
        this.checkNotCommitted();
        var preliminaryPath;
        if (typeof obj.path === "string") {
            preliminaryPath = obj.path;
        } else {
            preliminaryPath = this.adhPreliminaryNames.nextPreliminary();
        }
        var preliminaryFirstVersionPath;
        if (typeof obj.first_version_path === "string") {
            preliminaryFirstVersionPath = obj.first_version_path;
        } else {
            preliminaryFirstVersionPath = this.adhPreliminaryNames.nextPreliminary();
        }
        this.requests.push({
            method: "POST",
            path: path,
            body: AdhConvert.exportContent(this.adhMetaApi, obj),
            result_path: preliminaryPath,
            result_first_version_path: preliminaryFirstVersionPath
        });
        return {
            index: this.requests.length - 1,
            path: preliminaryPath,
            first_version_path: preliminaryFirstVersionPath
        };
    }

    public commit() : ng.IPromise<ResourcesBase.Resource[]> {
        var _self = this;

        this.checkNotCommitted();
        this.committed = true;
        var conv = (request) => {
            if (request.hasOwnProperty("body")) {
                request.body = AdhConvert.exportContent(this.adhMetaApi, request.body);
            }
            return request;
        };

        return this.adhHttp.postRaw("/batch", this.requests.map(conv)).then(
            (response) => {
                var imported = AdhConvert.importBatchContent(response.data.responses, this.adhMetaApi, this.adhPreliminaryNames);
                _self.adhCache.invalidateUpdated(response.data.updated_resources, _.pluck(imported, "path"));
                return imported;
            },
            AdhError.logBackendBatchError);
    }
}
