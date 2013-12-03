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
export function jsonAfterReceive(inobj : Types.Content, path) {
    // strip noise from content type and property sheet types
    var outobj : Types.Content = {
        content_type: 'C_' + inobj.content_type.substring(inobj.content_type.lastIndexOf(".") + 1),
        path: inobj.path,
        data: {}
    }

    for (i in inobj.data) {
        var i_local = 'P_' + i.substring(i.lastIndexOf(".") + 1);
        outobj.data[i_local] = inobj.data[i];
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
export function jsonBeforeSend(inobj : Types.Content) {
    var i;
    var outobj : Types.Content = {
        content_type: 'adhocracy.contents.interfaces.' + inobj.content_type.substring(2),
        data: {}
    };

    // FIXME: Get this list from the server!  (How?)
    var readOnlyProperties = ['P_IVersions'];

    for (i in inobj['data']) {
        if (readOnlyProperties.indexOf(i) < 0) {
            var i_remote = 'adhocracy.propertysheets.interfaces.' + i.substring(2);
            outobj.data[i_remote] = inobj.data[i];
        }
    }

    return outobj;
}
