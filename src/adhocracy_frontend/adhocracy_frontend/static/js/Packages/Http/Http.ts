/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/lodash/lodash.d.ts"/>

import Resources = require("../../Resources");
import ResourcesBase = require("../../ResourcesBase");
import Util = require("../Util/Util");
import MetaApi = require("../MetaApi/MetaApi");
import PreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhTransaction = require("./Transaction");
import AdhError = require("./Error");
import AdhConvert = require("./Convert");

// re-exports
export interface ITransactionResult extends AdhTransaction.ITransactionResult {};
export interface IBackendError extends AdhError.IBackendError {};
export interface IBackendErrorItem extends AdhError.IBackendErrorItem {};
export var logBackendError : (response : ng.IHttpPromiseCallbackArg<IBackendError>) => void = AdhError.logBackendError;


/**
 * send and receive objects with adhocracy data model awareness
 *
 * this service only handles resources of the form {content_type: ...,
 * path: ..., data: ...}.  if you want to send other objects over the
 * wire (such as during user login), use $http.
 */

// FIXME: This service should be able to handle any type, not just subtypes of
// ``Resources.Content``.  Methods like ``postNewVersion`` may need additional
// constraints (e.g. by moving them to subclasses).
export class Service<Content extends Resources.Content<any>> {
    constructor(
        private $http : ng.IHttpService,
        private $q : ng.IQService,
        private adhMetaApi : MetaApi.MetaApiQuery,
        private adhPreliminaryNames : PreliminaryNames
    ) {}

    public get(path : string) : ng.IPromise<Content> {
        if (this.adhPreliminaryNames.isPreliminary(path)) {
            throw "attempt to http-get preliminary path: " + path;
        }
        return this.$http
            .get(path)
            .then(
                (response) => AdhConvert.importContent(<any>response, this.adhMetaApi, this.adhPreliminaryNames),
                AdhError.logBackendError);
    }

    public put(path : string, obj : Content) : ng.IPromise<Content> {
        if (this.adhPreliminaryNames.isPreliminary(path)) {
            throw "attempt to http-put preliminary path: " + path;
        }
        return this.$http
            .put(path, AdhConvert.exportContent(this.adhMetaApi, obj))
            .then(
                (response) => AdhConvert.importContent(<any>response, this.adhMetaApi, this.adhPreliminaryNames),
                AdhError.logBackendError);
    }

    public post(path : string, obj : Content) : ng.IPromise<Content> {
        if (this.adhPreliminaryNames.isPreliminary(path)) {
            throw "attempt to http-post preliminary path: " + path;
        }
        return this.$http
            .post(path, AdhConvert.exportContent(this.adhMetaApi, obj))
            .then(
                (response) => AdhConvert.importContent(<any>response, this.adhMetaApi, this.adhPreliminaryNames),
                AdhError.logBackendError);
    }

    public getNewestVersionPath(path : string) : ng.IPromise<string> {
        // FIXME: This works under the assumption that there is always only
        // *one* latest version. This is not neccesserily true for multi-user
        // scenarios.
        return this.get(path + "/LAST")
            .then((tag) => tag.data["adhocracy.sheets.tags.ITag"].elements[0]);
    }

    /**
     * Post a reference graph of resources.
     *
     * Take an array of resources.  The array has set semantics and
     * may contain, e.g., a proposal to be posted and all of its
     * sub-resources.  All elements of the extended set are posted in
     * an order that avoids dangling references (referenced object
     * always occur before referencing object).
     *
     * Resources may contain preliminary paths created by the
     * PreliminaryNames service in places where
     * `adhocracy.schema.AbsolutePath` is expected.  These paths must
     * reference other items of the input array, and are converted to
     * real paths by the batch API server endpoint.
     *
     * This function does not handle unchanged resources any different
     * from changed ones, i.e. unchanged resources in the input array
     * will end up as duplicate versions on the server.  Therefore,
     * the caller should only pass resources that have changed. We
     * might want to handle this case in the future within the
     * deepPost function as well.
     *
     * *return value:* `deepPost` promises an array of the posted
     * objects (in original order).
     *
     * FIXME: It is not yet defined how errors (e.g. validation
     * errors) are passed back to the caller.
     */
    public deepPost(
        resources : ResourcesBase.Resource[]
    ) : ng.IPromise<ResourcesBase.Resource[]> {

        var sortedResources : ResourcesBase.Resource[] = ResourcesBase.sortResourcesTopologically(resources, this.adhPreliminaryNames);

        // post stuff
        return this.withTransaction((transaction) : ng.IPromise<ResourcesBase.Resource[]> => {
            _.forEach(sortedResources, (resource) => {
                transaction.post(resource.parent, resource);
            });

            return transaction.commit();
        });
    }

    public postNewVersion(oldVersionPath : string, obj : Content, rootVersions? : string[]) : ng.IPromise<Content> {
        var dagPath = Util.parentPath(oldVersionPath);
        var _obj = Util.deepcp(obj);
        _obj.data["adhocracy.sheets.versions.IVersionable"] = {
            follows: [oldVersionPath]
        };
        if (typeof rootVersions !== "undefined") {
            _obj.root_versions = rootVersions;
        }
        return this.post(dagPath, _obj);
    }

    public postToPool(poolPath : string, obj : Content) : ng.IPromise<Content> {
        return this.post(poolPath, obj);
    }

    /**
     * Resolve a path or content to content
     *
     * If you do not know if a reference is already resolved to the corresponding content
     * you can use this function to be sure.
     */
    public resolve(path : string) : ng.IPromise<Content>;
    public resolve(content : Content) : ng.IPromise<Content>;
    public resolve(pathOrContent) {
        if (typeof pathOrContent === "string") {
            return this.get(pathOrContent);
        } else {
            return this.$q.when(pathOrContent);
        }
    }

    /**
     * Call `withTransaction` with a callback that accepts a
     * transaction.  All calls to `transaction` within `trans` are
     * collected into a batch request.
     *
     * Note that the interface of the transaction differs
     * significantly from that of adhHttp. It can therefore not be
     * used as a drop-in.
     *
     * A transaction returns an object (not a promise!) containing
     * some information you might need in other requests within the
     * same transaction. Note that some of this information may be
     * preliminary and should therefore not be used outside of the
     * transaction.
     *
     * After all requests have been made you need to call
     * `transaction.commit()`.  After that, no further interaction
     * with `transaction` is possible and will throw exceptions.
     * `commit` promises a list of responses. You can easily
     * identify the index of each request via the `index` property
     * in the preliminary data.
     *
     * `withTransaction` simply returns the result of the callback.
     *
     * Arguably, `withTransaction` should implicitly call `commit`
     * after the callback returns, but this would only work in the
     * synchronous case.  On the other hand, the done()-idiom is not
     * any prettier than forcing the caller of `withTransaction` to
     * call `commit` manually.  On the plus side, this makes it easy
     * to do post-processing (such as discarding parts of the batch
     * request that have become uninteresting with the successful
     * batch post).
     *
     * Example:
     *
     *     var postVersion = (path : string, ...) => {
     *         return adhHttp.withTransaction((transaction) => {
     *             var resource = ...
     *             var resourcePost = transaction.post(path, resource);
     *
     *             var version = {
     *                 data: {
     *                     "adhocracy.sheets.versions.IVersionable": {
     *                         follows: resourcePost.first_version_path
     *                     },
     *                     ...
     *                 }
     *             };
     *             var versionPost = transaction.post(resourcePost.path, version);
     *             var versionGet = transaction.get(versionPost.path);
     *
     *             return transaction.commit()
     *                 .then((responses) => {
     *                     return responses[versionGet.index];
     *                 });
     *         });
     *     };
     */
    public withTransaction<Result>(callback : (httpTrans : AdhTransaction.Transaction) => ng.IPromise<Result>) : ng.IPromise<Result> {
        return callback(new AdhTransaction.Transaction(this.$http, this.adhMetaApi, this.adhPreliminaryNames));
    }
}