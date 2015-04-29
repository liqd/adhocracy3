from pyramid import testing
from pytest import fixture


class TestImageMetadataSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.image import image_metadata_meta
        return image_metadata_meta

    def test_create(self, meta):
        from adhocracy_core.sheets.image import IImageMetadata
        from adhocracy_core.sheets.image import image_mime_type_validator
        assert meta.isheet is IImageMetadata
        assert meta.mime_type_validator is image_mime_type_validator
        assert 'detail' in meta.image_sizes

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'attached_to': [],
                              'filename': '',
                              'mime_type': '',
                              'size': 0}


def test_image_mime_type_validator():
    from adhocracy_core.sheets.image import image_mime_type_validator
    assert image_mime_type_validator('image/jpeg') is True
    assert image_mime_type_validator('image/png') is True
    assert image_mime_type_validator('image/blah') is False
    assert image_mime_type_validator('') is False
    assert image_mime_type_validator(None) is False


def test_includeme_register__image_sheet(config):
    from adhocracy_core.sheets.image import IImageMetadata
    from adhocracy_core.utils import get_sheet
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.image')
    context = testing.DummyResource(__provides__=IImageMetadata)
    inst = get_sheet(context, IImageMetadata)
    assert inst.meta.isheet is IImageMetadata
