from pyramid import testing
from pytest import raises
from pytest import fixture
from pytest import mark


class TestEmbedCodeConfigBplanAdapter:

    @mark.usefixtures('integration')
    def test_get_config_for_bplan_process(self, request_, registry):
        from adhocracy_core.sheets.embed import IEmbedCodeConfig
        from adhocracy_meinberlin.resources.bplan import IProcess
        context = testing.DummyResource(__provides__=IProcess)
        result = registry.getMultiAdapter((context, request_),
                                          IEmbedCodeConfig)
        assert result == {'sdk_url': 'http://localhost:6551/AdhocracySDK.js',
                          'frontend_url': 'http://localhost:6551',
                          'path': 'http://example.com/',
                          'widget': 'mein-berlin-bplaene-proposal-embed',
                          'autoresize': 'false',
                          'locale': 'en',
                          'autourl': 'false',
                          'initial_url': '',
                          'nocenter': 'true',
                          'noheader': 'true',
                          'style': 'height: 650px',
                          }
