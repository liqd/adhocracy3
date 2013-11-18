/// <reference path="../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/mocha/mocha.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/chai/chai.d.ts"/>

// for importing things in TypeScript, see
// http://www.codeproject.com/Articles/528295/ModularizationplusinplusTypeScript
//
// html5 global variables for elem ids are officially a really bad
// idea.  a good counter-example is mocha, which both defines a global
// variable 'mocha' and expects an html div with id 'mocha'.
// typescript helps with this.  :-)

// import ProposalWorkbench = require('Adhocracy/Frames/ProposalWorkbench');


// cascade of synchronous ajax calls that establish some fixtures.
// for the subsequent tests.  data model is outdated and doesn't fit
// /docs/source/rest_api.rst any more.  but this is anyway not the
// place to set up fixtures...
//
// FIXME: the two paragraphs of the proposal are stored as versions in
// the same container, so the proposal contains two versions of the
// same paragraph as different paragraphs.  (we should probably
// implement postroot logic on the backend first to make it easier to
// fix this.)
export function proposal_workbench_setup() {
    var root_url = "/adhocracy";

    var showjs = function(json) {
        return JSON.stringify(json, null, 2)
    };

    // delete entire server db.
    $.ajax(root_url + '/admin/reset-db', {type: "GET", async: false});

    var propcontainer = {
        'content_type': 'adhocracy.contents.interfaces.IProposalContainer',
        'data': { 'adhocracy.propertysheets.interfaces.IName': { 'name': 'NoMoreMosquitos' } }
    };
    var resp = $.ajax(root_url, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(propcontainer),
        async: false
    });

    var propcontainer_path = $.parseJSON(resp.responseText)['path'];

    var prop = {
        'content_type': 'adhocracy.contents.interfaces.IProposal',
        'data': { 'adhocracy.propertysheets.interfaces.IName': { 'name': 'v1' } }
    };
    resp = $.ajax(propcontainer_path, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(prop),
        async: false
    });

    var propv1 = $.parseJSON(resp.responseText);

    var parcontainer = {'content_type': 'adhocracy.contents.interfaces.IParagraphContainer',
                        'data': { 'adhocracy.propertysheets.interfaces.IName': { 'name': 'paragraphs' }}};
    resp = $.ajax(root_url, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(parcontainer),
        async: false
    });

    var parcontainer_path = $.parseJSON(resp.responseText)['path'];

    var par = {'content_type': 'adhocracy.contents.interfaces.IParagraph',
               'data': { 'adhocracy.propertysheets.interfaces.IParagraph': {
                   'text': 'sein bart ist vom vorüberziehn der stäbchen'
               }
                       }
              };
    resp = $.ajax(parcontainer_path, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(par),
        async: false
    });

    propv1['data']['adhocracy.propertysheets.interfaces.IDocument']['paragraphs'].push({
        'content_type': 'adhocracy.contents.interfaces.IParagraph',
        'path': $.parseJSON(resp.responseText)['path']
    });

    par['data']['adhocracy.propertysheets.interfaces.IParagraph']['text'] = 'ganz weiß geworden, so wie nicht mehr frisch';
    resp = $.ajax(parcontainer_path, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(par),
        async: false
    });
    propv1['data']['adhocracy.propertysheets.interfaces.IDocument']['paragraphs'].push({
        'content_type': 'adhocracy.contents.interfaces.IParagraph',
        'path': $.parseJSON(resp.responseText)['path']
    });

    propv1['data']['adhocracy.propertysheets.interfaces.IDocument']['title'] = 'Der Käptn';
    propv1['data']['adhocracy.propertysheets.interfaces.IDocument']['description'] = '(nicht von rainer maria rilke)';

    propv1['data']['adhocracy.propertysheets.interfaces.IVersions'] = undefined;
    // ['preds'].push({
    //    'content_type': 'adhocracy.contents.interfaces.IProposal',
    //    'path': propv1['path']
    //});
    propv1['path'] = undefined;

    resp = $.ajax(propcontainer_path, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(propv1),
        async: false
    });

    propcontainer['data']['adhocracy.propertysheets.interfaces.IName']['name'] = 'CDU für alle';
    $.ajax(root_url, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(propcontainer),
        async: false
    });
    propcontainer['data']['adhocracy.propertysheets.interfaces.IName']['name'] = 'Gentechnik jetzt';
    $.ajax(root_url, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(propcontainer),
        async: false
    });
    propcontainer['data']['adhocracy.propertysheets.interfaces.IName']['name'] = 'Mehr Proposals';
    $.ajax(root_url, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(propcontainer),
        async: false
    });

    $('body').append("<pre>done creating proposal examples.</pre>");
}



// FIXME: s/Adhocracy.Frames.*/Adhocracy.Pages.*/g;

// check out: https://github.com/metaskills/mocha-phantomjs
