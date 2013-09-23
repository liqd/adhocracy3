
(function($, obviel) {

    // global transformer to put obviel iface attributes
    // into the received json objects.
    obviel.transformer(function(obj, path, name) {

        ad.repo[path] = obj;  // FIXME: do a deep copy here.

        var main_interface = obj.meta.content_type;
        if (typeof(main_interface) == 'undefined') {
            console.log(obj);
            throw ("Object from path " + path + " does not contain 'meta.content_type'");
        };
        obj.ifaces = [main_interface];

        for (i in obj.data) {
            obj.ifaces.push(i);
            obj.data[i].ifaces = i;
            obj.data[i.replace(/\./g, "#")] = obj.data[i];
            delete obj.data[i];
        }

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
