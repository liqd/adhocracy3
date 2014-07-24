import unittest
from unittest.mock import patch

import colander
from pyramid import testing

from adhocracy.utils import get_sheet


@patch('adhocracy.sheets.GenericResourceSheet')
def _create_dummy_sheet_adapter(registry, isheet, dummy_sheet=None):
    from adhocracy.interfaces import IResourceSheet
    sheet = dummy_sheet.return_value
    registry.registerAdapter(lambda x: sheet,
                             required=(isheet,),
                             provided=IResourceSheet,
                             name=isheet.__identifier__)
    return sheet


class ResourceModifiedMetadataSubscriberUnitTest(unittest.TestCase):

    def _call_fut(self, event):
        from adhocracy.sheets.metadata import resource_modified_metadata_subscriber
        return resource_modified_metadata_subscriber(event)

    def setUp(self):
        from adhocracy.sheets.metadata import IMetadata
        config = testing.setUp()
        self.registry = config.registry
        self.registry = config.registry
        self.sheet = _create_dummy_sheet_adapter(self.registry, IMetadata)
        self.context = testing.DummyResource(__provides__=IMetadata)

    def tearDown(self):
        testing.tearDown()

    def test_with_metadata_isheet(self):
        from datetime import datetime
        event = testing.DummyResource(object=self.context)

        self._call_fut(event)

        today = datetime.now().date()
        set_modification_date = self.sheet.set.call_args[0][0]['modification_date']
        assert set_modification_date.date() == today


class IMetadataSchemaUnitTest(unittest.TestCase):

    def _make_one(self, **kwargs):
        from adhocracy.sheets.metadata import MetadataSchema
        return MetadataSchema(**kwargs)

    def test_deserialize_empty(self):
        inst = self._make_one()
        result = inst.deserialize({})
        assert result == {}

    def test_serialize_empty(self):
        inst = self._make_one()
        result = inst.serialize({})
        assert result['creation_date'] == colander.null
        assert result['modification_date'] == colander.null
        assert isinstance(result['creator'], list)

    def test_serialize_empty_and_bind(self):
        from datetime import datetime
        inst = self._make_one().bind()
        result = inst.serialize({})
        this_year = str(datetime.now().year)
        assert this_year in result['creation_date']
        assert this_year in result['modification_date']


class MetadataSheetIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.events')
        self.config.include('adhocracy.sheets.metadata')

    def tearDown(self):
        testing.tearDown()

    def test_includeme_add_metadata_sheet_to_registry(self):
        from adhocracy.sheets.metadata import IMetadata
        from adhocracy.sheets.metadata import MetadataSchema
        context = testing.DummyResource(__provides__=IMetadata)
        inst = get_sheet(context, IMetadata)
        assert inst.meta.isheet is IMetadata
        assert inst.meta.editable is False
        assert inst.meta.creatable is False
        assert inst.meta.readable
        assert inst.meta.schema_class is MetadataSchema

    def test_register_metadate_update_subscriber(self):
        handlers = [x.handler.__name__ for x
                    in self.config.registry.registeredHandlers()]
        assert 'resource_modified_metadata_subscriber' in handlers
