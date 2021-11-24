#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.graphviz             	import graph_to_html
from pybgl.html                 	import beside, html
from pybgl.incidence_automaton      import make_incidence_automaton
from pybgl.incidence_node_automaton import *
from pybgl.ipynb                	import in_ipynb
from pybgl.revuz_minimize 			import *

#--------------------------------------------------
# Internals
#--------------------------------------------------

def check_graph(g :IncidenceAutomaton, e_expected :set):
    e_obtained = {(source(e, g), target(e, g)) for e in edges(g)}
    assert e_obtained == e_expected, \
        f"""
        Invalid edges:
            expected: {sorted(e_expected)}
            obtained: {sorted(e_obtained)}
        """

def _test_revuz_minimize(g :IncidenceAutomaton, e_expected :set):
    before_html = graph_to_html(g) if in_ipynb() else None
    revuz_minimize(g)
    if in_ipynb():
        after_html = graph_to_html(g)
        html(beside(before_html, after_html, "Minimization", "Before", "After"))
    check_graph(g, e_expected)

#--------------------------------------------------
# Tests
#--------------------------------------------------

def test_revuz_height():
    g = make_incidence_node_automaton(
        [
            (0, 1), (0, 2),
            (1, 2), (1, 3),
            (2, 4), (3, 4)
        ],
        make_assoc_property_map(defaultdict(
            lambda: None,
            {
                1 : "a",
                2 : "b",
                3 : "a",
                4 : "c"
            })
        )
    )

    map_vheight  = defaultdict()
    pmap_vheight = make_assoc_property_map(map_vheight)
    pmap_vlabel  = make_func_property_map(lambda u: "%s<br/>height: %s" % (u, pmap_vheight[u]))
    max_height   = revuz_height(g, pmap_vheight)

    if in_ipynb():
        html(graph_to_html(g))

    assert map_vheight == {0 : 3, 1 : 2, 2 : 1, 3 : 1, 4 : 0}
    assert max_height  == 3, f"Expected max_height = 3, got {max_height}"

def test_revuz_minimize_elabel():
    _test_revuz_minimize(
        g = make_incidence_automaton([
            (0, 1, "a"),
            (0, 2, "b"),
            (1, 4, "a"),
            (2, 3, "c"),
            (3, 5, "b"),
            (4, 6, "b"),
            (5, 7, "b"),
            (6, 8, "c"),
            (7, 9, "d"),
        ]),
        e_expected = {
            (0, 1), (1, 4), (4, 6), (6, 8),
            (0, 2), (2, 3), (3, 5), (5, 7), (7, 8)
        }
    )

def test_revuz_minimize_vlabel():
    _test_revuz_minimize(
        g = make_incidence_node_automaton(
            [
                (0, 1), (0, 2), (2, 3),
                (1, 4), (3, 5), (4, 6),
                (5, 7), (6, 8), (7, 9),
            ],
            make_assoc_property_map(
                defaultdict(
                    lambda: None,
                    {
                        1 : "a", 2 : "b", 3 : "a",
                        4 : "a", 5 : "b", 6 : "c",
                        7 : "c", 8 : "d", 9 : "d",
                    }
                )
            )
        ),
        e_expected = {(0, 1), (0, 2), (1, 3), (2, 4), (3, 6), (4, 5), (5, 6), (6, 8)}
    )

def test_revuz_minimize_final():
    _test_revuz_minimize(
        g = make_incidence_node_automaton(
            [(0, 1), (0, 2), (2, 3)],
            make_assoc_property_map({1 : "a", 2 : "b", 3 : "a"})
        ),
        e_expected = {(0, 1), (0, 2), (2, 1)}
    )
    _test_revuz_minimize(
        g = make_incidence_node_automaton(
            [(0, 1), (0, 2), (2, 3)],
            make_assoc_property_map({1 : "a", 2 : "b", 3 : "a"}),
            pmap_vfinal = make_func_property_map(lambda q: q == 1)
        ),
        e_expected = {(0, 1), (0, 2), (2, 3)}
    )

