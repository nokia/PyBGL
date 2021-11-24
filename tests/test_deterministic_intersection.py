#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.automaton                   import make_automaton, num_vertices, num_edges
from pybgl.ipynb                       import in_ipynb
from pybgl.property_map                import make_func_property_map
from pybgl.deterministic_intersection  import deterministic_intersection

def make_dafsa1():
    return make_automaton(
        [
            (0, 1, 'c'), (1, 2, 'a'), (2, 3, 't'),
            (3, 4, 's'), (0, 5, 'b'), (5, 2, 'a')
        ], 0,
        make_func_property_map(lambda q: q in {4})
    )

def make_dafsa2():
    return make_automaton(
        [
            (0, 1, 'c'), (1, 2, 'a'), (2, 3, 't'),
            (3, 4, 's'), (2, 5, 'l'), (5, 3, 'l')
        ], 0,
        make_func_property_map(lambda q: q in {4})
    )

def test_deterministic_intersection(show_g1 :bool = True, show_g2 :bool = True, show_g12 :bool = True):
    g1 = make_dafsa1()
    g2 = make_dafsa2()
    g12 = deterministic_intersection(g1, g2)

    if in_ipynb():
        from pybgl.graphviz import graph_to_html
        from pybgl.html     import html
        l = list()
        if show_g1:  l += ["<b>A</b>",  graph_to_html(g1)]
        if show_g2:  l += ["<b>A'</b>", graph_to_html(g2)]
        if show_g12: l += ["<b>A &#x2229; A'</b><br/>", graph_to_html(g12)]
        html("<br/>".join(l))
    assert num_vertices(g12) == 5
    assert num_edges(g12) == 4
