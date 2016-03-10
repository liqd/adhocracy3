from distutils import dir_util
import os
import transaction

from pytest import fixture
from pytest import mark
from webtest import TestResponse

from adhocracy_core.testing import add_resources
from adhocracy_core.testing import do_transition_to

class TestProcess:

    @fixture
    def meta(self):
        from .stadtforum import process_meta
        return process_meta

    def test_meta(self, meta):
        from .stadtforum import IProcess
        assert meta.iresource is IProcess
        assert meta.workflow_name == 'stadtforum'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestPoll:

    @fixture
    def meta(self):
        from .stadtforum import poll_meta
        return poll_meta

    def test_meta(self, meta):
        from .stadtforum import IPoll
        assert meta.iresource is IPoll
        assert meta.workflow_name == 'stadtforum_poll'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
