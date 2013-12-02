/// <reference path="../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>

var obviel = require('obviel');

export function register_transformer() {

    // register global transformer to add obviel ifaces attribute to
    // the received json objects.  also runs s/\./#/g on property
    // sheet names.
    obviel.transformer(function(obj, path, name) {

        // strip noise from content type and property sheet types
        obj.content_type = 'C_' + obj.content_type.substring(obj.content_type.lastIndexOf(".") + 1);

        for (i in obj.data) {
            var i_local = 'P_' + i.substring(i.lastIndexOf(".") + 1);
            obj.data[i_local] = obj.data[i];
            delete obj.data[i];
        }

        // add content type to ifaces
        var main_interface = obj.content_type;
        if (typeof(main_interface) == 'undefined') {
            throw ("Object " + obj  + " from path " + path + " has no 'content_type' field");
        };
        obj.ifaces = [main_interface];

        // add all property sheet types as ifaces
        for (var i in obj.data) {
            obj.ifaces.push(i);
        };

        return obj;
    });
}


// out-transformer.  call this on every object before sending it back
// to the server.
export function make_postable(inobj) {
    var i;
    var outobj = {};

    outobj.content_type = 'adhocracy.contents.interfaces.' + inobj.content_type.substring(2);
    outobj.data = {};

    for (i in inobj['data']) {
        var i_remote = 'adhocracy.propertysheets.interfaces.' + i.substring(2);
        outobj.data[i_remote] = inobj.data[i];
    }

    return outobj;
}
