################
#  test utils  #
################


def test_diff_dict():
    from . import diff_dict
    old = {'foo': 5, 'bar': 6, 'kaz': 8}
    new = {'bar': 6, 'baz': 7, 'kaz': 9, 'faz': 10}
    diff = diff_dict(old, new)
    assert diff == (set(['baz', 'faz']), set(['kaz']), set(['foo']))


def test_diff_dict_omit():
    from . import diff_dict
    old = {'foo': 5, 'bar': 6, 'kaz': 8}
    new = {'bar': 6, 'baz': 7, 'kaz': 9, 'faz': 10}
    diff = diff_dict(old, new, omit=('foo',))
    assert diff == (set(['baz', 'faz']), set(['kaz']), set())


#FIXME: more tests
