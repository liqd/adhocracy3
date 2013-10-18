define(['jquery', 'chai', 'mocha', 'Adhocracy', 'Adhocracy/Frames/ProposalWorkbench'], function($, chai, mocha, Adhocracy, ProposalWorkbench) {

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

        it('detail div must contain "..."', function() {
            expect($('#proposal_workbench_detail')[0].innerText).to.equal('...');
        });
    });

    return {
        run: function() {
            mocha.run();
        }
    }
});
