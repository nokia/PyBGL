#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import sys

from pybgl.graph                import DirectedGraph, add_edge, edges
from pybgl.graph_dp             import GraphDp
from pybgl.graph_extract        import graph_extract
from pybgl.graphviz             import dotstr_to_html
from pybgl.html                 import html
from pybgl.ipynb                import in_ipynb
from pybgl.property_map         import make_assoc_property_map, make_func_property_map
from pybgl.test_common          import run_tests

def test_graph_extract_small(threshold :int = 50):
    g = DirectedGraph(5)
    (e01, _) = add_edge(0, 1, g)
    (e02, _) = add_edge(0, 2, g)
    (e04, _) = add_edge(0, 4, g)
    (e12, _) = add_edge(1, 2, g)
    (e23, _) = add_edge(2, 3, g)
    (e24, _) = add_edge(2, 4, g)
    (e40, _) = add_edge(4, 0, g)
    (e44, _) = add_edge(4, 4, g)
    pmap_eweight = make_assoc_property_map({
        e01 : 83,
        e02 : 3,
        e04 : 78,
        e12 : 92,
        e23 : 7,
        e24 : 18,
        e40 : 51,
        e44 : 84,
    })

    extracted_edges = set()
    pmap_erelevant = make_func_property_map(lambda e: pmap_eweight[e] >= threshold)
    graph_extract(
        0, g,
        pmap_erelevant        = pmap_erelevant,
        callback_edge_extract = lambda e, g: extracted_edges.add(e)
    )

    if in_ipynb():
        pmap_extracted = make_func_property_map(lambda e: e in extracted_edges)
        html(dotstr_to_html(GraphDp(
            g,
                dpe = {
                    "color" : make_func_property_map(lambda e : "darkgreen" if pmap_extracted[e] else "lightgrey"),
                    "style" : make_func_property_map(lambda e : "solid"     if pmap_extracted[e] else "dashed"),
                    "label" : pmap_eweight,
                }
            ).to_dot())
        )

    expected_edges = None

    if threshold == 0:
        expected_edges = {e for e in edges(g)}
    elif threshold == 50:
        expected_edges = {e12, e40, e44, e04, e01}
    elif threshold > 100:
        expected_edges = set()

    if expected_edges is not None:
        assert (extracted_edges == expected_edges), """Invalid edges:
            For threshold = %s:
            extracted: %s
            expected:  %s
        """ % (threshold, sorted(extracted_edges), sorted(expected_edges))

#--------------------------------------------------
# Main program
#--------------------------------------------------

def test_graph_extract():
    """
    Runs the suite test related to CorrelationReverser* classes.
    """
    run_tests([
        (test_graph_extract_small, (0,   )),
        (test_graph_extract_small, (50,  )),
        (test_graph_extract_small, (100, )),
    ])

