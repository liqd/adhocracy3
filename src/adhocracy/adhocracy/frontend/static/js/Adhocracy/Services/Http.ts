/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");


// send and receive objects with adhocracy data model awareness

export var jsonPrefix : string = "/adhocracy";

export interface IService {
    get : (path : string) => ng.IPromise<Types.Content>;
    put : (path : string, obj : Types.Content) => ng.IPromise<Types.Content>;
    postNewVersion : (oldVersionPath : string, obj : Types.Content) => ng.IPromise<Types.Content>;
    postToPool : (poolPath : string, obj : Types.Content) => ng.IPromise<Types.Content>;
}

export function factory($http : ng.IHttpService) : IService {
    var adhHttp : IService = {
        get: get,
        put: put,
        postNewVersion: postNewVersion,
        postToPool: postToPool,
    };

    function assertResponse(msg : string, path : string) {
        return (resp) => {
            if (resp.status !== 200) {
                console.log(resp);
                throw (msg + ": http error " + resp.status.toString() + " on path " + path);
            }
            return importContent(resp.data);
        };
    }

    function get(path : string) : ng.IPromise<Types.Content> {
        return $http.get(path).then(assertResponse("adhHttp.get", path));
    }

    function put(path : string, obj : Types.Content) : ng.IPromise<Types.Content> {
        return $http.put(path, obj).then(assertResponse("adhHttp.put", path));
    }

    function postNewVersion(oldVersionPath : string, obj : Types.Content) : ng.IPromise<Types.Content> {
        var dagPath = Util.parentPath(oldVersionPath);
        var config = {
            headers: { follows: oldVersionPath },
            params: {},
        };
        return $http.post(dagPath, exportContent(obj), config).then(assertResponse("adhHttp.postNewVersion", dagPath));
    }

    function postToPool(poolPath : string, obj : Types.Content) : ng.IPromise<Types.Content> {
        return $http.post(poolPath, exportContent(obj)).then(assertResponse("adhHttp.postToPool", poolPath));
    }

    return adhHttp;
}


// transform objects on the way in and out

export var importContent : (obj : Types.Content) => Types.Content
    = translateContent(shortenType);

export var exportContent : (obj : Types.Content) => Types.Content
    = (obj) =>
{
    var newobj = translateContent(unshortenType)(obj);

    // FIXME: Get this list from the server!
    var readOnlyProperties = [
        "adhocracy.propertysheets.interfaces.IVersions"
    ];

    for (var ro in readOnlyProperties) {
        delete newobj.data[readOnlyProperties[ro]];
    }

    delete newobj.path;
    return newobj;
};

var contentTypeNameSpaces = {
    "adhocracy.resources": "R"
};

var propertyTypeNameSpaces = {
    "adhocracy.sheets": "S"
};

function shortenType(nameSpaces) {
    return s => {
        var t = s;
        for (var k in nameSpaces) {
            t = t.replace(new RegExp("^" + k + "(\\.[^\\.]+)$"), nameSpaces[k] + "$1");
        }
        return t;
    };
}

function unshortenType(nameSpaces) {
    return s => {
        var t = s;
        for (var k in nameSpaces) {
            t = t.replace(new RegExp("^" + nameSpaces[k] + "\\.(.+)$"), k + ".$1");
        }
        return t;
    };
}

function translateContent(translateType) {
    return inobj => {
        var outobj = {
            content_type: translateType(contentTypeNameSpaces)(inobj.content_type),
            path: inobj.path,
            data: {},
        };

        for (var k in inobj.data) {
            var k_local = translateType(propertyTypeNameSpaces)(k);
            outobj.data[k_local] =
                changeContentTypeRecursively(inobj.data[k],
                                             translateType(contentTypeNameSpaces));
        }

        return outobj;
    };
}

function changeContentTypeRecursively(obj, f) {
    var t = Object.prototype.toString.call(obj);

    switch (t) {
    case "[object Object]":
        var newobj = {};
        for (var k in obj) {
            if (k === "content_type") {
                newobj[k] = f(obj[k]);
            } else {
                newobj[k] = changeContentTypeRecursively(obj[k], f);
            }
        }
        return newobj;

    case "[object Array]":
        return obj.map((el) => { return changeContentTypeRecursively(el, f); });

    default:
        return obj;
    }
}
