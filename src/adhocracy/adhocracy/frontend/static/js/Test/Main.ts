/// <reference path="../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/mocha/mocha.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/chai/chai.d.ts"/>

// for importing things in TypeScript, see
// http://www.codeproject.com/Articles/528295/ModularizationplusinplusTypeScript

// This is missing in mocha's d.ts, isn't it?
declare var mocha : Mocha; // Should not be called 'mocha', since that clashes
                           // with the (required) 'mocha'-div, but I didn't get
                           // that to work.
mocha = require('mocha');

chai = require('chai');
var expect = chai.expect;

import Adhocracy = require('Adhocracy');
import ProposalWorkbench = require('Adhocracy/Frames/ProposalWorkbench');
import Util = require('Adhocracy/Util');


mocha.setup({ui: 'bdd', slow: 30, timeout: 2000});

describe('something pure yet lame', function() {
    it('should half its input', function() {
        expect(ProposalWorkbench.something_pure(18)).to.equal(9);
    });
});

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
    it('must have three divs named appropriately', function() {
        expect($('#___probably_not_a_valid_dom_elem_id___')).to.have.length(0);
        expect($('#proposal_workbench_detail')).to.not.have.length(0);
        expect($('#proposal_workbench_directory')).to.not.have.length(0);
        expect($('#proposal_workbench_discussion')).to.not.have.length(0);
    });

    it('detail div must contain "..." after Adhocracy.init()', function() {
        Adhocracy.init();
        expect($('#proposal_workbench_detail')[0].innerText).to.equal('...');
    });

    describe('directory div must contain list of proposals as created by fixtures.js', function() {

        // FIXME: fixtures.js does not exist.  the following
        // should be slightly out of order, but the idea should be
        // valid.

        var expected_names;
        var directory_div;

        beforeEach(function(done) {
            ajax_pool_names('/adhocracy/', function(names) {
                expected_names = names;

                ProposalWorkbench.open_proposals('/adhocracy/', function() {
                    directory_div = $.makeArray($('#proposal_workbench_directory'))[0]
                    done();
                });
            });
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
