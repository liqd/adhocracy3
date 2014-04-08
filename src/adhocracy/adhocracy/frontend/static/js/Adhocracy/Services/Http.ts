/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");


// send and receive objects with adhocracy data model awareness

export var jsonPrefix : string = "/adhocracy";

export interface IService<Data> {
    get : (path : string) => ng.IPromise<Types.Content<Data>>;
    put : (path : string, obj : Types.Content<Data>) => ng.IPromise<Types.Content<Data>>;
    postNewVersion : (oldVersionPath : string, obj : Types.Content<Data>) => ng.IPromise<Types.Content<Data>>;
    postToPool : (poolPath : string, obj : Types.Content<Data>) => ng.IPromise<Types.Content<Data>>;
}

export function factory<Data>($http : ng.IHttpService) : IService<Data> {
    var adhHttp : IService<Data> = {
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

    function get(path : string) : ng.IPromise<Types.Content<Data>> {
        return $http.get(path).then(assertResponse("adhHttp.get", path));
    }

    function put(path : string, obj : Types.Content<Data>) : ng.IPromise<Types.Content<Data>> {
        return $http.put(path, obj).then(assertResponse("adhHttp.put", path));
    }

    function postNewVersion(oldVersionPath : string, obj : Types.Content<Data>) : ng.IPromise<Types.Content<Data>> {
        var dagPath = Util.parentPath(oldVersionPath);
        var config = {
            headers: { follows: oldVersionPath },
            params: {},
        };
        return $http.post(dagPath, exportContent(obj), config).then(assertResponse("adhHttp.postNewVersion", dagPath));
    }

    function postToPool(poolPath : string, obj : Types.Content<Data>) : ng.IPromise<Types.Content<Data>> {
        return $http.post(poolPath, exportContent(obj)).then(assertResponse("adhHttp.postToPool", poolPath));
    }

    return adhHttp;
}


// transform objects on the way in and out

export function importContent<Data>(obj : Types.Content<Data>) : Types.Content<Data> {
    return obj;
}

export function exportContent<Data>(obj : Types.Content<Data>) : Types.Content<Data> {
    var newobj : Types.Content<Data> = obj

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
