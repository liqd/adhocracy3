/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>

// FIXME: remove submodules jquery-datalink/, jquery-bbq/ (hash urls
// aka fragments are obsoleted by html5 history api)

declare var $ : any;  // FIXME: use jquery git submodule, pick a more recent version, and tc-wrap it propertly.
declare var window : any;    // FIXME: type this more rigorously
declare var history : any;   // FIXME: type this more rigorously

var obviel : any = require('obviel');

import Obviel = require('Adhocracy/Obviel');
import Util = require('Adhocracy/Util');
import Css = require('Adhocracy/Css');

var templatePath : string = '/static/templates';
var appPrefix : string = '/app';
var jsonPrefix : string = '/adhocracy';

export function open_proposals(jsonUri : string, done ?: any) {

    // FIXME: rename open_proposals() to start()
    // FIXME: much of what happens in this function shouldn't happen here.  refactor!

    var appUri : string = appPrefix + jsonUri;

    Obviel.register_transformer();


    // views for center column: proposal directory

    obviel.view({
        iface: 'P_IPool',
        name: 'ProposalWorkbench',
        obvtUrl: templatePath + '/ProposalWorkbench.obvt',
    });

    obviel.view({
        iface: 'P_IPool',
        name: 'Directory',
        obvtUrl: templatePath + '/Directory.obvt',
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
        },
    });

    obviel.view({
        iface: 'P_IDocument',
        name: 'DirectoryEntry',
        obvtUrl: templatePath + '/DirectoryEntry.obvt',
        render: function() {
            $('a', this.el).on('click', function(e) {
                onClickDirectoryEntry(e.target.href);
                e.preventDefault();
            });
        },
    });


    // views for left column: detail view

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
        obvtUrl: templatePath + '/IDocumentDisplay.obvt',
    });

    obviel.view({
        iface: 'P_IDocument',
        name: 'edit',
        obvtUrl: templatePath + '/IDocumentEdit.obvt',
    });


    // paragraph.

    obviel.view({
        iface: 'P_IParagraph',
        obvtUrl: templatePath + '/IParagraphDisplay.obvt',

        edit: function(ev) {
            // re-render local object in edit mode.
            this.el.render(this.obj, 'edit');
        }
    });

    obviel.view({
        iface: 'P_IParagraph',
        name: 'edit',
        obvtUrl: templatePath + '/IParagraphEdit.obvt',

        reset: function(ev) {
            // load the object again from server and render it from scratch.
            var versionurl = this.obj['path'];
            this.el.render(versionurl, undefined);
        },
        save: function(ev) {
            // send local object to server.

            var parDAGPath = this.obj['path'].substring(0, this.obj['path'].lastIndexOf("/"));
            // a nice collection of other solutions for string disection is this here:
            // http://stackoverflow.com/questions/2187256/js-most-optimized-way-to-remove-a-filename-from-a-path-in-a-string
            // or, actually: var parDAGPath = this.obj['data']['P_IVersions']['versionpostroot'];

            var followsPath = (function() {
                // FIXME: this is not how we should do this!  either
                // make each P_IVersions know its own version number,
                // or when we fetch the DAG in order to get to the
                // HEAD, keep not only the HEAD, but also its version
                // number.  (this would be in another view.)

                // FIXME: Obviel.jsonAfterReceive() doesn't work here.
                // typescript doesn't like something.

                var parDAG = JSON.parse($.ajax(parDAGPath, { type: "GET", async: false }).responseText)
                var allDAGVersions = parDAG['data']['adhocracy.propertysheets.interfaces.IDAG']['versions'];
                if ('path' in allDAGVersions[0]) { return allDAGVersions[0]['path']; }
            })();

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


    // debugging.
    obviel.view({
        iface: 'debug_links',
        obvtUrl: templatePath + '/debug_links.obvt'
    });


    // history api (back button).
    window.addEventListener('popstate', function(event) {
        onClickDirectoryEntry(event.target.location.toString());  // (besides 'toString()' there is also 'pathname'...)
    });


    // start.
    history.pushState(null, null, appUri);
    $('#adhocracy').render(jsonUri, 'ProposalWorkbench');

    // FIXME: deep links don't work.  The contents of jsonUri must
    // contain a proposal pool that contains proposal dags.  Regarding
    // URLs that open a particular proposal in detail view directly,
    // there are at least two options:
    //
    // 1. fixed object hierarchy: if the object under jsonUri does not
    // work as a proposal pool, try proposal dag, and then proposal
    // version.  (dag: remove last stub from the path and render that
    // as pool/worbench; then render the full path into detail view;
    // version: same, but remove last two stubs, not one.)
    //
    // 2. get parameters: encode the uri of the proposal to be opened
    // in detail view in a get parameter.  this does not assume any
    // fixed object hierarchy, but it is more awkward if you like
    // typing in urls manually.
    //
    // either way this has to be fixed, or reload and deep links must
    // be considered broken.

    // FIXME: history api only goes back one step, and does not go
    // forward at all.
}

// if the url with which this page was loaded mentions a particular
// pool or a particular detail view, return that as poolUri.
// otherwise, return the default passed as argument to this function.
export function poolUri(defaultUri) {
    var uri = window.location.pathname.match(new RegExp('^' + appPrefix + '(' + jsonPrefix + '.*)$'));
    if (uri) {
        return uri[1];
    } else {
        return defaultUri;
    }
}

function onClickDirectoryEntry(pathRaw : string) {
    var pathHtml : string = pathRaw.replace(new RegExp('^http://[^:/]+(:\\d+)?'), '');
    var pathJson : string = pathHtml.replace(new RegExp('^' + appPrefix), '');

    history.pushState(null, null, pathHtml);
    $('#proposal_workbench_detail').render(pathJson);
    $('#debug_links').render({ 'iface': 'debug_links', 'path': pathJson });
}

export function newProposal() {
    console.log('[newProposal]');
}

export function newParagraph() {
    console.log('[newParagraph]');
}
