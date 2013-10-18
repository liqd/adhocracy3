define(['jquery',
        // 'obviel',
        // 'obvieltemplate',
        'chai',
        'mocha',
        'Adhocracy',
        'Adhocracy/Frames/ProposalWorkbench'],
       function($,
                // obviel,
                // obvieltemplate,
                chai,
                mocha,
                Adhocracy,
                ProposalWorkbench)
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

        it('directory div must contain list of proposals as created by fixtures.js', function() {

            // FIXME: fixtures.js does not exist.  the following
            // should be slightly out of order, but the idea should be
            // valid.

            ProposalWorkbench.open_proposals('/adhocracy/');
            var expected_names = ['proposal DAG 1', 'proposal DAG 2'];

            var list_items = $('#proposal_workbench_directory')[0].getElementsByTagNames('li');
            list_items.forEach(function(li) {
                expect(li.innerText).to.equal(expected_names.shift());
            });
        });
    });

    return {
        run: function() {
            mocha.run();
        }
    }
});
