Model classes
==============

setup::

    >>> from adhocracy.core.testing import setUp
    >>> from adhocracy.core.testing import load_registry
    >>> conf = setUp()
    >>> registry = load_registry(conf)

We have an application root object::

    >>> from pyramid import testing
    >>> request = testing.DummyRequest()
    >>> import adhocracy.core
    >>> root = adhocracy.core.root_factory(request)

We can add container objects to the root object::

    >>> from repoze.lemonade.content import create_content
    >>> from adhocracy.core.models.interfaces import IContainer
    >>> from adhocracy.core.models.interfaces import IChildsDict
    >>> root_adapter = IChildsDict(root)
    >>> root_adapter["g0"] = create_content(IContainer, name=u"g0")
    >>> root_adapter["g0"]
    <Container: http://localhost...


or add them as childs to other container objects::

    >>> g0_adapter = IChildsDict(root_adapter["g0"])
    >>> g0_adapter["g1"] = create_content(IContainer, name=u"g1")
    >>> g0_adapter["g1"]
    <Container: http://localhost...



