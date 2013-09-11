(function($, obviel) {

    obviel.view({
        iface: 'adhocracy.interfaces.IProposalContainer',
        before: function() {
            children_urls = [];
            for (i in this.obj.children) {
                children_urls.push(this.obj.children[i].path);
            };
            this.obj.children_urls = children_urls;
        },
        obvtUrl: 'templates/IProposalContainer.obvt',
    });

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IProposal',
        obvtUrl: 'templates/IProposal.obvt',
    }));

    obviel.view({
        iface: 'adhocracy.interfaces.INodeTags',
        obvt: "_tags"
    });

    obviel.view({
        iface: 'adhocracy.interfaces.INodeVersions',
        obvtUrl: "templates/INodeVersions.obvt"
    });

    obviel.view({
        iface: "formlist",
        obvt: '<div data-repeat="elements" data-render="@."></div>'
    });


}) (jQuery, obviel);
