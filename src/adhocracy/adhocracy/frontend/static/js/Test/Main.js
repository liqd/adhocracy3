define(['chai', 'mocha', 'Adhocracy', 'Adhocracy/Frames/ProposalWorkbench'], function(chai, mocha, Adhocracy, ProposalWorkbench) {

    mocha.setup('bdd');

    var expect = chai.expect;

    // console.log(expect(18).to.equal(18));
    // console.log(expect(18).to.equal(19));

    describe('something pure yet lame', function() {
        it('should half its input', function() {
            expect(ProposalWorkbench.something_pure(18)).to.equal(9);
        });
    });

    return {
        run: function() {
            mocha.run();
        }
    }
});
