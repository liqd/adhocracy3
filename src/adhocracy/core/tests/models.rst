Model classes
==============

We have an application root object::

    >>> from pyramid import testing
    >>> request = testing.DummyRequest()
    >>> root =  app.root_factory(request)

We can add container objects to the root object::

    >>> from adhocracy.core.models.interfaces import IContainer
    >>> from adhocracy.core.models.interfaces import INode
    >>> from repoze.lemonade.content import create_content
    >>> container0 = create_content(IContainer, name=u"g0")
    >>> root["g0"] = container0
    >>> root["g0"]
    <Container: http://localhost...

or add them as childs to other container objects::

    >>> container1 = create_content(IContainer, name=u"g1")
    >>> root["g0"]["g1"] = container1
    >>> root["g0"]["g1"]
    <Container: http://localhost...
