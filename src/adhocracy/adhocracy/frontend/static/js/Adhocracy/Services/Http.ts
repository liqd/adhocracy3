/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require("../Types");
import Util = require("../Util");

export var factory;
export var importContent;
export var exportContent;
export var logBackendError;


/**
 * send and receive objects with adhocracy data model awareness
 */

// FIXME: This service should be able to handle any type, not just subtypes of
// ``Types.Content``.  Methods like ``postNewVersion`` may need additional
// constraints (e.g. by moving them to subclasses).
export interface IBaseService<Content extends Types.Content<any>> {
    get : (path : string) => ng.IPromise<Content>;
    put : (path : string, obj : Content) => ng.IPromise<Content>;
    post : (path : string, obj : Content) => ng.IPromise<Content>;
    postNewVersion : (oldVersionPath : string, obj : Content) => ng.IPromise<Content>;
    postToPool : (poolPath : string, obj : Content) => ng.IPromise<Content>;
}

export interface ITransaction<Content extends Types.Content<any>> extends IBaseService<Content> {}

export class Service<Content extends Types.Content<any>> implements IBaseService<Content> {
    constructor(private $http : ng.IHttpService, private $q) {}

    get(path : string) : ng.IPromise<Content> {
        return this.$http.get(path).then(importContent, logBackendError);
    }

    put(path : string, obj : Content) : ng.IPromise<Content> {
        return this.$http.put(path, exportContent(obj)).then(importContent, logBackendError);
    }

    post(path : string, obj : Content) : ng.IPromise<Content> {
        return this.$http.post(path, exportContent(obj)).then(importContent, logBackendError);
    }

    postNewVersion(oldVersionPath : string, obj : Content, rootVersions? : string[]) : ng.IPromise<Content> {
        var dagPath = Util.parentPath(oldVersionPath);
        var _obj = exportContent(obj);
        _obj.data["adhocracy.sheets.versions.IVersionable"] = {
            follows: [oldVersionPath]
        };
        if (typeof rootVersions !== "undefined") {
            _obj.root_versions = rootVersions;
        }
        return this.post(dagPath, _obj);
    }

    postToPool(poolPath : string, obj : Content) : ng.IPromise<Content> {
        return this.post(poolPath, obj);
    }

    /**
     * Resolve a path or content to content
     *
     * If you do not know if a reference is already resolved to the corresponding content
     * you can use this function to be sure.
     */
    resolve(path : string) : ng.IPromise<Content>;
    resolve(content : Content) : ng.IPromise<Content>;
    resolve(pathOrContent) {
        if (typeof pathOrContent === "string") {
            return this.get(pathOrContent);
        } else {
            return this.$q.when(pathOrContent);
        }
    }

    /**
     * query meta-api for resource content types.  return the json
     * object explaining the content type of a resource.  if called
     * without an argument, return a list of all known content types.
     */
    metaApiResource(name : string) : any {
        throw "not implemented.";
    }

    /**
     * query meta-api for property types.  return the json object
     * explaining the type of a property sheet.  if called without an
     * argument, return a list of all known property sheets.
     */
    metaApiSheet(name : string) : any {
        throw "not implemented.";
    }

    /**
     * Call withTransaction with a callback `trans` that accepts a
     * transaction (an adhHttp-like service) and a done callback.
     * All calls to `transaction` within `trans` are collected into
     * a batch request, and the batch-request is sent to the backend
     * when `done` is called.
     *
     * Transactions can not be used as drop-ins for the adhHttp
     * service because the promises will only be resolved after `done`
     * has been called. This might result in deadlocks in code that
     * was orginially written for adhHttp.
     *
     * The current implementation is a mock and passes the plain
     * (transaction-less) http service.
     *
     * In an ideal world, the promised values of the calls to
     * `transaction` should be completely indifferent to the question
     * whether they have been produced in a transaction or not -- they
     * should just return the values from the server once those have
     * actually been produced.
     *
     * This is in tension with the requirement that requests inside
     * one transaction depend on each other, so we need to change the
     * api somehow.  Perhaps we can pass local preliminary paths
     * together with post path and posted object to a variant of the
     * post method.
     */
    public withTransaction(trans : (httpTrans : IService<Content>, done : () => void) => void) : void {
        trans(this, () => null);
    }
}


/**
 * transform objects on the way in and out
 */
importContent = <Content extends Types.Content<any>>(resp: {data: Content}) : Content => {
    "use strict";

    var obj = resp.data;

    if (typeof obj === "object") {
        return obj;
    } else {
        throw ("unexpected type: " + (typeof obj).toString() + " " + obj.toString());
    }

    // FIXME: it would be nice if this function could throw an
    // exception at run-time if the type of obj does not match
    // Content.  however, not only is Content a compile-time entity,
    // but it may very well be based on an interface that has no
    // run-time entity anywhere.  two options:
    //
    // (1) http://stackoverflow.com/questions/24056019/is-there-a-way-to-check-instanceof-on-types-dynamically
    //
    // (2) typescript language feature request! :)
    //
    //
    // the following function would be useful if the problem of
    // turning abstract types into runtime objects could be solved.
    // (for the time being, it has been removed from the Util module
    // where it belongs.)
    //
    //
    //   // in a way another function in the deep* family: check that _super
    //   // has only attributes also available in _sub.  also check recursively
    //   // (if _super has an object attribute, its counterpart in _sub must
    //   // have the same attributes, and so on).
    //
    //   // FIXME: untested!
    //   export function subtypeof(_sub, _super) {
    //       if (typeof _sub !== typeof _super) {
    //           return false;
    //       }
    //
    //       if (typeof(_sub) === "object") {
    //           if (_sub === null || _super === null) {
    //               return true;
    //           }
    //
    //           for (var x in _super) {
    //               if (!(x in _sub)) { return false; }
    //               if (!subtypeof(_sub[x], _super[x])) { return false; }
    //           }
    //       }
    //
    //       return true;
    //   }
};

exportContent = <Content extends Types.Content<any>>(obj : Content) : Content => {
    "use strict";

    // FIXME: newobj should be a copy, not a reference
    var newobj : Content = obj;

    // FIXME: Get this list from the server!
    var readOnlyProperties = [
        "adhocracy.propertysheets.interfaces.IVersions"
    ];

    for (var ro in readOnlyProperties) {
        if (readOnlyProperties.hasOwnProperty(ro)) {
            delete newobj.data[readOnlyProperties[ro]];
        }
    }

    delete newobj.path;
    return newobj;
};


// error handling

// Error responses in the Adhocracy REST API contain json objects in
// the body that have the following form:
export interface IBackendError {
    status: string;
    errors: string[][];
}

logBackendError = (data: IBackendError, status: number, headers, config) : void => {
    "use strict";

    console.log("http response with error status: " + status);

    for (var e in data.errors) {
        if (data.errors.hasOwnProperty(e)) {
            console.log("error #" + e);
            console.log("where: " + data.errors[e][0] + ", " + data.errors[e][1]);
            console.log("what:  " + data.errors[e][2]);
        }
    }

    console.log(config);
    console.log(data);

    throw ("adhHttp: exit code " + status + "!");
};
