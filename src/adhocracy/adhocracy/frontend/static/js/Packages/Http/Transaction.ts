import AdhResources = require("../../Resources");


export interface ITransactionResult {
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
    private paths : string[];
    private committed : boolean;
    private nextID : number;

    constructor(private $http : ng.IHttpService) {
        this.requests = [];
        this.paths = [];
        this.committed = false;
        this.nextID = 0;
    }

    private checkCommitted() : void {
        if (this.committed) {
            throw("Tried to use an already committed transaction");
        }
    }

    private generatePath() : string {
        return "@path" + this.nextID++;
    }

    public get(path : string) : ITransactionResult {
        this.checkCommitted();
        this.requests.push({
            method: "GET",
            path: path
        });
        this.paths.push(path);
        return {
            path: path
        };
    }

    public put(path : string, obj : AdhResources.Content<any>) : ITransactionResult {
        this.checkCommitted();
        this.requests.push({
            method: "PUT",
            path: path,
            body: obj
        });
        this.paths.push(path);
        return {
            path: path
        };
    }

    public post(path : string, obj : AdhResources.Content<any>) : ITransactionResult {
        this.checkCommitted();
        var preliminaryPath = this.generatePath();
        this.requests.push({
            method: "POST",
            path: path,
            body: obj
        });
        this.paths.push(preliminaryPath);
        return {
            path: preliminaryPath,
            first_version_path: "@" + preliminaryPath
        };
    }

    public commit() : ng.IPromise<{[path : string]: AdhResources.Content<any>}> {
        this.checkCommitted();
        this.committed = true;

        return this.$http.post("/batch", this.requests)
            .then((responses : AdhResources.Content<any>[]) => {
                var responseMap = {};

                responses.forEach((response, ix) => {
                    var path = this.paths[ix];
                    responseMap[path] = response;
                });

                return responseMap;
            });
    }
}

