require(['chai'], function(chai) {

    var expect = chai.expect;

    debugger;

    // console.log(expect(18).to.equal(18));
    // console.log(expect(18).to.equal(19));

    describe('something pure yet lame', function() {
        // throw 'reached...';
        it('should half its input', function() {
            throw 'not reached!';
            expect(18).to.equal(19);
        });
    });

/*
    require(['Adhocracy', 'Adhocracy/Frames/ProposalWorkbench'], function(Adhocracy, ProposalWorkbench) {
        describe('something pure yet lame', function() {
            it('should half its input', function() {
                expect(ProposalWorkbench.something_pure(18)).to.equal(19);
            });
        });
    });
*/

});
