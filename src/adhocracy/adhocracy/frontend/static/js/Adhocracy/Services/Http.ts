/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");


// send and receive objects with adhocracy data model awareness

// FIXME: This service should be able to handle any type, not just subtypes of
// ``Types.Content``.  Methods like ``postNewVersion`` may need additional
// constraints (e.g. by moving them to subclasses).

export interface IService<Content extends Types.Content<any>> {
    get : (path : string) => ng.IPromise<Content>;
    put : (path : string, obj : Content) => ng.IPromise<Content>;
    postNewVersion : (oldVersionPath : string, obj : Content) => ng.IPromise<Content>;
    postToPool : (poolPath : string, obj : Content) => ng.IPromise<Content>;
    metaApiResource : (name : string) => any;
    metaApiSheet : (name : string) => any;
}

export function factory<Content extends Types.Content<any>>($http : ng.IHttpService) : IService<Content> {
    "use strict";

    var adhHttp : IService<Content> = {
        get: get,
        put: put,
        postNewVersion: postNewVersion,
        postToPool: postToPool,
        metaApiResource: metaApiResource,
        metaApiSheet: metaApiSheet
    };

    function get(path : string) : ng.IPromise<Content> {
        return $http.get(path).success(importContent).error(logBackendError);
    }

    function put(path : string, obj : Content) : ng.IPromise<Content> {
        return $http.put(path, obj).success(importContent).error(logBackendError);
    }

    function postNewVersion(oldVersionPath : string, obj : Content) : ng.IPromise<Content> {
        var dagPath = Util.parentPath(oldVersionPath);
        var config = {
            headers: { follows: oldVersionPath },
            params: {}
        };
        return $http
            .post(dagPath, exportContent(obj), config)
            .success(importContent)
            .error(logBackendError);
    }

    function postToPool(poolPath : string, obj : Content) : ng.IPromise<Content> {
        return $http
            .post(poolPath, exportContent(obj))
            .success(importContent)
            .error(logBackendError);
    }

    // query meta-api for resource content types.  return the json
    // object explaining the content type of a resource.  if called
    // without an argument, return a list of all known content types.
    function metaApiResource(name : string) : any {
        throw "not implemented.";
    }

    // query meta-api for property types.  return the json object
    // explaining the type of a property sheet.  if called without an
    // argument, return a list of all known property sheets.
    function metaApiSheet(name : string) : any {
        throw "not implemented.";
    }

    return adhHttp;
}


// transform objects on the way in and out

export function importContent<Content extends Types.Content<any>>(obj : Content) : Content {
    "use strict";
    return obj;
}

export function exportContent<Content extends Types.Content<any>>(obj : Content) : Content {
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

export interface IBackendError {
    status: string;
    errors: string[][];
}

export var logBackendError = (data: IBackendError, status: number, headers, config) => {
    console.log("http response with error status: " + status);

    for (var e in data.errors) {
        console.log("error #" + e);
        console.log("where: " + data.errors[e][0] + ", " + data.errors[e][1]);
        console.log("what:  " + data.errors[e][2]);
    }

    console.log(config);
    console.log(data);

    throw ("adhHttp: exit code " + status + "!");
};
