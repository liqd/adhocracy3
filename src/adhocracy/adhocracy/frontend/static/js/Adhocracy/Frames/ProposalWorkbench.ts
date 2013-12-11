/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

declare var $ : any;  // FIXME: use jquery git submodule, pick a more recent version, and tc-wrap it propertly.
declare var window : any;    // FIXME: type this more rigorously
declare var history : any;   // FIXME: type this more rigorously

import Types = require('Adhocracy/Types');
// import Obviel = require('Adhocracy/Obviel');
// import Util = require('Adhocracy/Util');
import Css = require('Adhocracy/Css');

var templatePath : string = '/static/templates';
var appPrefix : string = '/app';
var jsonPrefix : string = '/adhocracy';





/*

export function open_proposals(jsonUri : string, done ?: any) {

    // FIXME: rename open_proposals() to start()
    // FIXME: much of what happens in this function shouldn't happen here.  refactor!

    var appUri : string = appPrefix + jsonUri;
    var currentProposalVersionPath;

    Obviel.register_transformer();


    // views for center column: proposal directory

    obviel.view({
        iface: 'adhocracy#propertysheets#interfaces#IPool',
        name: 'ProposalWorkbench',
        obvtUrl: templatePath + '/ProposalWorkbench.obvt',
        render: function() {
            $(Css.clsd('create_proposal_button'))
                .on('click',
                    function() { return newProposal(jsonUri) });
            $(Css.clsd('create_paragraph_button'))
                .on('click',
                    function() { return newParagraph(currentProposalVersionPath); });
        },
    });

    obviel.view({
        iface: 'adhocracy#propertysheets#interfaces#IPool',
        name: 'Directory',
        obvtUrl: templatePath + '/Directory.obvt',
        render: function() {
            updateWs('#proposal_workbench_directory', this.obj.path, 'Directory');
            // FIXME: get the sizzle from this.el rather than statically?
        },
    });

    obviel.view({
        iface: 'adhocracy#propertysheets#interfaces#IDAG',
        name: 'DirectoryEntry',

        render: function() {
            var dag = this.obj.data['adhocracy#propertysheets#interfaces#IDAG'];
            if (dag.versions.length > 0) {
                this.el.render(dag.versions[0].path, 'DirectoryEntry');
            } else {
                this.el.text('[no versions]');
            }
        },
    });

    obviel.view({
        iface: 'adhocracy#propertysheets#interfaces#IDocument',
        name: 'DirectoryEntry',
        obvtUrl: templatePath + '/DirectoryEntry.obvt',
        render: function() {
            $('a', this.el).on('click', function(e) {
                renderDetail(e.target.href, undefined);
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
            elements = this_.obj.data['adhocracy#propertysheets#interfaces#IDAG'].versions;
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
        iface: 'adhocracy#propertysheets#interfaces#IDAG',
        render: function() {
            updateWs('#proposal_workbench_detail', this.obj.path, undefined);
            // FIXME: get the sizzle from this.el?
            render_DAG(this, undefined);
        },
    });

    // FIXME: these two view only differ in view name.  construct them in a more concise way!
    obviel.view({
        iface: 'adhocracy#propertysheets#interfaces#IDAG',
        name: 'edit',
        render: function() {
            closeWs('#proposal_workbench_detail');
            // FIXME: get the sizzle from this.el?
            render_DAG(this, 'edit');
        }
    });


    // document.

    obviel.view({
        iface: 'adhocracy#propertysheets#interfaces#IDocument',
        obvtUrl: templatePath + '/IDocumentDisplay.obvt',

        render: function() {
            currentProposalVersionPath = this.obj.path;
        },

        edit: function() {
            closeWs('#proposal_workbench_detail');
            this.el.render(this.obj, 'edit');
        },
    });

    obviel.view({
        iface: 'adhocracy#propertysheets#interfaces#IDocument',
        name: 'edit',
        obvtUrl: templatePath + '/IDocumentEdit.obvt',

        render: function() {
            currentProposalVersionPath = this.obj.path;
        },

        reset: function() {
            var dagPath = Util.parentPath(this.obj.path);
            var dagView = undefined;
            $('#proposal_workbench_detail').render(dagPath, dagView);
            updateWs('#proposal_workbench_detail', dagPath, dagView);
        },

        save: function() {
            // see (view adhocracy#propertysheets#interfaces#IParagraph|edit).save function for more
            // documentation.  (there is also a utility function
            // hidden here that should be factored out.)
            var docDAGPath = Util.parentPath(this.obj.path);
            var docPoolPath = Util.parentPath(docDAGPath);

            var predecessorPath = (function() {
                // FIXME: why am i not using the Util.* convenience
                // http api for this?
                var docDAG = JSON.parse($.ajax(docDAGPath, { type: "GET", async: false }).responseText);
                var allVersions = docDAG.data['adhocracy.propertysheets.interfaces.IDAG'].versions;
                if (allVersions && allVersions[0] && 'path' in allVersions[0]) {
                    return allVersions[0].path;
                }
            })();

            var doc = this.obj.data['adhocracy#propertysheets#interfaces#IDocument'];
            doc.title = $(Css.clsd('edit_document_title'), this.el)[0].value;
            doc.description = $(Css.clsd('edit_document_description'), this.el)[0].value;

            Util.postx(docDAGPath, this.obj, { follows: predecessorPath }, docDAGPathDone, function(xhr, text, exception) {
                console.log('ajax post failed!\n' + [xhr, text, exception].toString())
            });

            function docDAGPathDone(response) {
                // while in edit mode, the web socket is closed, and
                // changes won't be visible.  now we need to run one
                // re-render manually and re-open the we bsocket.
                //
                // FIXME: this is the same as the reset method above.
                // remove redundancy!

                var dagPath = Util.parentPath(response.path);
                var dagView = undefined;
                $('#proposal_workbench_detail').render(dagPath, dagView);
                updateWs('#proposal_workbench_detail', dagPath, dagView);
            }
        },
    });



    // paragraph.

    obviel.view({
        iface: 'adhocracy#propertysheets#interfaces#IParagraph',
        obvtUrl: templatePath + '/IParagraphDisplay.obvt',

        edit: function(ev) {
            // re-render local object in edit mode.
            this.el.render(this.obj, 'edit');
        }
    });

    obviel.view({
        iface: 'adhocracy#propertysheets#interfaces#IParagraph',
        name: 'edit',
        obvtUrl: templatePath + '/IParagraphEdit.obvt',

        reset: function(ev) {
            // load the object again from server and render it from scratch.
            this.el.render(this.obj.path, undefined);
        },
        save: function(ev) {
            // send local object to server.

            var parDAGPath = Util.parentPath(this.obj.path);
            // a nice collection of other solutions for string disection is this here:
            // http://stackoverflow.com/questions/2187256/js-most-optimized-way-to-remove-a-filename-from-a-path-in-a-string
            // or, actually: var parDAGPath = this.obj.data['adhocracy#propertysheets#interfaces#IVersions']['versionpostroot'];

            var followsPath = (function() {
                // FIXME: this is not how we should do this!  either
                // make each adhocracy#propertysheets#interfaces#IVersions know its own version number,
                // or when we fetch the DAG in order to get to the
                // HEAD, keep not only the HEAD, but also its version
                // number.  (this would be in another view.)

                // FIXME: Obviel.jsonAfterReceive() doesn't work here.
                // typescript doesn't like something.

                var parDAG = JSON.parse($.ajax(parDAGPath, { type: "GET", async: false }).responseText)
                var allDAGVersions = parDAG.data['adhocracy.propertysheets.interfaces.IDAG'].versions;
                if ('path' in allDAGVersions[0]) { return allDAGVersions[0].path; }
            })();

            this.obj['data']['adhocracy#propertysheets#interfaces#IParagraph']['text'] =
                $('textarea', this.el)[0].value;

            var postobj = Obviel.jsonBeforeSend(this.obj);

            $.ajax(parDAGPath, {
                type: "POST",
                dataType: "json",
                contentType: "application/json",
                headers: { follows: followsPath },
                data: JSON.stringify(postobj)
            }).fail(function(xhr, text, exception) {
                console.log('ajax post failed!\n' + [xhr, text, exception].toString());
            }).done(function() {
                console.log('ajax post succeeded!');
            });
        }
    });


    // some crude error handling (instead of the default of silently
    // ignoring errors.)

    obviel.httpErrorHook(function(xhr) {
        console.log('ajax error in obviel!\n' + [xhr].toString());
    });


    // debugging.
    obviel.view({
        iface: 'debug_links',
        obvtUrl: templatePath + '/debug_links.obvt'
    });


    // history api (back button).
    window.addEventListener('popstate', function(event) {
        renderDetail(event.target.location.toString(), undefined);  // (besides 'toString()' there is also 'pathname'...)
        // FIXME: i don't think this is working properly yet.  but
        // it's just the 'back' button.
    });


    // start.
    history.pushState(null, null, appUri);
    $('#adhocracy').render(jsonUri, 'ProposalWorkbench');

    // FIXME: deep links don't work.  The contents of jsonUri must
    // contain a proposal pool that contains proposal dags.  Regarding
    // URIs that open a particular proposal in detail view directly,
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
    // typing in uris manually.
    //
    // either way this has to be fixed, or reload and deep links must
    // be considered broken.

    // FIXME: history api only goes back one step, and does not go
    // forward at all.
}



// and-whatnot

// if the uri with which this page was loaded mentions a particular
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



// object updates

function newProposal(poolUri : string) : void {
    console.log('[newProposal]');
    if (!poolUri) {
        throw "newProposal: bad argument";
    }

    function failDefault() {
        throw "newProposal: ajax error.";
    }

    var propDag : Types.Content = { content_type: 'adhocracy#contents#interfaces#IProposalContainer' };
    Util.post(poolUri, propDag, propDagDone, failDefault);

    function propDagDone(propDagResponse) {
        var propVersion : Types.Content = { content_type: 'adhocracy#contents#interfaces#IProposal' };
        Util.post(propDagResponse.path, propVersion, propVersionDone, failDefault);
    }

    function propVersionDone(propVersionResponse) {
        renderDetail(appPrefix + Util.parentPath(propVersionResponse.path), 'edit');
    }
}

function newParagraph(propVersionUri : string) : void {
    console.log('[newParagraph]');
    if (!propVersionUri)
        return;  // (there is currently no proposal open in detail view)

    // FIXME: do not always use the head of the document!  this
    // function should get a specific version that it is supposed to
    // create a successor of.

    var parDag      : Types.Content  = { content_type: 'adhocracy#contents#interfaces#IParagraphContainer' };
    var propDagUri  : string         = Util.parentPath(propVersionUri);
    Util.post(propDagUri, parDag, postParDagDone,
              function() { throw "newParagraph: ajax error."; });

    function postParDagDone(parDagResponse) {
        var parVersion : Types.Content = { content_type: 'adhocracy#contents#interfaces#IParagraph' };
        Util.post(parDagResponse.path, parVersion, postParVersionDone,
                  function() { throw "newParagraph: ajax error."; });
    }

    var parVersionReference : Types.Content = {
        content_type: 'adhocracy#contents#interfaces#IParagraph',
        reference_colour: 'EssenceRef'
    }

    function postParVersionDone(parVersionResponse) {
        parVersionReference.path = parVersionResponse.path;
        Util.get(Util.parentPath(propVersionUri), getPropDagDone,
                 function() { throw "newParagraph: ajax error."; });
    }

    function getPropDagDone(propDagResponse) {
        var propPredecessorPath : string = propDagResponse.data['adhocracy#propertysheets#interfaces#IDAG'].versions[0].path;
        Util.get(propPredecessorPath, propPredecessorDone,
                 function() { throw "newParagraph: ajax error."; });
    }

    function propPredecessorDone(propPredecessorResponse) {
        var propPredecessorPath = propPredecessorResponse.path;
        var propSuccessor = propPredecessorResponse;
        propSuccessor.data['adhocracy#propertysheets#interfaces#IDocument'].paragraphs.push(parVersionReference);
        Util.postx(propDagUri, propSuccessor, { follows: propPredecessorPath }, propSuccessorDone,
                   function() { throw "newParagraph: ajax error."; });
    }

    function propSuccessorDone() {
    }
}



// rerender helpers

function renderDetail(pathRaw : string, viewname : string) : void {
    var pathHtml : string = pathRaw.replace(new RegExp('^http://[^:/]+(:\\d+)?'), '');
    var pathJson : string = pathHtml.replace(new RegExp('^' + appPrefix), '');

    history.pushState(null, null, pathHtml);
    $('#proposal_workbench_detail').render(pathJson, viewname);
    $('#debug_links').render({ 'iface': 'debug_links', 'path': pathJson });
}



// web sockets

var wsdict = {};

// Create a web socket and connect it to a dom element for online
// updates.  If an old web socket was registered, close and delete it.
// Do *not* render the dom element once initially.  Do *not* push new
// state to history api stack (this is only desired for *one* dom
// element per page).
//
// FIXME: each time a render is triggered, the queue should be flushed
// and compressed first.  as it is, if a proposal pool is growing by
// three proposals before a client looks at the web socket queue
// again, the client will render the latest version three times rather
// than once.
export function updateWs(sizzle : string, path : string, viewName ?: string) : void {
    console.log('updateWs: ' + sizzle, path, viewName);

    if (sizzle in wsdict) {
        if (wsdict[sizzle].path == path) {
            wsdict[sizzle].viewName = viewName;
            return;
        } else {
            closeWs(sizzle);
            makeNew();
            return;
        }
    } else {
        makeNew();
        return;
    }

    function makeNew() {
        var wsuri = 'ws://' + window.location.host + path + '?ws=node';
        var ws = new WebSocket(wsuri);

        wsdict[sizzle] = {
            path: path,
            viewName: viewName,
            ws: ws,
        }

        ws.onmessage = function(event) {
            // var path = event.data;
            // (we don't need to do this; every path gets its own web socket for now.)

            console.log('ws.onmessage: updating '  + wsdict[sizzle].path
                        + ' with view '            + wsdict[sizzle].viewName
                        + ' on dom node:\n'        + sizzle);
            $(sizzle).render(wsdict[sizzle].path, wsdict[sizzle].viewName);
        };

        // some console info to keep track of things happening:
        ws.onerror = function(event) {
            console.log('ws.onerror: ' + event.toString());
        };
        ws.onopen = function() {
            console.log('[ws.onopen]');
        };
        ws.onclose = function() {
            console.log('[ws.onclose]');
        };
    }
}

export function closeWs(sizzle : string) {
    console.log('closeWs: ' + sizzle);

    if (sizzle in wsdict) {
        wsdict[sizzle].ws.close();
        delete wsdict[sizzle];
    }
}

*/
