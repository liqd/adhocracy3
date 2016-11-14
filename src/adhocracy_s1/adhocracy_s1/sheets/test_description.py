from unittest.mock import Mock
from pyramid import testing
from pytest import fixture

class TestDescriptionSheet:

    @fixture
    def meta(self):
        from .description import description_meta
        return description_meta

    def test_default(self, meta, context):
        from .description import deferred_default_short_description
        from .description import deferred_default_description
        inst = meta.sheet_class(meta, context, None)
        assert inst.schema['short_description'].default \
               == deferred_default_short_description
        assert inst.schema['description'].default \
               == deferred_default_description


class TestDeferredDefaultShortDescription:

    def call_fut(self, *args):
        from .description import deferred_default_short_description
        return deferred_default_short_description(*args)

    def test_deferred_default_non_s1_process(self, node, kw):
        kw['context'] = testing.DummyResource()
        result = self.call_fut(node, kw)
        assert result == ''

    def test_deferred_default_s1_process(self, node, kw):
        from adhocracy_s1.resources.s1 import IProcess
        from .description import DEFAULT_S1_SHORT_DESCRIPTION
        kw['context'] = testing.DummyResource(__provides__=IProcess)
        result = self.call_fut(node, kw)
        assert result == DEFAULT_S1_SHORT_DESCRIPTION

    def test_deferred_default_creating_non_s1_process(self, node, kw,
                                                      resource_meta):
        kw['context'] = testing.DummyResource()
        kw['creating'] = resource_meta
        result = self.call_fut(node, kw)
        assert result == ''

    def test_deferred_default_creating_s1_process(self, node, kw,
                                                  resource_meta):
        from adhocracy_s1.resources.s1 import IProcess
        from .description import DEFAULT_S1_SHORT_DESCRIPTION
        kw['context'] = testing.DummyResource()
        kw['creating'] = resource_meta._replace(iresource=IProcess)
        result = self.call_fut(node, kw)
        assert result == DEFAULT_S1_SHORT_DESCRIPTION


class TestDeferredDefaultDescription:

    def call_fut(self, *args):
        from .description import deferred_default_description
        return deferred_default_description(*args)

    def test_deferred_default_non_s1_process(self, node, kw):
        kw['context'] = testing.DummyResource()
        result = self.call_fut(node, kw)
        assert result == ''

    def test_deferred_default_s1_process(self, node, kw):
        from adhocracy_s1.resources.s1 import IProcess
        from .description import DEFAULT_S1_DESCRIPTION
        kw['context'] = testing.DummyResource(__provides__=IProcess)
        result = self.call_fut(node, kw)
        assert result == DEFAULT_S1_DESCRIPTION

    def test_deferred_default_creating_non_s1_process(self, node, kw,
                                                      resource_meta):
        kw['context'] = testing.DummyResource()
        kw['creating'] = resource_meta
        result = self.call_fut(node, kw)
        assert result == ''

    def test_deferred_default_creating_s1_process(self, node, kw,
                                                  resource_meta):
        from adhocracy_s1.resources.s1 import IProcess
        from .description import DEFAULT_S1_DESCRIPTION
        kw['context'] = testing.DummyResource()
        kw['creating'] = resource_meta._replace(iresource=IProcess)
        result = self.call_fut(node, kw)
        assert result == DEFAULT_S1_DESCRIPTION
