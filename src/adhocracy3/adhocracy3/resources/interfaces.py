import colander
from substanced.schema import (
    Schema,
    NameSchemaNode
    )
from substanced.interfaces import (
    IFolder,
    IAutoNamingFolder
)
from substanced.util import renamer
from substanced.objectmap import reference_targetid_property
from zope.interface import (
    Interface,
    Attribute,
   taggedValue,
)

from adhocracy3.schema import ReferenceSetSchemaNode

# Interface types

class IMarkerInterface(Interface):
    """Marker interface to represent a special type of object.
       It does not expose any attribute or method.
    """


class IPropertySheetMarkerInterface(Interface):
    """Marker interface with tagged value "schema" to
       reference a colander shema class to set/get data
    """

    taggedValue("schema", "substanced.schema.Schema")


# TODO: remove Mixin classes and attribute storage, use adapter and annotation
# storage instead?

# Base Pool


class IPool(IFolder):
    """Container to define a namespace for supergraph Nodes
       and to provide services like catalog, workflow registry, ..
    """

# Base Node
# TODO don't use IFolder all the time, this is bloat

class INodeContainer(IFolder):
    """Container for all versions and tags of one Node
       or other node containers that are part of the essence.
    """

    content_type = Attribute('Addable node contenttype, '
                             'has to implement INode and IVersionable')
    versions = Attribute('INodeVersions object')
    tags = Attribute('INodeTags object')


class INodeVersions(IAutoNamingFolder):
    """Container to store all node versions
    """

class INodeTags(IFolder):
    """Container to store tag nodes to reference specific node versions
    """

class INode(IFolder):
    """Marker interface representing a supergraph node"""

# Name Data

class NameSchema(Schema):

    name = NameSchemaNode()


class IName(IPropertySheetMarkerInterface):

    taggedValue("schema", "adhocracy3.resources.interfaces.NameSchema")


# Versionable Data

class IVersionable(IPropertySheetMarkerInterface):
    """Marker interface representing a node with version data"""

    taggedValue("schema", "adhocracy3.resources.interfaces.VersionableSchema")

class IForkable(IVersionable):
    """Marker interface representing a forkable node with version data"""


class VersionableSchema(Schema):

    follows = ReferenceSetSchemaNode(essence_refs=True,
                                     default=[],
                                     missing=[],
                                     interface=IVersionable,
                                     )

# Text Data

class IText(IPropertySheetMarkerInterface):
    """Marker interfaces representing a node with text data """

    taggedValue("schema", "adhocracy3.resources.interfaces.TextSchema")


class TextSchema(Schema):

    title =  colander.SchemaNode(colander.String())

    content =  colander.SchemaNode(colander.String())


# Concrete Nodes

class IProposalContainer(INodeContainer):
    """Proposal container"""


class IProposal(INode):
    """Proposal node"""


# copy paste garbage:

#class IVersionableForking(IVersionable):
    #"""Marker interface representing a forkable node"""

#class IAssessmentPool(INodePool):
    #"""Marker interface representing a container to add assessments"""

    ##taggedValue("addable", [IAssessment])

#IMyParticipationProcess(IPool):
    #@not_essence
    #assesments : IAssessmentPool
    #@not_essence
    #proposals : IProposalPool

#IInstance(IPool):
    #@not_essence
    #contents: set(IPool)
    #@not_essence
    #users : IUserPool
 #IAssessment(INode):

    #@essence
    #uid : string

    #@essence
    #object : INode


#IAssessable(INode):

    #@not_essence
    #assessments : [IAssessment]


#concrete interfaces
#-------------------

#IUser(INode):

    #name : str

    #uid : str

    #@not_essence
    #user_assessments : [IAssessment]


#IProposal(INode, IAssessable):

    #@essence
    #title : str

    #@essence
    #content : string


#IDisagreement(IAssessment, IAssessable):
    #(uid : str)
    #(object : IProposal)

    #@essence
    #rationale : string


#IAgreement(IAssessment, IAssessable):
    #(uid : str)
    #(object : IProposal)

    #@essence
    #rationale : string


#ISeconds(IAssessment):
    #(uid : string)
    #(object : IAssessment)
