
(function($, obviel) {

    // global transformer to put obviel iface attributes
    // into the received json objects.
    obviel.transformer(function(obj, path, name) {

        var main_interface = obj.meta.content_type;
        if (typeof(main_interface) == 'undefined') {
            console.log(obj);
            throw ("Object from path " + path + " does not contain 'meta.content_type'");
        };
        obj.ifaces = [main_interface];

        for (i in obj.data) {
            obj.data[i.replace(/\./g, "#")] = obj.data[i];
            delete obj.data[i];
        }

        // sub-interfaces: a node can be all of 'document',
        // 'commentable', 'likeable'.  the following loop iterates
        // over the latter two.  XXX: explain better.

        for (name in obj.other_interfaces) {
            var data = obj[name];
            data.ifaces = [name];
        };

        return obj;
    });

    // Adds some crude error handling instead of the default
    // of silently ignoring errors.
    obviel.httpErrorHook(function(xhr) {
        console.log("httpError:");
        console.log(xhr);
    });

    $(window).bind('hashchange', function(ev) {
        var path = ev.fragment;
        $('#debug_links').render({
            'iface': 'debug_links',
            'path': path
        });
        $('#main').render(path);
    });

    // entry function
    $(document).ready(function() {
        // initially renders to the main tag
        $(window).trigger('hashchange');
    });

}) (jQuery, obviel);
