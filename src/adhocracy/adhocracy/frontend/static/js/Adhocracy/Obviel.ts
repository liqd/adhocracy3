/// <reference path="../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>

var obviel = require('obviel');

export function register_transformer() {

    // register global transformer to add obviel ifaces attribute to
    // the received json objects.  also runs s/\./#/g on property
    // sheet names.
    obviel.transformer(function(obj, path, name) {

        var main_interface = obj.content_type;
        if (typeof(main_interface) == 'undefined') {
            throw ("Object " + obj  + " from path " + path + " has no 'content_type' field");
        };
        obj.ifaces = [main_interface];

        for (var i in obj.data) {
            obj.ifaces.push(i);
        };

        // add ifaces to the propertysheet interfaces in the data field
        for (i in obj.data) {
            obj.data[i.replace(/\./g, "#")] = obj.data[i];
            delete obj.data[i];
        }

        return obj;
    });
}
