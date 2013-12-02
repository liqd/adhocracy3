/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery.bbq/jquery.bbq.d.ts"/>

declare var $ : any;  // FIXME: use jquery git submodule, pick a more recent version, and tc-wrap it propertly.

var obviel : any = require('obviel');
var bbq = require('bbq');

import Obviel = require('Adhocracy/Obviel');
import Util = require('Adhocracy/Util');
import Css = require('Adhocracy/Css');

export function open_proposals(uri, done) {

    // FIXME: much of what happens in this function shouldn't.  refactor!

    Obviel.register_transformer();


    // proposal directory

    obviel.view({
        iface: 'P_IPool',
        name: 'ProposalWorkbench',
        obvtUrl: 'templates/ProposalWorkbench.obvt',
    });

    obviel.view({
        iface: 'P_IPool',
        name: 'Directory',
        obvtUrl: 'templates/Directory.obvt',
    });

    obviel.view({
        iface: 'P_IDAG',
        name: 'DirectoryEntry',

        render: function() {
            if (this.obj.data.P_IDAG.versions.length > 0) {
                this.el.render(this.obj.data.P_IDAG.versions[0].path, 'DirectoryEntry');
            } else {
                this.el.text('[no versions]');
            }
        }
    });

    obviel.view({
        iface: 'P_IDocument',
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
            elements = this_.obj.data['P_IDAG'].versions;
        } catch (e) {
            throw ('[missing or bad IDAG property sheet: ' + this_.toString() + ']');
        }

        if (elements.length > 0) {
            // FIXME: use HEAD tag to get to path.  (this requires the backend to support tags.)
            // var path = elements[elements.length - 1].path;  // (not) last element is the youngest.
            var path = elements[0].path;  // first element is the youngest.
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
        iface: 'P_IDAG',
        html: '<pre></pre>',
        render: function() { render_DAG(this, undefined); }
    });

    obviel.view({
        iface: 'P_IDAG',
        name: 'edit',
        html: '<pre></pre>',
        render: function() { render_DAG(this, 'edit'); }
    });


    // document.

    obviel.view({
        iface: 'P_IDocument',
        obvtUrl: 'templates/IDocumentDisplay.obvt',
    });

    obviel.view({
        iface: 'P_IDocument',
        name: 'edit',
        obvtUrl: 'templates/IDocumentEdit.obvt',
    });


    // paragraph.

    obviel.view({
        iface: 'P_IParagraph',
        obvtUrl: 'templates/IParagraphDisplay.obvt',

        edit: function(ev) {
            // re-render local object in edit mode.
            this.el.render(this.obj, 'edit');
        }
    });

    obviel.view({
        iface: 'P_IParagraph',
        name: 'edit',
        obvtUrl: 'templates/IParagraphEdit.obvt',

        reset: function(ev) {
            // load the object again from server and render it from scratch.
            var versionurl = this.obj['path'];
            this.el.render(versionurl, undefined);
        },
        save: function(ev) {
            // send local object to server.

            var parDAGPath = this.obj['path'].substring(0, this.obj['path'].lastIndexOf("/"));
            // a nice collection of other solutions is here:
            // http://stackoverflow.com/questions/2187256/js-most-optimized-way-to-remove-a-filename-from-a-path-in-a-string
            // or, actually: var parDAGPath = this.obj['data']['P_IVersions']['versionpostroot'];

            var followsPath = parDAGPath + "/v_1"  // FIXME: hard-coded predecessor version is wrong.  refer to HEAD tag instead.
            delete this.obj['data']['P_IVersions'];

            this.obj['data']['P_IParagraph']['text'] =
                $('textarea', this.el)[0].value;

            var postobj = Obviel.make_postable(this.obj);

            $.ajax(parDAGPath, {
                type: "POST",
                dataType: "json",
                contentType: "application/json",
                headers: { follows: followsPath },
                data: JSON.stringify(postobj)
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
                // the server (websockets).  this workaround 'done'
                // handler should go away completely.

                // (regarding the work-around: i am expecting obviel
                // to re-pull the proposal from the server, but i'm
                // not sure if that always happens.  what does the
                // obviel code say?  (Update on this: paragraph model
                // objects are *not* refreshed from the server when
                // rerender is called on the proposal node!)
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
