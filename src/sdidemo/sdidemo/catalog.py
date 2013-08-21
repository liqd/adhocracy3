from substanced.catalog import Field, catalog_factory

@catalog_factory('sdidemo')
class Indexes(object):
    title = Field()
    created = Field()
    modified = Field()
    
class IndexViews:
    def __init__(self, resource):
        self.resource = resource

    def title(self, default):
        result = getattr(self.resource, 'title', default)
        if result is not default:
            result = unicode(result)
        return result

    def created(self, default):
        date = getattr(self.resource, '__created__', default)
        if date is not default:
            date = date.isoformat()
        return date

    def modified(self, default):
        date = getattr(self.resource, '__modified__', default)
        if date is not default:
            date = date.isoformat()
        return date
    
def includeme(config):
    config.add_indexview(
        IndexViews,
        catalog_name='sdidemo',
        index_name='title',
        attr='title'
        )
    config.add_indexview(
        IndexViews,
        catalog_name='sdidemo',
        index_name='created',
        attr='created'
        )
    config.add_indexview(
        IndexViews,
        catalog_name='sdidemo',
        index_name='modified',
        attr='modified'
        )
