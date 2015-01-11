from collections import Mapping

inc = lambda x: x + 1
dec = lambda x: x - 1
dissoc = object()  # marker object


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def get_in(structure, path):
    if structure is None:
        return None
    if not path:
        return structure
    if len(path) == 1:
        return structure.get(path[0])
    return get_in(structure.get(path[0]), path[1:])


def dissoc_in(structure, path):
    assert path
    if len(path) == 1:
        return structure.discard(path[0])
    sub_structure = get_in(structure, path[:-1])
    return structure.set_in(path[:-1], sub_structure.discard(path[-1]))


def expand_path(structure, already_evaluated_path, rest_path):
    if not rest_path:
        return [already_evaluated_path + []]
    if rest_path[0] is any or callable(rest_path[0]):
        result = []
        for x in get_in(structure, already_evaluated_path).keys():
            if rest_path[0] is any or rest_path[0](x):
                result.extend(expand_path(structure, already_evaluated_path + [x], rest_path[1:]))
        return result
    else:
        return expand_path(structure, already_evaluated_path + [rest_path[0]], rest_path[1:])


def transform(structure, *transformations):
    r = structure
    for p, command in chunks(transformations, 2):
        for path in expand_path(structure, [], p):
            if command is dissoc:
                r = dissoc_in(r, path)
            elif callable(command):
                r = r.set_in(path, command(get_in(r, path)))
            else:
                r = r.set_in(path, command)
    return r


def _discard(evolver, key):
    try:
        del evolver[key]
    except KeyError:
        pass

discard = _discard

import re
from pyrsistent import pmap


def rex(expr):
    r = re.compile(expr)
    return lambda key: isinstance(key, basestring) and r.match(key)

ny = lambda _: True


def transform2(structure, *transformations):
    r = structure
    for path, command in chunks(transformations, 2):
        r = do_to_path(r, path, command)
    return r


def do_to_path(structure, path, command):
    if not path:
        return command(structure) if callable(command) else command

    kvs = get_keys_and_values(structure, path[0])
    return update_structure(structure, kvs, path[1:], command)


def items(structure):
    try:
        return structure.items()
    except AttributeError:
        return list(enumerate(structure))


def get(structure, key, default):
    try:
        return structure[key]
    except (IndexError, KeyError):
        return default


def get_keys_and_values(structure, key_spec):
    if callable(key_spec):
        return [(k, v) for k, v in items(structure) if key_spec(k)]

    return [(key_spec, get(structure, key_spec, pmap()))]


def update_structure(structure, kvs, path, command):
    e = structure.evolver()
    for k, v in kvs:
        if not path and command is discard:
            discard(e, k)
        else:
            e[k] = do_to_path(v, path, command)
    return e.persistent()
