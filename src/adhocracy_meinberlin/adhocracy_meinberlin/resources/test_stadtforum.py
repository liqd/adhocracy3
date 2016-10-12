from pyramid import testing
from pytest import fixture
from pytest import mark

class TestProcess:

    @fixture
    def meta(self):
        from .stadtforum import process_meta
        return process_meta

    def test_meta(self, meta):
        from .stadtforum import IProcess
        assert meta.iresource is IProcess
        assert meta.default_workflow == 'stadtforum'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestPoll:

    @fixture
    def meta(self):
        from .stadtforum import poll_meta
        return poll_meta

    def test_meta(self, meta):
        from adhocracy_core import sheets
        from .stadtforum import IPoll
        assert meta.iresource is IPoll
        assert meta.default_workflow == 'stadtforum_poll'
        assert sheets.embed.IEmbed in meta.extended_sheets

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestEmbedCodeConfigAdapter:

    @mark.usefixtures('integration')
    def test_get_config_for_stadtforum_poll(self, request_, registry):
        from adhocracy_core.sheets.embed import IEmbedCodeConfig
        from adhocracy_meinberlin.resources.stadtforum import IPoll
        context = testing.DummyResource(__provides__=IPoll)
        result = registry.getMultiAdapter((context, request_),
                                          IEmbedCodeConfig)
        assert result == {'sdk_url': 'http://localhost:6551/AdhocracySDK.js',
                          'frontend_url': 'http://localhost:6551',
                          'path': 'http://example.com/VERSION_0000000/',
                          'widget': 'meinberlin-stadtforum-proposal-detail',
                          'autoresize': 'false',
                          'locale': 'en',
                          'initial_url': '',
                          'autourl': 'false',
                          'nocenter': 'true',
                          'noheader': 'true',
                          'style': 'height: 650px',
                          }
