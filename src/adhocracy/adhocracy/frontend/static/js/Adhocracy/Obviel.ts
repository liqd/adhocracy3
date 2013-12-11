/// <reference path="../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>

var obviel = require('obviel');

import Types = require('Adhocracy/Types');

export function register_transformer() {

    // register global transformer to add obviel ifaces attribute to
    // the received json objects.  also runs s/\./#/g on property
    // sheet names.
    obviel.transformer(jsonAfterReceive);
}


// in-transformer.  call this on every object first thing it hits us
// from the server.
export function jsonAfterReceive(inobj : Types.Content, path) : Types.Content {
    // strip noise from content type and property sheet types
    var outobj : Types.Content = {
        content_type: importContentType(inobj.content_type),
        path: inobj.path,
        data: {},
    }

    for (i in inobj.data) {
        var i_local = importPropertyType(i);
        outobj.data[i_local] = changeContentTypeRecursively(inobj.data[i], importContentType);
    }

    // add content type to ifaces
    outobj.ifaces = [outobj.content_type];

    // add all property sheet types as ifaces
    for (var i in outobj.data) {
        outobj.ifaces.push(i);
    };

    return outobj;
}


// out-transformer.  call this on every object before sending it back
// to the server.
export function jsonBeforeSend(inobj : Types.Content) : Types.Content {
    var i;
    var outobj : Types.Content = {
        content_type: exportContentType(inobj.content_type),
        data: {},
    };

    // FIXME: Get this list from the server!  (How?)
    var readOnlyProperties = ['adhocracy#propertysheets#interfaces#IVersions'];

    for (i in inobj['data']) {
        if (readOnlyProperties.indexOf(i) < 0) {
            var i_remote = exportPropertyType(i);
            outobj.data[i_remote] = changeContentTypeRecursively(inobj.data[i], exportContentType);
        }
    }

    return outobj;
}


function importContentType(s : string) : string {
    // return 'C_' + s.substring(s.lastIndexOf(".") + 1);
    return s.replace(/\./g, "#");
}

function exportContentType(s : string) : string {
    // return 'adhocracy.contents.interfaces.' + s.substring(2);
    return s.replace(/#/g, ".");
}

function importPropertyType(s : string) : string {
    // return 'P_' + s.substring(s.lastIndexOf(".") + 1);
    return s.replace(/\./g, "#");
}

function exportPropertyType(s : string) : string {
    // return 'adhocracy.propertysheets.interfaces.' + s.substring(2);
    return s.replace(/#/g, ".");
}

function changeContentTypeRecursively(obj, f) {
    var t = Object.prototype.toString.call(obj);

    switch(t) {
    case '[object Object]':
        var newobj = {};
        for (var k in obj) {
            if (k == 'content_type') {
                newobj[k] = exportContentType(obj[k]);
            } else {
                newobj[k] = changeContentTypeRecursively(obj[k], f);
            }
        }
        return newobj;

    case '[object Array]':
        return obj.map(function(el) { return changeContentTypeRecursively(el, f); });

    default:
        return obj;
    }
}
