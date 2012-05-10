import unittest

from pyramid import testing
from pyramid.tests.test_traversal import (
     ResourceTreeTraverserTests,
     DummyRequest,
)


class DummyContextWithoutGetitem(object):
    __parent__ = None

    def __init__(self, next=None, name=None):
        self.next = next
        self.__name__ = name

    def __repr__(self):
        return '<DummyContext with name %s at id %s>' %\
                (self.__name__, id(self))


class ResourceTreeTraverserAdoptedTests(ResourceTreeTraverserTests):

    def _getTargetClass(self):
        from pyramid_adoptedtraversal.resourcetreetraverseradopted \
                import ResourceTreeTraverserAdopted
        return ResourceTreeTraverserAdopted

    def test_call_without_getitem(self):
        foo = DummyContextWithoutGetitem(None, 'test')
        root = DummyContextWithoutGetitem(foo, 'root')
        policy = self._makeOne(root)
        path_info = b'/Qu\xc3\xa9bec'
        environ = self._getEnviron(PATH_INFO=path_info)
        request = DummyRequest(environ)
        result = policy(request)
        self.assertNotEqual(result['context'], foo)


class AdapterTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTargetClass(self):
        from pyramid_adoptedtraversal.resourcetreetraverseradopted \
                import ResourceTreeTraverserAdopted
        return ResourceTreeTraverserAdopted

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def _getEnviron(self, **kw):
        environ = {}
        environ.update(kw)
        return environ

    def test_call_without_getitem_but_adapter(self):
        from pyramid_adoptedtraversal.interfaces import IChildsDictLike
        from pyramid_adoptedtraversal.adapters \
                import ExampleChildsDictLikeAdapter
        from zope.interface import Interface
        from pyramid.threadlocal import get_current_registry
        registry = get_current_registry()
        registry.registerAdapter(ExampleChildsDictLikeAdapter,\
                (Interface,), IChildsDictLike)

        foo = DummyContextWithoutGetitem(None, 'test')
        root = DummyContextWithoutGetitem(foo, 'root')
        policy = self._makeOne(root)
        path_info = b'/Qu\xc3\xa9bec'
        environ = self._getEnviron(PATH_INFO=path_info)
        request = DummyRequest(environ)
        result = policy(request)
        self.assertEqual(result['context'], foo)
