#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from pybgl.incidence_automaton import (
    edges, make_incidence_automaton, source, target, vertices
)
from pybgl.prune_incidence_automaton import prune_incidence_automaton
from pybgl.property_map import make_func_property_map

G1 = make_incidence_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 2, 'a'), (1, 1, 'b'),
        (2, 1, 'a'), (2, 1, 'b'),
        (3, 4, 'a'), (5, 1, 'b'),
        (1, 6, 'a')
    ], 0,
    make_func_property_map(lambda q: q in {1})
)

def test_prune_incidence_automaton():
    assert len(set(edges(G1))) == 8
    prune_incidence_automaton(G1)
    assert set(vertices(G1)) == {0, 1, 2}
    assert set(
        (source(e, G1), target(e, G1)) for e in edges(G1)
    ) == {(0, 1), (1, 2), (0, 0), (2, 1), (1, 1)}
