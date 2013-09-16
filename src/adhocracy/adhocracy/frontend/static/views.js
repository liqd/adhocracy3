(function($, obviel) {

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
            obvt: '<div data-render="_versions_path">hu</div>',
        });
    };

    // small views for named items
    var interfaces = ["IProposalContainer", "IParagraphContainer"];
    for (i in interfaces) {
        name = interfaces[i];
        obviel.view({
            iface: 'adhocracy.interfaces.' + name,
            name: 'small',
            obvtUrl: 'templates/small.obvt'
        });
    };



    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IProposal',
        obvtUrl: 'templates/IProposal.obvt',
    }));

    obviel.view({
        iface: 'adhocracy.interfaces.IParagraph',
        obvtUrl: 'templates/IParagraph.obvt',
    });

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
