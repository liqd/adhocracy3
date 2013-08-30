from substanced.content import ContentRegistry



class AdhocracyContentRegistry(ContentRegistry):

    def metadata(self, resource, name, default=None):
        """
        Return a metadata value for the content type of ``resource`` based on
        the ``**meta`` value passed to
        :meth:`~substanced.content.ContentRegistry.add`.

        Subtyped to allow local overrides:

            A ressource attribute with the same name as the metadata key
            overrides the metadata value.
        """
        value = super(AdhocracyContentRegistry, self).metadata(resource, name,
                                                               default)
        local_value = getattr(resource, name, None)
        if local_value:
            value = local_value
        return value


def includeme(config): # pragma: no cover
    # subtype content registry object
    content_old = config.registry.content
    content_new = AdhocracyContentRegistry(config.registry)
    content_new.__dict__.update(content_old.__dict__)
    config.registry.content = content_new

