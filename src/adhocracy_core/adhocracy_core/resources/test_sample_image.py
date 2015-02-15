from pytest import fixture
from pytest import mark


def test_sample_image_meta():
    from .sample_image import sample_image_meta
    from .sample_image import ISampleImage
    from adhocracy_core.sheets.asset import IAssetData
    from adhocracy_core.sheets.metadata import IMetadata
    from adhocracy_core.sheets.sample_image import ISampleImageMetadata
    meta = sample_image_meta
    assert meta.iresource is ISampleImage
    assert meta.is_implicit_addable is True
    assert set(meta.basic_sheets) == {IAssetData, IMetadata,
                                      ISampleImageMetadata}


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.sample_image')


@mark.usefixtures('integration')
class TestSampleImage:

    @fixture
    def context(self, pool):
        return pool

    def test_create_sample_image(self, context, registry):
        from adhocracy_core.resources.sample_image import ISampleImage
        appstructs = {}
        res = registry.content.create(ISampleImage.__identifier__,
                                      appstructs=appstructs,
                                      parent=context)
        assert ISampleImage.providedBy(res)
