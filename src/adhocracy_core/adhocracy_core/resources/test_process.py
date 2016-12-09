from pyramid import testing
from pytest import mark
from pytest import fixture


class TestProcess:

    @fixture
    def meta(self):
        from .process import process_meta
        return process_meta

    def test_meta(self, meta):
        from .process import IProcess
        from .asset import add_assets_service
        from .badge import add_badges_service
        from adhocracy_core.interfaces import IPool
        from adhocracy_core import sheets
        assert meta.iresource is IProcess
        assert meta.is_sdi_addable
        assert IProcess.isOrExtends(IPool)
        assert meta.is_implicit_addable is False
        assert meta.permission_create == 'create_process'
        assert sheets.asset.IHasAssetPool in meta.basic_sheets
        assert sheets.badge.IHasBadgesPool in meta.basic_sheets
        assert sheets.description.IDescription in meta.basic_sheets
        assert sheets.embed.IEmbed in meta.basic_sheets
        assert sheets.workflow.IWorkflowAssignment in meta.basic_sheets
        assert sheets.notification.IFollowable in meta.basic_sheets
        assert sheets.anonymize.IAllowAddAnonymized in meta.basic_sheets
        assert add_assets_service in meta.after_creation
        assert add_badges_service in meta.after_creation
        assert meta.default_workflow == 'sample'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)


class TestEmbedCodeConfigAdapter:

    @mark.usefixtures('integration')
    def test_get_config_for_process(self, request_, registry,
                                    mocker):
        from .process import IProcess
        from adhocracy_core.sheets.embed import IEmbedCodeConfig
        context = testing.DummyResource(__provides__=IProcess)
        mocker.patch('adhocracy_core.resources.process.resource_path',
                     return_value='/process')
        result = registry.getMultiAdapter((context, request_),
                                          IEmbedCodeConfig)
        assert result == {'sdk_url': 'http://localhost:6551/AdhocracySDK.js',
                          'frontend_url': 'http://localhost:6551',
                          'path': 'http://example.com/',
                          'widget': 'plain',
                          'autoresize': 'false',
                          'locale': 'en',
                          'autourl': 'true',
                          'initial_url': '/r/process/',
                          'nocenter': 'true',
                          'noheader': 'false',
                          'style': 'height: 650px',
                          }
