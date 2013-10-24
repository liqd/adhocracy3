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
            ProposalWorkbench.open_proposals('/adhocracy/', function() {
                expected_names = ['proposal DAG 1', 'proposal DAG 2'];
                directory_div = $.makeArray($('#proposal_workbench_directory'))[0]
                done();
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
