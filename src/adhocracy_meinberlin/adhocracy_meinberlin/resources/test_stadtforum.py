from distutils import dir_util
import os
import transaction

from pytest import fixture
from pytest import mark

from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to

class TestProcess:

    @fixture
    def meta(self):
        from .stadtforum import process_meta
        return process_meta

    def test_meta(self, meta):
        from .stadtforum import IProcess
        assert meta.iresource is IProcess
        assert meta.workflow_name == 'standard'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


@mark.functional
class TestStadtForum:

    @fixture
    def process_url(self):
        return '/organisation/stadtforum'

    def test_create_resources(self,
                              registry,
                              datadir,
                              process_url,
                              app,
                              app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app, json_file)
        resp = app_admin.get(process_url)
        assert resp.status_code == 200


    def test_set_participate_phase(self, registry, app, process_url, app_admin):
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url,
                                'announce')
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url,
                                'participate')
        assert resp.status_code == 200
