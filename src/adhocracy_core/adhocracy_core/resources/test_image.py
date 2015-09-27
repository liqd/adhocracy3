from pytest import fixture
from pytest import mark


class TestImage:

    @fixture
    def meta(self):
        from .image import image_meta
        return image_meta

    def test_meta(self, meta):
        from . import image
        import adhocracy_core.sheets.image
        assert meta.iresource is image.IImage
        assert meta.is_implicit_addable is True
        assert meta.extended_sheets ==\
               (adhocracy_core.sheets.image.IImageMetadata,)

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
