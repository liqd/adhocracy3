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
//
// FIXME: This is missing in mocha's d.ts, isn't it?
var mocha : Mocha = require('mocha');

var expect : chai.ExpectStatic = (function() {
    var chai = require('chai');
    return chai.expect;
})();

import ProposalWorkbench = require('Adhocracy/Frames/ProposalWorkbench');


// cascade of synchronous ajax calls that establish some fixtures.
// for the subsequent tests.  data model is outdated and doesn't fit
// /docs/source/rest_api.rst any more.  but this is anyway not the
// place to set up fixtures...
function very_adhoc_fixtures_script() {
    var root_url = "/adhocracy";

    var showjs = function(json) {
        return JSON.stringify(json, null, 2)
    };

    $.ajax(root_url + '/0/0', {type: "GET"}).fail(function() {
        // run this in case the above GET yields nothing.  (otherwise, assume fixtures are already created.)

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

        propv1['data']['adhocracy.propertysheets.interfaces.IVersions']['preds'].push({
            'content_type': 'adhocracy.contents.interfaces.IProposal',
            'path': propv1['path']
        });

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
    });
}


mocha.setup({ui: 'bdd', slow: 30, timeout: 2000});

// url must yield a content-type that implements property sheet
// interface IPool, and all elements of IPool must implement property
// sheet interface IName.
//
// FIXME: find haddock for js
//
// FIXME: fix type signature for continuation
function ajax_pool_names(url: string, done_pool_names?: (pool: string[]) => any) {
    var get_args = {
        type: "GET",
        dataType: "json",
        contentType: "application/json",
    };

    function ajax_fail(jqxhr, textstatus, errorthrown) {
        function showjs(json) {
            return JSON.stringify(json, null, 2)
        };

        console.log(name + ": [" + showjs(jqxhr) + "][" + textstatus + "][" +
                    errorthrown + "]");

        throw "ajax error";
    };

    $.ajax(url, get_args).fail(ajax_fail).done(function(pool) {
        var refs = pool['data']['adhocracy.propertysheets.interfaces.IPool']['elements'];
        if (!refs.length)
            done_pool_names([]);  // the rest of this block only works on non-empty element lists!

        var elems = refs.map(function(ref) { return $.ajax(ref['path'], get_args); });

        // (Q is a library for promises that might be useful here.  We
        // are trying to do it by hand first.)

        var results = [];
        var counter = 0;

        function check_done() {
            counter += 1;
            if (counter >= elems.length) {
                done_pool_names(results.map(function(elem) {
                    return elem['data']['adhocracy.propertysheets.interfaces.IName']['name'];
                }));
            }
        };

        for (var i in elems) {
            elems[i].done((function(i) {
                return function(result) {
                    results[i] = result;
                    check_done();
                }})(i));
        };

        /* there may be a weirder solution along the lines of this:

        elems.reduce(function(newelem, done??) {
            newelem.done()...
        }, ??)(done_pool_names);

        */

        // FIXME: factor this out into a utils module export.

    })
}

describe('some trivial DOM invariants', function() {
    describe('directory div must contain list of proposals', function() {

        var expected_names;
        var directory_div;

        before(function(done) {
            ajax_pool_names('/adhocracy/', function(names) {
                expected_names = names;

                ProposalWorkbench.open_proposals('/adhocracy/', function() {
                    directory_div = $.makeArray($('#proposal_workbench_directory'))[0];
                    done();
                });
            });
        });

        it('must have three divs named appropriately', function() {
            expect($('#___probably_not_a_valid_dom_elem_id___')).to.have.length(0);
            expect($('#proposal_workbench_detail')).to.not.have.length(0);
            expect($('#proposal_workbench_directory')).to.not.have.length(0);
            expect($('#proposal_workbench_discussion')).to.not.have.length(0);
        });

        it('list_items must contain the right proposal names.', function() {
            expected_names.forEach(function (name) {
                expect(directory_div.innerText).to.match(new RegExp(name));
            });
        });
    });
});

// collect all links from a dom subtree, select one at random, and
// trigger a click event on that link.
function click_any(dom, done_click) {
    var links = dom.find('a').toArray();

    if (links.length > 0) {
        // var ix : number = Math.round(Math.random() * (links.length - 1));
        var ix : number = 0;
        var link = dom.find('a:eq(' + ix.toString() + ')');
        link.trigger(new $.Event('click', {pageX: this.x, pageY: this.y}), done_click);  // link actually *does* have a trigger method!
        // click_element(link[0], done_click);
        done_click(true);  // ...  but at this point, it is too early to call done_click.
    } else {
        done_click(false);
    }
}

function click_element(el, done_click) {
    var ev : any = document.createEvent("MouseEvent");
    ev.initMouseEvent("click");
    el.addEventListener("click", done_click);
    el.dispatchEvent(ev);
}

describe ('opening proposals', function() {

    it('must open proposal in the left div on click (any version), if proposal list is non-empty', function(done_it) {
        click_any($('#proposal_workbench_directory'), function(data_available) {
            expect(data_available).to.be.true;  // (this does not produce a very helpful error message.  blargh.)

            // for a start, just expect a <pre> element to pop up in the
            // detail div with the raw json object of the proposal.

            expect($('#proposal_workbench_detail pre')).to.have.length(1);
            done_it();
        });
    });

    it('must always open head, not just any version');

});

export function run_tests() {
    very_adhoc_fixtures_script();
    mocha.run(function() {});
};



// FIXME: s/Adhocracy.Frames.*/Adhocracy.Pages.*/g;

// check out: https://github.com/metaskills/mocha-phantomjs
