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

    taggedValue(
        "schema", "substanced.schema.Schema")  # suptype has to override
    taggedValue("permission_view", "view")  # subtype should override this
    taggedValue("permission_edit", "edit")  # subtype should override this


# Name Data


class NameSchema(Schema):

    name = NameSchemaNode(default="")


class NameReadonlySchema(Schema):

    name = NameSchemaNode(readonly=True, default="")


class IName(IPropertySheetMarker):

    taggedValue("schema", "adhocracy.properties.interfaces.NameSchema")


class INameReadonly(IName):

    taggedValue(
        "schema", "adhocracy.properties.interfaces.NameReadonlySchema")


# Pool data

class IPool(IPropertySheetMarker):

    taggedValue("schema", "adhocracy.properties.interfaces.PoolSchema")


class PoolSchema(Schema):
    elements = ReferenceSetSchemaNode(essence_refs=False,
                                      default=[],
                                      missing=[],
                                      interface=Interface
                                      )

# Versionable Data


class IVersionable(IPropertySheetMarker):

    """Marker interface representing a versionable Fubel."""

    taggedValue(
        "schema", "adhocracy.properties.interfaces.VersionableSchema")


# class IForkable(IVersionable):
#     """Marker interface representing a forkable node with version data"""

class VersionableSchema(Schema):

    follows = ReferenceSetSchemaNode(essence_refs=True,
                                     default=[],
                                     missing=[],
                                     interface=IVersionable,
                                     )
    followed_by = ReferenceSetSchemaNode(
        default=[],
        missing=[],
        interface=IVersionable,
        readonly=True,
    )


class IVersions(IPropertySheetMarker):

    """Dag for collecting all versions of one Fubel."""
    taggedValue("schema", "adhocracy.properties.interfaces.VersionsSchema")


class VersionsSchema(Schema):

    elements = ReferenceSetSchemaNode(essence_refs=False,
                                      default=[],
                                      missing=[],
                                      interface=IVersionable,
                                      )


class ITags(IPropertySheetMarker):

    """List for collecting all tags one Fubel."""
    taggedValue("schema", "adhocracy.properties.interfaces.TagsSchema")


class TagsSchema(Schema):

    elements = ReferenceSetSchemaNode(essence_refs=False,
                                      default=[],
                                      missing=[],
                                      interface=IVersionable,
                                      )


# Document Data


class IDocument(IPropertySheetMarker):

    """Marker interface representing a Fubel with document data """

    taggedValue("schema", "adhocracy.properties.interfaces.DocumentSchema")


class DocumentSchema(Schema):

    elements = ReferenceSetSchemaNode(essence_refs=True,
                                      default=[],
                                      missing=[],
                                      interface=
                                      "adhocracy.resources.interfaces.ISection")


class ISection(IPropertySheetMarker):

    """Marker interface representing a document section """

    taggedValue("schema", "adhocracy.properties.interfaces.SectionSchema")


class SectionSchema(Schema):
    title = colander.SchemaNode(colander.String(), default="")
    elements = ReferenceSetSchemaNode(essence_refs=True,
                                      default=[],
                                      missing=[],
                                      interface=
                                      "adhocracy.resources.interfaces.ISection")
