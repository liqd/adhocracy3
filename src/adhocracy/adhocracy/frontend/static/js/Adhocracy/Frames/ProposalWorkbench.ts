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

    // the default view for an IDag is the default view for the head.
    // (if there is more than one head version...  öhm...  something!)
    // (for now, it's yet a little simpler: an IDag must always also
    // implement IPool; the IDag property sheet contains the version
    // numbers and possibly data on version edges; the pool contains
    // the actual versions.  this view just plucks the first element
    // of the IPool elements array and renders that.)
    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IDag',
        html: '<pre></pre>',
        render: function() {
            var elements = this.obj.data['adhocracy#propertysheets#interfaces#IPool'].elements;
            if (elements.length > 0) {
                var path = elements[0].path;
                if (typeof path == 'string') {
                    // this.render(path);  // FIXME: this recurses indefinitely
                    $('pre', this.el).text(path);
                } else {
                    throw ('bad reference' + elements.toString());
                }
            } else {
                this.el.text('[no versions]');
            }
        }
    });

    // default document (details).
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
