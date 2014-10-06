from pyramid import testing

import unittest


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy_core.testing import create_pool_with_graph
        config = testing.setUp()
        config.include('adhocracy_core.registry')
        config.include('adhocracy_core.events')
        config.include('adhocracy_core.catalog')
        config.include('adhocracy_core.sheets')
        config.include('adhocracy_core.sheets.comment')
        config.include('adhocracy_core.resources.comment')
        self.config = config
        context = create_pool_with_graph()
        self.context = context

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        from adhocracy_core.resources.comment import ICommentVersion
        from adhocracy_core.resources.comment import IComment
        from adhocracy_core.resources.comment import ICommentsService
        content_types = self.config.registry.content.factory_types
        assert IComment.__identifier__ in content_types
        assert ICommentVersion.__identifier__ in content_types
        assert ICommentsService.__identifier__ in content_types

    def test_includeme_registry_create_commentversion(self):
        from adhocracy_core.resources.comment import ICommentVersion
        res = self.config.registry.content.create(ICommentVersion.__identifier__,
                                                  self.context)
        assert ICommentVersion.providedBy(res)

    def test_includeme_registry_create_commentsservice(self):
        from adhocracy_core.resources.comment import ICommentsService
        from substanced.util import find_service
        res = self.config.registry.content.create(ICommentsService.__identifier__,
                                                  self.context)
        assert ICommentsService.providedBy(res)
        assert find_service(self.context, 'comments')

    def test_add_commentsservice(self):
        from adhocracy_core.resources.comment import add_commentsservice
        add_commentsservice(self.context, self.config.registry, {})
        assert self.context['comments']
