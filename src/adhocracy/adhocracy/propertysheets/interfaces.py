import colander
from substanced.schema import (
    Schema,
    NameSchemaNode
    )
from zope.interface import (
    Interface,
    taggedValue,
    )

from adhocracy.schema import ReferenceSetSchemaNode


# Interface types


class IPropertySheetMarker(Interface):
    """Marker interface with tagged value "schema" to
       reference a colander schema class.

       The colander schema should define the facade to work with
       IContent objects.

       To set/get the data you can adapt to IPropertySheet objects.

       A tagged value "view_permission" set the permission
       to create this content object and add it to the object hierarchy.
    """

    taggedValue("schema", "substanced.schema.Schema")

    taggedValue("view_permission", "view")
    taggedValue("edit_permission", "edit-content")


# Name Data


class NameSchema(Schema):

    name = NameSchemaNode(default="")


class NameReadonlySchema(Schema):

    name = NameSchemaNode(readonly=True, default="")


class IName(IPropertySheetMarker):

    taggedValue("schema", "adhocracy.propertysheets.interfaces.NameSchema")
    taggedValue("view_permission", "view")
    taggedValue("edit_permission", "edit-content")

# TODO this should be a specialication of IName..
class INameReadonly(IPropertySheetMarker):

    taggedValue("schema", "adhocracy.propertysheets.interfaces.NameReadonlySchema")
    taggedValue("view_permission", "view")
    taggedValue("edit_permission", "edit-content")


# Versionable Data

class IVersionable(IPropertySheetMarker):
    """Marker interface representing a node with version data"""

    taggedValue("schema", "adhocracy.propertysheets.interfaces.VersionableSchema")
    taggedValue("view_permission", "view")
    taggedValue("edit_permission", "edit-content")


class IForkable(IVersionable):
    """Marker interface representing a forkable node with version data"""


class VersionableSchema(Schema):

    follows = ReferenceSetSchemaNode(essence_refs=True,
                                     default=[],
                                     missing=[],
                                     interface=IVersionable,
                                     )
    #followed_by = ReferenceSetSchemaNode(
                                     #default=[],
                                     #missing=[],
                                     #interface=IVersionable,
                                     #readonly=True,
                                     #)

# Document Data


class IDocument(IPropertySheetMarker):
    """Marker interfaces representing a node with document data """

    taggedValue("schema", "adhocracy.propertysheets.interfaces.DocumentSchema")
    taggedValue("view_permission", "view")
    taggedValue("edit_permission", "edit-content")


class DocumentSchema(Schema):

    title = colander.SchemaNode(colander.String(), default="")

    description = colander.SchemaNode(colander.String(), default="")

    paragraphs = ReferenceSetSchemaNode(essence_refs=True,
                                        default=[],
                                        missing=[],
                                        interface="adhocracy.contents.interfaces.IParagraph")

# Text Data


class IText(IPropertySheetMarker):
    """Marker for nodes that contain text."""

    taggedValue("schema", "adhocracy.propertysheets.interfaces.TextSchema")
    taggedValue("view_permission", "view")
    taggedValue("edit_permission", "edit-content")


class TextSchema(Schema):

    text = colander.SchemaNode(colander.String(), default="")
