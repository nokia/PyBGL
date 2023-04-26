#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

import sys

from collections import defaultdict
from pybgl.graph import DirectedGraph
from pybgl.graph_dp import GraphDp
from pybgl.graph_extract import graph_extract
from pybgl.graphviz import dotstr_to_html
from pybgl.html import html
from pybgl.ipynb import in_ipynb
from pybgl.property_map import make_assoc_property_map, make_func_property_map

def _test_graph_extract_small(threshold: int = 50):
    g = DirectedGraph(5)
    (e01, _) = g.add_edge(0, 1)
    (e02, _) = g.add_edge(0, 2)
    (e04, _) = g.add_edge(0, 4)
    (e12, _) = g.add_edge(1, 2)
    (e23, _) = g.add_edge(2, 3)
    (e24, _) = g.add_edge(2, 4)
    (e40, _) = g.add_edge(4, 0)
    (e44, _) = g.add_edge(4, 4)
    pmap_eweight = make_assoc_property_map(
        defaultdict(
            int,
            {
                e01: 83,
                e02: 3,
                e04: 78,
                e12: 92,
                e23: 7,
                e24: 18,
                e40: 51,
                e44: 84,
            }
        )
    )

    extracted_edges = set()
    pmap_erelevant = make_func_property_map(lambda e: pmap_eweight[e] >= threshold)
    graph_extract(
        0, g,
        pmap_erelevant=pmap_erelevant,
        callback_edge_extract = lambda e, g: extracted_edges.add(e)
    )

    if in_ipynb():
        pmap_extracted = make_func_property_map(lambda e: e in extracted_edges)
        html(
            dotstr_to_html(
                GraphDp(
                    g,
                    dpe = {
                        "color": make_func_property_map(
                            lambda e: "darkgreen" if pmap_extracted[e] else "lightgrey"
                        ),
                        "style": make_func_property_map(
                            lambda e: "solid" if pmap_extracted[e] else "dashed"
                        ),
                        "label": pmap_eweight,
                    }
                ).to_dot()
            )
        )

    expected_edges = None

    if threshold == 0:
        expected_edges = set(g.edges())
    elif threshold == 50:
        expected_edges = {e12, e40, e44, e04, e01}
    elif threshold > 100:
        expected_edges = set()

    if expected_edges is not None:
        assert (extracted_edges == expected_edges), """Invalid edges:
            For threshold = %s:
            extracted: %s
            expected: %s
        """ % (threshold, sorted(extracted_edges), sorted(expected_edges))

def test_graph_extract_small():
    for threshold in [0, 50, 100]:
        _test_graph_extract_small(threshold)
