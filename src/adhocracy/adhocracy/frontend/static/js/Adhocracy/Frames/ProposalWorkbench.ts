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
    function render_DAG(this_, view_name) {
        var elements;

        try {
            elements = this_.obj.data['adhocracy#propertysheets#interfaces#IPool'].elements;
        } catch (e) {
            throw ('[missing or bad IDAG property sheet: ' + this_.toString() + ']');
        }

        if (elements.length > 0) {
            var path = elements[elements.length - 1].path;  // last element is the youngest.
            if (typeof path == 'string') {
                this_.el.render(path, view_name);
            } else {
                throw ('[bad reference object: ' + elements.toString() + ']');
            }
        } else {
            this_.el.text('[no versions]');
        }
    }

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IDAG',
        html: '<pre></pre>',
        render: function() { render_DAG(this, undefined); }
    });

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IDAG',
        name: 'edit',
        html: '<pre></pre>',
        render: function() { render_DAG(this, 'edit'); }
    });


    // document.

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IDocument',
        obvtUrl: 'templates/IDocumentDisplay.obvt',
    });

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IDocument',
        name: 'edit',
        obvtUrl: 'templates/IDocumentEdit.obvt',
    });


    // paragraph.

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IParagraph',
        obvtUrl: 'templates/IParagraphDisplay.obvt',

        edit: function(ev) {
            // re-render local object in edit mode.
            this.el.render(this.obj, 'edit');
        }
    });

    obviel.view({
        iface: 'adhocracy.propertysheets.interfaces.IParagraph',
        name: 'edit',
        obvtUrl: 'templates/IParagraphEdit.obvt',

        reset: function(ev) {
            // load the object again from server and render it from scratch.
            var versionurl = this.obj['path'];
            this.el.render(versionurl, undefined);
        },
        save: function(ev) {
            // send local object to server.  (FIXME: updates will probably come via web sockets.)

            // var dagurl = this.obj['data']['adhocracy.propertysheets.interfaces.IVersions']['versionpostroot'];

            // (FIXME: this is cheating, but it works for now, kind of.)
            var dagurl = this.obj['path'].substring(0, this.obj['path'].length - 2);

            delete this.obj['data']['adhocracy#propertysheets#interfaces#IVersions'];

            this.obj['data']['adhocracy#propertysheets#interfaces#IParagraph']['text'] =
                $('textarea', this.el)[0].value;

            Obviel.make_postable(this.obj);

            $.ajax(dagurl, {
                type: "POST",
                dataType: "json",
                contentType: "application/json",
                data: JSON.stringify(this.obj)
            }).fail(function(err, err2) {
                console.log('ajax post failed!');
                console.log(err);
                console.log(err2);
            }).done(function() {
                console.log('ajax post succeeded!');

                // at this point, we trigger a re-render of the DAG.
                // in order to get to the path of the DAG, we chop off
                // the version part of the path of the version
                // currently rendered.

                // FIXME: re-render of anything should be triggered by
                // the server (websockets?  eventsource?  long-poll?).
                // this 'done' handler should go away completely.

                // FIXME: i am expecting obviel to re-pull the
                // proposal from the server, but i'm not sure if that
                // always happens.  what does the obviel code say?

                $('#proposal_workbench_detail').rerender();
            });
        }
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
    });
}
