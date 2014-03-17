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


def test_strip_optional_prefix():
    from . import strip_optional_prefix
    assert strip_optional_prefix('footile', 'foo') == 'tile'
    assert strip_optional_prefix('futile', 'foo') == 'futile'
    assert strip_optional_prefix('footile', 'oot') == 'footile'
    assert strip_optional_prefix('footile', 'ile') == 'footile'
    assert strip_optional_prefix('', 'foo') == ''
    assert strip_optional_prefix('footile', '') == 'footile'
    assert strip_optional_prefix(' footile ', 'foo') == ' footile '
    assert strip_optional_prefix('foo', 'foo') == ''
    assert strip_optional_prefix('foo', 'foot') == 'foo'

#FIXME: more tests
