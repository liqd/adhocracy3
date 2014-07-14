
Concept: Modelling a Simple Use-Case with The Supergraph
===========================================================

1 create participation process and content
    Superuser Father has an Instance Hive.
    He adds an a participation project "Homestuff" to discuss proposals.
    He creates an proposal "dishwash table" and allows other users to access the proposal.

2a user disagrees and comments - user statement about content
    A user Alice looks at an existing proposal. She states her
    disagreement with the proposal (using a "disagree" button).
    She justifies her disagreement with a short text.

2a user agrees
    User Carl looks at everything, and annotates the proposal with an
    agreement (using an "agree" button).

3 user seconds disagreement - user statement about statement
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
    (object : IProposal)

    @essence
    rationale : string


IAgreement(IAssessment, IAssessable):
    (uid : str)
    (object : IProposal)

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

IMyParticipationProcess(IPool):
    @not_essence
    assesments : IAssessmentPool
    @not_essence
    proposals : IProposalPool

IUserPool(IPool):
    (contents : set(IUser))

IInstance(IPool):
    @not_essence
    contents: set(IPool)
    @not_essence
    users : IUserPool
