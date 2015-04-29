from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.image')


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


@mark.usefixtures('integration')
def test_includeme_register__image_sheet(registry):
    from adhocracy_core.sheets.image import IImageMetadata
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IImageMetadata)
    inst = get_sheet(context, IImageMetadata, registry=registry)
    assert inst.meta.isheet is IImageMetadata


class TestImageReference:

    @fixture
    def meta(self):
        from .image import image_reference_meta
        return image_reference_meta

    def test_meta(self, meta):
      from .image import IImageReference
      from .image import ImageReferenceSchema
      from adhocracy_core.sheets import AnnotationStorageSheet
      assert meta.sheet_class == AnnotationStorageSheet
      assert meta.isheet == IImageReference
      assert meta.schema_class == ImageReferenceSchema
      assert meta.editable is True

    def test_create(self, meta, context):
        assert meta.sheet_class(meta, context)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'picture': None}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, registry):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet, registry=registry)


