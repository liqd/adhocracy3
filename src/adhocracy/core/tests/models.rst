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


Now we can traverse the resulting object hierachy::

    >>> browser.open('http://localhost/')
    >>> "pyramid" in browser.contents
    True

...TODO not working with doctest >>> browser.open('http://localhost/g0')

