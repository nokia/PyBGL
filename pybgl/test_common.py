#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import traceback

from pybgl.graph        import Graph, edges, num_vertices, num_edges, vertices
from pybgl.ipynb        import in_ipynb
from pybgl.property_map import ReadPropertyMap

def check_graph_size(g :Graph, n_expected :int, m_expected :int):
    """
    Tests whether a Graph has the expected size.
    Args:
        n_expected: The expected number of vertices.
        m_expected: The expected number of edges.
    """
    n = num_vertices(g)
    m = num_edges(g)
    assert n == n_expected, "Expected %s vertices, got %s" % (n_expected, n)
    assert m == m_expected, "Expected %s edges, got %s"    % (m_expected, m)

def check_pmap(
    pmap_expected :ReadPropertyMap,
    pmap_obtained :ReadPropertyMap,
    keys :list,
    pmap_name :str = ""
):
    """
    Tests whether a ReadPropertyMap has the expected value.
    Args:
        pmap_expected: The reference ReadPropertyMap.
        pmap_obtained: The tested ReadPropertyMap.
        keys: The keys to process.
        pmap_name: The name of the pmap (for debugging purposes).
    """
    for key in keys:
        obtained = pmap_obtained[key]
        expected = pmap_expected[key]
        assert expected == obtained, "%s[%s] invalid: expected %s, got %s" % (pmap_name, key, expected, obtained)

def check_pmap_vertex(
    pmap_expected :ReadPropertyMap,
    pmap_obtained :ReadPropertyMap,
    g :Graph,
    pmap_name :str = ""
):
    check_pmap(pmap_expected, pmap_obtained, vertices(g), pmap_name)

def check_pmap_edge(
    pmap_expected :ReadPropertyMap,
    pmap_obtained :ReadPropertyMap,
    g :Graph,
    pmap_name :str = ""
):
    check_pmap(pmap_expected, pmap_obtained, edges(g), pmap_name)

def run_tests(tests):
    """
    Run a list of tests.
    Args:
        tests: A list of pair (f, args) where:
            f: A test_* function, which raise exceptions in case
                of problem.
            args: A tuple corresponding to the parameters passed to f.
    Returns:
        0 in case of success, 1 otherwise.
    """
    ret = 0
    try:
        # Call each tests
        #for name, f in tests.items():
        for f, args in tests:
            s = "Running test: %s%s" % (f.__name__, args)
            if in_ipynb():
                from pybgl.html import html
                html("<b>%s</b>" % s)
            else:
                print(s)
            f(*args)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        ret = 1
    return ret
