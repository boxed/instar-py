# instar-py
# =========
# 
# Easier transformations for pyrsistent data structures. Basically a port of my clojure library instar. 
# 
def test_line_5():
    from instar import transform, inc, dissoc
    from pyrsistent import m, freeze
    
    m = freeze({'foo': {'bar': {'baz': 1}}})
    e = freeze({})
    assert transform(e, ['foo', 'bar', 'baz'], 7) == {'foo': {'bar': {'baz': 7}}}
    assert transform(m, ['foo', 'bar', 'baz'], inc) == {'foo': {'bar': {'baz': 2}}}
    assert transform(m, ['foo', 'bar', 'baz'], dissoc) == {'foo': {'bar': {}}}
    

