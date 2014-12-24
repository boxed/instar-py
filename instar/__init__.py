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
        return structure.remove(path[0])
    sub_structure = get_in(structure, path[:-1])
    return structure.set_in(path[:-1], sub_structure.remove(path[-1]))


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