/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery.bbq/jquery.bbq.d.ts"/>

declare var $ : any;  // FIXME

var obviel : any = require('obviel');
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

    // the default view for an IDAG is the default view for the head.
    // (if there is more than one head version...  öhm...  something!)
    // (for now, it's yet a little simpler: an IDAG must always also
    // implement IPool; the IDAG property sheet contains the version
    // numbers and possibly data on version edges; the pool contains
    // the actual versions.  this view just plucks the first element
    // of the IPool elements array and renders that.)
    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IDAG',
        html: '<pre></pre>',
        render: function() {
            var elements;

            try {
                elements = this.obj.data['adhocracy#propertysheets#interfaces#IPool'].elements;
            } catch (e) {
                throw ('[missing or bad IDAG property sheet: ' + this.toString() + ']');
            }

            if (elements.length > 0) {
                var path = elements[0].path;
                if (typeof path == 'string') {
                    this.el.render(path);
                } else {
                    throw ('[bad reference object: ' + elements.toString() + ']');
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

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IParagraph',
        obvtUrl: 'templates/IParagraph.obvt',
    });


    // some crude error handling (instead of the default of silently
    // ignoring errors.)

    obviel.httpErrorHook(function(xhr) {
        console.log("httpError:");
        console.log(xhr);
    });


    // clickability

    obviel.view({
        iface: 'debug_links',
        obvtUrl: 'templates/debug_links.obvt'
    });

    // hashchange and fragment handling will go away and be replaced
    // by the new history api.  (suggested by tobias)

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
