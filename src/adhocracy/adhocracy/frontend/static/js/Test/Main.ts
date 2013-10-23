declare var define;
declare var describe;
declare var it;
declare var before;
declare var beforeEach;

// import Util = require('../Adhocracy/Util');

define(['jquery',
        // 'obviel',
        // 'obvieltemplate',
        'chai',
        'mocha',
        'Adhocracy',
        'Adhocracy/Frames/ProposalWorkbench',
        'Adhocracy/Util',],
       function($,
                // obviel,
                // obvieltemplate,
                chai,
                mocha,
                Adhocracy,
                ProposalWorkbench,
                Util)
{
    mocha.setup('bdd');

    var expect = chai.expect;

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
//                     expect(directory_div.innerText).to.match(
//                         new RegEx('/' + name + '/'),
//                         "wef");
                    expect(Util.isInfixOf(name, directory_div.innerText)).to.equal(true, name);
                });
            });

        });

    });

    return {
        run: function() {
            mocha.run();
        }
    }
});
