from zope.dottedname.resolve import resolve

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

    def addable_content_types(self, resource):
        """
        Returns a list with addable adhocracy content types.
        The list is generated base on the "addable_content_interfaces"
        metadata and interface heritage.

        Resources with adhocracy content interface return [].
        """
        content_type = self.typeof(resource)
        meta = self.meta.get(content_type, {})
        # TODO evil hack
        addables =[resolve(x) for x in meta.get("addable_content_interfaces",
                                                 [])]
        maybe_addables = [resolve(x) for x in self.all() if "adhocracy3" in x ]
        all_addables = []
        for maybe in maybe_addables:
            for addable in addables:
                addit = False
                if maybe is addable:
                    addit = True
                implicit = self.meta[maybe.__identifier__].get(
                    "is_implicit_addable", False)
                if implicit and issubclass(maybe, addable):
                    addit = True
                addit and all_addables.append(maybe.__identifier__)
        return all_addables


def includeme(config): # pragma: no cover
    # subtype content registry object
    content_old = config.registry.content
    content_new = AdhocracyContentRegistry(config.registry)
    content_new.__dict__.update(content_old.__dict__)
    config.registry.content = content_new

