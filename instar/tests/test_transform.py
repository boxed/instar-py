from instar import transform, inc, dissoc, expand_path, get_in, transform2, discard, rex, ny
from pyrsistent import freeze, thaw


def test_get_in():
    assert get_in({}, ['foo', 'bar']) is None


def test_expand_path():
    assert expand_path(freeze({'foo': 1, 'bar': 2}), [], [any]) == [
        ['bar'],
        ['foo'],
    ]
    assert expand_path(freeze({'foo': {'bar': {'baz': 1}}}), [], [any, any, any]) == [
        ['foo', 'bar', 'baz']
    ]
    assert expand_path(freeze({'foo': {'bar': {'baz': 1, 'qux': 4}}}), [], ['foo', any, any]) == [
        ['foo', 'bar', 'baz'],
        ['foo', 'bar', 'qux']
    ]


def test_simple():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    e = freeze({})
    assert transform(e, ['foo', 'bar', 'baz'], 7) == {'foo': {'bar': {'baz': 7}}}
    assert transform(m, ['foo', 'bar', 'baz'], inc) == {'foo': {'bar': {'baz': 2}}}
    assert transform(m, ['foo', 'bar', 'baz'], dissoc) == {'foo': {'bar': {}}}


def test_star():
    foo = freeze({'foo': {'bar': {'baz': 1, 'qux': 4},
                          'bar2': {'baz': 2, 'qux': 5}}})
    expected = {'foo': {'bar': {'baz': 2, 'qux': 5},
                'bar2': {'baz': 3, 'qux': 6}}}
    assert thaw(transform(foo, ['foo', any, any], inc)) == expected


def test_callable_no_match():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    assert transform(m, ['foo', lambda x: x.startswith('c'), 'baz'], inc) == m


def test_callable():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    assert transform(m, ['foo', lambda x: x.startswith('b'), 'baz'], inc) == {'foo': {'bar': {'baz': 2}}}


def test_transform2_simple_callable_command():
    m2 = freeze({'foo': {'bar': {'baz': 1}}})
    assert transform2(m2, ['foo', 'bar', 'baz'], inc) == {'foo': {'bar': {'baz': 2}}}


def test_transform2_callable_matcher():
    m = freeze({'foo': {'bar': {'baz': 1}, 'qux': {'baz': 1}}})
    assert transform2(m, ['foo', lambda x: x.startswith('b'), 'baz'], inc) == {'foo': {'bar': {'baz': 2}, 'qux': {'baz': 1}}}


def test_transform2_remove():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    assert transform2(m, ['foo', 'bar', 'baz'], discard) == {'foo': {'bar': {}}}


def test_transform2_callable_no_match():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    assert transform2(m, ['foo', lambda x: x.startswith('c'), 'baz'], inc) == m


def test_transform2_rex():
    m = freeze({'foo': {'bar': {'baz': 1},
                        'bof': {'baz': 1}}})
    assert transform2(m, ['foo', rex('^bo.*'), 'baz'], inc) == {'foo': {'bar': {'baz': 1},
                                                                        'bof': {'baz': 2}}}


def test_transform2_ny():
    m = freeze({'foo': 1, 'bar': 2})
    assert transform2(m, [ny], 5) == {'foo': 5, 'bar': 5}
