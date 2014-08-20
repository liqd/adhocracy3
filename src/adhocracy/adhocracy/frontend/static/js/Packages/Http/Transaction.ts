import AdhResources = require("../../Resources");
import MetaApi = require("../MetaApi/MetaApi");

import AdhError = require("./Error");
import AdhMarshall = require("./Marshall");


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
    private nextID : number;

    constructor(private $http : ng.IHttpService, private adhMetaApi : MetaApi.MetaApiQuery) {
        this.requests = [];
        this.committed = false;
        this.nextID = 0;
    }

    private checkNotCommitted() : void {
        if (this.committed) {
            throw("Tried to use an already committed transaction");
        }
    }

    private generatePath() : string {
        return "path" + this.nextID++;
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
            body: AdhMarshall.exportContent(this.adhMetaApi, obj)
        });
        return {
            index: this.requests.length - 1,
            path: path
        };
    }

    public post(path : string, obj : AdhResources.Content<any>) : ITransactionResult {
        this.checkNotCommitted();
        var preliminaryPath = this.generatePath();
        this.requests.push({
            method: "POST",
            path: path,
            body: AdhMarshall.exportContent(this.adhMetaApi, obj),
            result_path: preliminaryPath
        });
        return {
            index: this.requests.length - 1,
            path: "@" + preliminaryPath,
            first_version_path: "@@" + preliminaryPath
        };
    }

    public commit() : ng.IPromise<AdhResources.Content<any>[]> {
        this.checkNotCommitted();
        this.committed = true;
        return this.$http.post("/batch", this.requests).then(
            (response) => {
                response.data = (<any>(response.data)).map(AdhMarshall.importContent);
                // FIXME: description files don't appear to support
                // array-typed response bodies.  this might be a good
                // thing (web security and all).  change rest batch
                // spec to wrap array in trivial object?

                return response;
            },
            AdhError.logBackendError);
    }
}
