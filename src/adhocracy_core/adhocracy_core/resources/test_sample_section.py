from pyramid import testing
from pytest import fixture
from pytest import mark


def test_sectionversion_meta():
    from .sample_section import sectionversion_meta
    from .sample_section import ISectionVersion
    meta = sectionversion_meta
    assert meta.iresource is ISectionVersion
    assert meta.permission_create == 'edit_section'


def test_section_meta():
    from .sample_section import section_meta
    from .sample_section import ISectionVersion
    from .sample_section import ISection
    from .tag import ITag
    meta = section_meta
    assert meta.iresource is ISection
    assert meta.element_types == [ITag, ISectionVersion]
    assert meta.item_type == ISectionVersion
    assert meta.permission_create == 'create_section'


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.sample_section')
    config.include('adhocracy_core.resources.tag')


@mark.usefixtures('integration')
class TestSection:

    @fixture
    def context(self, pool):
        return pool

    def test_create_section(self, context, registry):
        from adhocracy_core.resources.sample_section import ISection
        from adhocracy_core.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': 'name1'}}
        res = registry.content.create(ISection.__identifier__,
                                      appstructs=appstructs,
                                      parent=context)
        assert ISection.providedBy(res)

    def test_create_sectionversion(self, context, registry):
        from adhocracy_core.resources.sample_section import ISectionVersion
        res = registry.content.create(ISectionVersion.__identifier__,
                                      parent=context)
        assert ISectionVersion.providedBy(res)
