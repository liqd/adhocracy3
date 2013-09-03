(function($, obviel) {

    // global transformer to put obviel iface attributes
    // into the received json objects.
    obviel.transformer(function(obj) {
	console.log("transformer-in");
	console.log(obj);

        obj.iface = obj.main_interface;

	// sub-interfaces: a node can be all of 'document',
	// 'commentable', 'likeable'.  the following loop iterates
	// over the latter two.  XXX: explain better.

	// FIXME: add attribute "other_interfaces": [] to a3 rest api.
	// better yet: put all sub-interfaces into a proper attribute
	// "subinterfaces".  or give them prefix "__widget__"?
	// they're not necessarily widgets, though.

        for (name in obj) {
            if (name != "main_interface" && name != "iface") {
                var data = obj[name];
                data["iface"] = name;
            };
        };

	console.log(obj);
	console.log("transformer-out");
        return obj;
    });

    // views

    // Adds fields to make a view settings object editable.
    var Editable = function(child) {
        var result = {
            edit: function(ev) {
                    this.el.render(toForm(this.obj));
                },
        };
        $.extend(result, child);
        return result;
    };

    obviel.view(Editable({
        iface: 'text',
        obvtUrl: 'text.display.obvt',
    }));

    // Adds some crude error handling instead of the default
    // of silently ignoring errors.
    obviel.httpErrorHook(function(xhr) {
        console.log("httpError:");
        console.log(xhr);
    });

    // entry function
    $(document).ready(function() {
        // Initially renders to the main tag.
        $("#main").render("paragraph1.json");
    });

    // Re-renders the document.
    // FIXME: This has to be done better with some
    // kind of server side push (socket.io?)
    main_rerender = function() {
        $("#main").rerender();
    };

}) (jQuery, obviel);



/* obsolete code:

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

    obviel.view(Editable({
        iface: 'document',
        obvtUrl: 'document.display.obvt',
    }));

    obviel.view({
        iface: 'document',
        name: 'edit',
    });
*/

