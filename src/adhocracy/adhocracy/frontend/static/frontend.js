(function($, obviel) {

    // global transformer to put obviel iface attributes
    // into the received json objects.
    obviel.transformer(function(obj, path, name) {
        var main_interface = obj.meta.content_type;
        if (typeof(main_interface) == 'undefined') {
            console.log(obj);
            throw ("Object from path " + path + " does not contain a field 'main_interface'");
        };
        obj.ifaces = [main_interface];

        for (i in obj.data) {
            obj.data[i.replace(/\./g, "#")] = obj.data[i];
            delete obj.data[i];
        }

        // sub-interfaces: a node can be all of 'document',
        // 'commentable', 'likeable'.  the following loop iterates
        // over the latter two.  XXX: explain better.

        // FIXME: maybe put all sub-interfaces into a proper attribute
        // "subinterfaces".  or give them prefix "__widget__"?
        // they're not necessarily widgets, though.

        for (name in obj.other_interfaces) {
            var data = obj[name];
            data.ifaces = [name];
        };

        return obj;
    });

    // views
    // See also in views.js

    // Adds fields to make a view settings object editable.
    ad.Editable = function(child) {
        var result = {
            edit: function(ev) {
                    this.el.render(toForms(this.obj));
                },
        };
        $.extend(result, child);
        return result;
    };

    obviel.view(ad.Editable({
        iface: 'text',
        obvtUrl: 'templates/text.display.obvt',
    }));

    obviel.view({
        iface: 'text',
        name: 'short',
        obvt: '{text.content}'
    });

    obviel.view(ad.Editable({
        iface: 'document',
        obvtUrl: 'templates/document.display.obvt',
    }));

    obviel.view({
        iface: 'document',
        name: 'link',
        obvt: '<a href="#{path}" data-render="document.title|short"></a>'
    });

    obviel.view({
        iface: 'root',
        obvt: '<a href="#{link}">link</a>'
    });

    obviel.view({
        iface: 'listing',
        obvtUrl: 'templates/listing.obvt'
    });

    // Adds some crude error handling instead of the default
    // of silently ignoring errors.
    obviel.httpErrorHook(function(xhr) {
        console.log("httpError:");
        console.log(xhr);
    });

    $(window).bind('hashchange', function(ev) {
        var path = ev.fragment;
        console.log("hashchange: " + path);
        $('#main').render(path);
    });

    // entry function
    $(document).ready(function() {
        // initially renders to the main tag
        $(window).trigger('hashchange');
    });

}) (jQuery, obviel);
