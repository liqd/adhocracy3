/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require("../Types");
import Util = require("../Util");

export var importContent : <Content extends Types.Content<any>>(resp: {data: Content}) => Content;
export var exportContent : <Content extends Types.Content<any>>(obj : Content) => Content;
export var logBackendError : (response : ng.IHttpPromiseCallbackArg<IBackendError>) => void;


/**
 * send and receive objects with adhocracy data model awareness
 *
 * this service only handles resources of the form {content_type: ...,
 * path: ..., data: ...}.  if you want to send other objects over the
 * wire (such as during user login), use $http.
 */

// FIXME: This service should be able to handle any type, not just subtypes of
// ``Types.Content``.  Methods like ``postNewVersion`` may need additional
// constraints (e.g. by moving them to subclasses).
export class Service<Content extends Types.Content<any>> {
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
        var _obj = Util.deepcp(obj);
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

    // FIXME: Get this list from the server (meta-api)!
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
    errors: IBackendErrorItem[];
}

export interface IBackendErrorItem {
    name : string;
    location : string;
    description : string;
}

logBackendError = (response : ng.IHttpPromiseCallbackArg<IBackendError>) : void => {
    "use strict";

    console.log("http response with error status: " + response.status);

    for (var e in response.data.errors) {
        if (response.data.errors.hasOwnProperty(e)) {
            console.log("error #" + e);
            console.log("where: " + response.data.errors[e].name + ", " + response.data.errors[e].location);
            console.log("what:  " + response.data.errors[e].description);
        }
    }

    console.log(response.config);
    console.log(response.data);

    throw response.data.errors;
};
