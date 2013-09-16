(function($, obviel) {

    // for editing

    // FIXME: Put in seperate module
    // Adds fields to make a view settings object editable.
    ad.Editable = function(child) {
        var result = {
            edit: function(ev) {
                    this.el.render(this.obj, "edit");
                },
        };
        $.extend(result, child);
        return result;
    };

    obviel.view({
        iface: 'adhocracy.interfaces.IParagraph',
        name: 'edit',
        obvt: '<div data-render="form"></div><button data-on="click|preview">Preview</div>',
        before: function() {
            this.obj.form = toForms(this.obj);
        },
        preview: function() {
            // FIXME: How do we get the real value?
            value = document.getElementById('obviel-field-auto0-text').value;
            this.obj.data['adhocracy#interfaces#IText'].text = value;
            this.el.render(this.obj);
        }
    });

    // end editing


    // Pool:
    obviel.view({
        iface: 'adhocracy.interfaces.IPool',
        obvtUrl: 'templates/IPool.obvt',
    });

    // Versionables
    var interfaces = ["IProposalContainer", "IParagraphContainer"];
    for (i in interfaces) {
        name = interfaces[i];
        console.log(('adhocracy.interfaces.' + name));
        obviel.view({
            iface: ('adhocracy.interfaces.' + name),
            before: function() {
                this.obj._versions_path = this.obj.meta.path + "/_versions";
            },
            obvt: '<div data-render="_versions_path"></div>',
        });
    };

    // small views for named items
    var interfaces = ["IProposalContainer", "IParagraphContainer"];
    for (i in interfaces) {
        name = interfaces[i];
        obviel.view({
            iface: 'adhocracy.interfaces.' + name,
            name: 'small',
            obvtUrl: 'templates/IName.small.obvt'
        });
    };

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IProposal',
        obvtUrl: 'templates/IProposal.obvt',
    }));

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IParagraph',
        obvtUrl: 'templates/IParagraph.obvt',
    }));

    obviel.view({
        iface: 'adhocracy.interfaces.INodeVersions',
        obvtUrl: "templates/INodeVersions.obvt"
    });

    obviel.view({
        iface: "formlist",
        obvt: '<div data-repeat="elements" data-render="@."></div>'
    });

    obviel.view({
        iface: 'debug_links',
        obvtUrl: 'templates/debug_links.obvt'
    });

}) (jQuery, obviel);
