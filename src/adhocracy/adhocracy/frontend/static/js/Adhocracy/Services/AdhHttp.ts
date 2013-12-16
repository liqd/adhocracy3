/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require('Adhocracy/Types');
import Util = require('Adhocracy/Util');


// send and receive objects with adhocracy data model awareness

export interface AdhHttpService {
    get: (path: string) => ng.IPromise<Types.Content>;
    drill: (data: any, xpath: any, target: any, ordered: boolean) => void;
    postNewVersion: (oldVersionPath: string, obj: any, callback: any) => ng.IPromise<Types.Content>;
}

export function adhHttpFactory($http : ng.IHttpService) : AdhHttpService {
    var adhHttp : AdhHttpService = {
        get: (path: string) => {
            return $http.get(path).then((response) => {
                if (response.status != 200) {
                    console.log(response);
                    throw ('adhHttp.get: http error ' + response.status.toString() + ' on path ' + path);
                }
                return importContent(response.data);
            });
        },

        drill: (data: any, xpath: /* string[] or string[][] */ any, target: any, ordered: boolean) => {
            function resolveReference() {
                if ('path' in data) {
                    adhHttp.get(data['path']).then((resource) => {
                        adhHttp.drill(resource, xpath, target, ordered);
                    });
                } else {
                    console.log(data);
                    throw 'adhHttp.drill: not a resource and not a reference.';
                }
            }

            if ('content_type' in data) {
                if ('data' in data) {
                    adhHttp.drill(data['data'], xpath, target, ordered);
                    return;
                } else {
                    resolveReference();
                    return;
                }
            } else {
                if (xpath.length == 0) {
                    if (target.xpath.length != 1) {
                        throw 'not implemented.';
                    }
                    target.ref[target.xpath[0]] = data;
                    return;
                }
                var step = xpath.shift();
                if (typeof step == 'string' || typeof step == 'number') {
                    adhHttp.drill(data[step], xpath, target, ordered);
                    return;
                }
                if (step instanceof Array) {
                    if (step.length != 1 || !(typeof(step[0]) == 'string' || typeof(step[0]) == 'number')) {
                        // FIXME: what about "[[step]]"?
                        // FIXME: if xpath contains more than one [step], i don't know what'll happen...
                        console.log(step);
                        throw 'internal';
                    }
                    step = step[0];

                    if (!(data[step] instanceof Array)) {
                        console.log(data);
                        console.log(step);
                        throw 'internal';
                    }
                    var elements = data[step];

                    if (!(target.ref instanceof Array)) {
                        console.log(target);
                        throw 'not implemented.';
                    }

                    if (!ordered) {
                        console.log(ordered);
                        throw 'not implemented.';
                    }

                    // loop over step, and call drill recursively on
                    // each element, together with the corresponding
                    // element of target.
                    for (var ix in elements) {
                        var subtarget = {
                            ref: target.ref,
                            xpath: [ix],
                        };
                        adhHttp.drill(elements[ix], Util.deepcp(xpath), subtarget, ordered);
                    }
                    return;
                }
            }
        },

        postNewVersion: (oldVersionPath: string, obj: any, callback: any) => {
            var dagPath = Util.parentPath(oldVersionPath);
            var config = {
                headers: { follows: oldVersionPath },
                params: {},
            };
            return $http.post(dagPath, exportContent(obj), config).then(callback);
        },
    };

    return adhHttp;
}


// transform objects on the way in and out

var importContent : (obj: Types.Content) => Types.Content
    = translateContent(shortenType);

var exportContent : (obj: Types.Content) => Types.Content
    = (obj) => {
    var newobj = translateContent(unshortenType)(obj);

    // FIXME: Get this list from the server!
    var readOnlyProperties = [
        'adhocracy.propertysheets.interfaces.IVersions'
    ];

    for (var ro in readOnlyProperties)
        delete newobj.data[readOnlyProperties[ro]];

    delete newobj.path;
    return newobj;
}

var contentTypeNameSpaces = {
    'adhocracy.contents.interfaces': 'C'
}

var propertyTypeNameSpaces = {
    'adhocracy.propertysheets.interfaces': 'P'
}

function shortenType(nameSpaces) {
    return s => {
        var t = s;
        for (var k in nameSpaces) {
            t = t.replace(new RegExp('^' + k + '(\\.[^\\.]+)$'), nameSpaces[k] + '$1');
        }
        return t;
    }
}

function unshortenType(nameSpaces) {
    return s => {
        var t = s;
        for (var k in nameSpaces) {
            t = t.replace(new RegExp('^' + nameSpaces[k] + '(\\.[^\\.]+)$'), k + '$1');
        }
        return t;
    }
}

function translateContent(translateType) {
    return inobj => {
        var outobj = {
            content_type: translateType(contentTypeNameSpaces)(inobj.content_type),
            path: inobj.path,
            data: {},
        }

        for (var k in inobj.data) {
            var k_local = translateType(propertyTypeNameSpaces)(k);
            outobj.data[k_local] =
                changeContentTypeRecursively(inobj.data[k],
                                             translateType(contentTypeNameSpaces));
        }

        return outobj;
    }
}

function changeContentTypeRecursively(obj, f) {
    var t = Object.prototype.toString.call(obj);

    switch(t) {
    case '[object Object]':
        var newobj = {};
        for (var k in obj) {
            if (k == 'content_type') {
                newobj[k] = f(obj[k]);
            } else {
                newobj[k] = changeContentTypeRecursively(obj[k], f);
            }
        }
        return newobj;

    case '[object Array]':
        return obj.map((el) => { return changeContentTypeRecursively(el, f); });

    default:
        return obj;
    }
}
