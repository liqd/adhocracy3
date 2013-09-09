(function($, obviel) {

    obviel.view(ad.Editable({
        iface: 'IProposalContainer',
        before: function() {
            children_urls = [];
            for (i in this.obj.children) {
                children_urls.push(this.obj.children[i].path);
                this.obj.children_urls = children_urls;
            };
        },
        obvtUrl: 'templates/IProposalContainer.obvt',
    }));

    obviel.view(ad.Editable({
        iface: 'IProposal',
        obvtUrl: 'templates/IProposal.obvt',
    }));

    obviel.view({
        iface: 'INodeTags',
        obvt: "_tags"
    });

    obviel.view({
        iface: 'INodeVersions',
        obvtUrl: "templates/INodeVersions.obvt"
    });


}) (jQuery, obviel);
