#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.incidence_automaton import make_incidence_automaton
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
    assert len(set(G1.edges())) == 8
    prune_incidence_automaton(G1)
    assert set(G1.vertices()) == {0, 1, 2}
    assert set(
        (G1.source(e), G1.target(e)) for e in G1.edges()
    ) == {(0, 1), (1, 2), (0, 0), (2, 1), (1, 1)}
