import PreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhResources = require("../../Resources");
import MetaApi = require("../MetaApi/MetaApi");
import AdhConfig = require("../Config/Config");

import AdhError = require("./Error");
import AdhHttp = require("./Http");
import AdhConvert = require("./Convert");


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
        private adhMetaApi : MetaApi.MetaApiQuery,
        private adhPreliminaryNames : PreliminaryNames,
        private adhConfig : AdhConfig.Type
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

    public put(path : string, obj : AdhResources.Content<any>) : ITransactionResult {
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

    public post(path : string, obj : AdhResources.Content<any>) : ITransactionResult {
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

    public commit() : ng.IPromise<AdhResources.Content<any>[]> {
        this.checkNotCommitted();
        this.committed = true;
        var conv = (request) => {
            if (request.hasOwnProperty("body")) {
                request.body = AdhConvert.exportContent(this.adhMetaApi, request.body);
            }
            return request;
        };

        return this.adhHttp.postRaw("/batch", this.requests.map(conv)).then(
            (response) => AdhConvert.importBatchContent(<any>response, this.adhMetaApi, this.adhPreliminaryNames),
            AdhError.logBackendBatchError);
    }
}
