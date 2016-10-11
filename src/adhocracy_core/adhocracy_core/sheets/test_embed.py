from pyramid import testing
from pytest import raises
from pytest import fixture
from pytest import mark


class TestEmbedCodeConfigAdapter:

    def call_fut(self, *args):
        from .embed import embed_code_config_adapter
        return embed_code_config_adapter(*args)

    def test_default_mapping(self, context, request_):
        result = self.call_fut(context, request_)
        assert result == {'sdk_url': 'http://localhost:6551/AdhocracySDK.js',
                          'frontend_url': 'http://localhost:6551',
                          'path': 'http://example.com/',
                          'widget': '',
                          'autoresize': 'false',
                          'locale': 'en',
                          'autourl': 'false',
                          'initial_url': '',
                          'nocenter': 'true',
                          'noheader': 'false',
                          'style': 'height: 650px',
                          }

    def test_set_sdk_and_frontend_url_based_on_frontend_url(self, context,
                                                            request_):
        request_.registry.settings['adhocracy.frontend_url'] = 'http://x.de'
        result = self.call_fut(context, request_)
        assert result['sdk_url'] == 'http://x.de/AdhocracySDK.js'
        assert result['frontend_url'] == 'http://x.de'

    def test_set_locale_based_on_default_locale(self, context, request_):
        request_.registry.settings['pyramid.default_locale_name'] = 'de'
        result = self.call_fut(context, request_)
        assert result['locale'] == 'de'

    @mark.usefixtures('integration')
    def test_register_adapter(self, registry):
        from pyramid.interfaces import IRequest
        from adhocracy_core.interfaces import IResource
        from .embed import embed_code_config_adapter
        from .embed import IEmbedCodeConfig
        adapter = registry.adapters.lookup((IResource, IRequest),
                                           IEmbedCodeConfig)
        assert adapter == embed_code_config_adapter


class TestDeferredEmbedCode:

    @fixture
    def mock_config_adapter(self, mocker):
        return mocker.patch('pyramid.registry.Registry.getMultiAdapter')

    def call_fut(self, *args):
        from .embed import deferred_default_embed_code
        return deferred_default_embed_code(*args)

    def test_render_embed_code_html_with_default_mapping(
            self, mock_config_adapter, config, node, kw):
        config.include('pyramid_mako')
        mock_config_adapter.return_value = {'path': 'http:localhost/1'}
        result = self.call_fut(node, kw)
        assert 'data-path="http:localhost/1"' in result


class TestEmbedSheet:

    @fixture
    def meta(self):
        from .embed import embed_meta
        return embed_meta

    def test_meta(self, meta):
        from . import embed
        assert meta.isheet == embed.IEmbed
        assert meta.schema_class == embed.EmbedSchema
        assert meta.creatable is True
        assert meta.editable is True
        assert meta.readable is True

    def test_create(self, meta, context):
        from .embed import deferred_default_embed_code
        from deform.widget import TextAreaWidget
        inst = meta.sheet_class(meta, context, None)
        assert inst
        assert inst.schema['embed_code'].default \
               == deferred_default_embed_code
        assert isinstance(inst.schema['embed_code'].widget, TextAreaWidget)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'embed_code': '',
                              'external_url': ''}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)
