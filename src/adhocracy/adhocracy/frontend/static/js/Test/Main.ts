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

var chai = require('chai');
var expect = chai.expect;

import ProposalWorkbench = require('Adhocracy/Frames/ProposalWorkbench');


mocha.setup({ui: 'bdd', slow: 30, timeout: 2000});

// url must yield a content-type that implements property sheet
// interface IPool, and all elements of IPool must implement property
// sheet interface IName.
//
// FIXME: find haddock for js
//
// FIXME: fix type signature for continuation
function ajax_pool_names(url: string, done_pool_names?: any) {
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
                    directory_div = $.makeArray($('#proposal_workbench_directory'))[0]
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

        it('list_items should contain the right proposal names.', function() {
            expected_names.forEach(function (name) {
                expect(directory_div.innerText).to.match(new RegExp(name));
            });
        });
    });
});

export function run_tests() {
    mocha.run(function() {});
};
