(function($, obviel) {

    // global transformer to put obviel iface attributes
    // into the received json objects.
    obviel.transformer(function(obj) {
        obj.iface = obj.main_interface;
        for (name in obj) {
            if (name != "main_interface" && name != "iface") {
                var data = obj[name];
                data["iface"] = name;
            };
        };
        return obj;
    });

    // views
    var rerender_edit_view = function (ev) {
        this.el.render(this.obj, 'edit');
    };

    obviel.view({
        iface: 'text',
        obvtUrl: 'text.display.obvt',
        edit: rerender_edit_view,
    });

    obviel.view({
        iface: 'text',
        name: 'edit',
        obvtUrl: 'text.edit.obvt',
        save: function() {
            text = document.getElementById('text_edit').value
            // FIXME: send a post message
            console.log('NYI: POST message should be sent here.');
            this.obj.text.content = text;
            this.el.render(this.obj);
        },
    });


    // Adds some crude error handling instead of the default
    // of silently ignoring errors.
    obviel.httpErrorHook(function(xhr) {
        console.log("httpError:");
        console.log(xhr);
    });


    // entry function
    $(document).ready(function() {
        // Initially renders to the main tag.
        $("#main").render("document.json");
    });

    // Re-renders the document.
    // FIXME: This has to be done better with some
    // kind of server side push (socket.io?)
    main_rerender = function() {
        $("#main").rerender();
    };

}) (jQuery, obviel);
