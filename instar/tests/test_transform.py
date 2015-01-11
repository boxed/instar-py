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


def test_transform2_callable_command():
    m2 = freeze({'foo': {'bar': {'baz': 1}}})
    assert transform2(m2, ['foo', 'bar', 'baz'], inc) == {'foo': {'bar': {'baz': 2}}}


def test_transform2_predicate():
    m = freeze({'foo': {'bar': {'baz': 1}, 'qux': {'baz': 1}}})
    assert transform2(m, ['foo', lambda x: x.startswith('b'), 'baz'], inc) == {'foo': {'bar': {'baz': 2}, 'qux': {'baz': 1}}}


def test_transform2_remove():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    assert transform2(m, ['foo', 'bar', 'baz'], discard) == {'foo': {'bar': {}}}


def test_transform2_predicate_no_match():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    assert transform2(m, ['foo', lambda x: x.startswith('c'), 'baz'], inc) == m


def test_transform2_rex_redicate():
    m = freeze({'foo': {'bar': {'baz': 1},
                        'bof': {'baz': 1}}})
    assert transform2(m, ['foo', rex('^bo.*'), 'baz'], inc) == {'foo': {'bar': {'baz': 1},
                                                                        'bof': {'baz': 2}}}


def test_rex_with_non_string_key():
    m = freeze({'foo': 1, 5: 2})
    assert transform2(m, [rex(".*")], 5) == {'foo': 5, 5: 2}


def test_transform2_ny_predicated_matches_any_key():
    m = freeze({'foo': 1, 5: 2})
    assert transform2(m, [ny], 5) == {'foo': 5, 5: 5}


def test_transform2_new_elements_created_when_missing():
    m = freeze({})
    assert transform2(m, ['foo', 'bar', 'baz'], 7) == {'foo': {'bar': {'baz': 7}}}


def test_transform2_mixed_vector_and_map():
    m = freeze({'foo': [1, 2, 3]})
    assert transform2(m, ['foo', 1], 5) == freeze({'foo': [1, 5, 3]})


def test_transform2_vector_predicate_callable_command():
    v = freeze([1, 2, 3, 4, 5])
    assert transform2(v, [lambda i: 0 < i < 4], inc) == freeze(freeze([1, 3, 4, 5, 5]))


def test_transform2_vector_insert_map_one_step_beyond_end():
    v = freeze([1, 2])
    assert transform2(v, [2, 'foo'], 3) == freeze([1, 2, {'foo': 3}])
