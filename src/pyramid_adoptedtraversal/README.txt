pyramid_adoptedtraversal 
========================

Alternative implementation of pyramid.interfaces.ITraverser that uses an adpater
that implements IChildsDictLike to call the __getitem__ method. 
That means your ressource does not have to override the __getitem__ method
to allow traversal.

Usage:
------

Setup:

    >>> from pyramid import testing
    >>> ignore = testing.setUp()

Register your own IChildsDictLike adapter::

    >>> from pyramid_adoptedtraversal.interfaces import IChildsDictLike
    >>> from pyramid_adoptedtraversal.adapters import ExampleChildsDictLikeAdapter
    >>> from zope.interface import Interface 
    >>> from pyramid.threadlocal import get_current_registry
    >>> registry = get_current_registry()    
    >>> registry.registerAdapter(ExampleChildsDictLikeAdapter,(Interface,), IChildsDictLike)
    >>> from pyramid_adoptedtraversal.tests import DummyContextWithoutGetitem
    >>> foo = DummyContextWithoutGetitem(None, 'test')
    >>> adapter = IChildsDictLike(foo)
    >>> adapter 
    <pyramid_adoptedtraversal.adapters.ExampleChildsDictLikeAdapter...
    >>> adapter.context
    <DummyContext with name test...

Register the traverser to use the adpater::

    >>> from pyramid.interfaces import ITraverser
    >>> from zope.interface import Interface
    >>> from pyramid_adoptedtraversal.resourcetreetraverseradopted import ResourceTreeTraverserAdopted
    >>> registry = get_current_registry()    
    >>> registry.registerAdapter(ResourceTreeTraverserAdopted, (Interface,), ITraverser)

Cleanup:

    >>> testing.tearDown()


