/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery.bbq/jquery.bbq.d.ts"/>

declare var $ : any;  // FIXME

var obvieltemplate = require('obvieltemplate');
var obviel = require('obviel');
var bbq = require('bbq');

import Obviel = require('Adhocracy/Obviel');
import Util = require('Adhocracy/Util');

export function open_proposals(uri, done) {

    // FIXME: much of what happens in this function shouldn't.  refactor!

    Obviel.register_transformer();


    // proposal directory

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IPool',
        name: 'ProposalWorkbench',
        obvtUrl: 'templates/ProposalWorkbench.obvt',
    });

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IPool',
        name: 'Directory',
        obvtUrl: 'templates/Directory.obvt',
    });

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IName',
        name: 'DirectoryEntry',
        obvtUrl: 'templates/DirectoryEntry.obvt',
    });


    // detail view

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IDag',
        obvtUrl: 'templates/IDag.obvt',
    });

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IDocument',
        obvtUrl: 'templates/IDocument.obvt',
    });


    // clickability

    obviel.view({
        iface: 'debug_links',
        obvtUrl: 'templates/debug_links.obvt'
    });

    $(window).bind('hashchange', function(event) {
        var path = event.fragment;
        $('#debug_links').render({
            'iface': 'debug_links',
            'path': path
        });
        $('#proposal_workbench_detail').render(path);
    });


    // start

    $('#adhocracy').render('/adhocracy/', 'ProposalWorkbench').done(function() {
        $(window).trigger('hashchange');
        done();
    });
}
