
Example of Modelling a Simple Use-Case Using our Supergraph
===========================================================


A user Alice looks at an existing proposal. She states her
disagreement with the proposal (using a "disagree" button).
She justifies her disagreement with a short text.

User Bob looks at the proposal, sees Alice's reaction and
states that he seconds both her disagreement and the 
justifying text.


interfaces that are inherited from
----------------------------------


INode:
    deps() : { <node> : { <interface> : [ <attr> ] } }
    refs() : { <attr> : <node> }


IAssessment(INode):

    @essence
    uid : string

    @essence
    object : INode


IAssessable(INode):

    @not_essence
    assessments : [IAssessment]


concrete interfaces
-------------------

IUser(INode):

    name : str

    uid : str

    @not_essence
    user_assessments : [IAssessment]


IProposal(INode, IAssessable):

    @essence
    title : str

    @essence
    content : string


IDisagreement(IAssessment, IAssessable):
    (uid : str)
    (object : IProposal | IAssessment)

    @essence
    rationale : string


IAgreement(IAssessment, IAssessable):
    (uid : str)
    (object : IProposal | IAssessment)

    @essence
    rationale : string


ISeconds(IAssessment):
    (uid : string)
    (object : IAssessment)


where to put everything
-----------------------

IPool(INode):
    @not_essence
    contents : set(INode)

IProposalPool(IPool):
    (contents : set(IProposal))

IAssessmentPool(IPool):
    (contents : set(IAssessment))

IUserPool(IPool):
    (contents : set(IUser))

IMyInstance(INode):
    @not_essence
    users : IUserPool
    @not_essence
    assesments : IAssessmentPool
    @not_essence
    proposals : IProposalPool
