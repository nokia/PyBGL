#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.automaton import Automaton, make_automaton
from pybgl.ipynb import in_ipynb
from pybgl.property_map import make_func_property_map
from pybgl.deterministic_inclusion import deterministic_inclusion

TEMPLATE_HTML = "<div style='background-color:white;'>%s</div>"

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
            (3, 4, 's')
        ], 0,
        make_func_property_map(lambda q: q in {4})
    )

def make_fda1():
    return make_automaton(
        [
            (0, 1, 'c'), (1, 2, 'a'), (2, 3, 't'),
            (3, 4, 's'), (0, 5, 'b'), (5, 5, 'b'), (5, 2, 'a')
        ], 0,
        make_func_property_map(lambda q: q in {4})
    )

def make_fda2():
    return make_automaton(
        [
            (0, 1, 'x'), (1, 1, 'y')
        ], 0,
        make_func_property_map(lambda q: q in {1})
    )

def check_deterministic_inclusion(
    g1: Automaton,
    g2: Automaton,
    expected: int,
    show_g1: bool = True,
    show_g2: bool = True
):
    obtained = deterministic_inclusion(g1, g2)

    if in_ipynb():
        from pybgl.graphviz import graph_to_html
        from pybgl.html     import html
        l = list()
        if show_g1:
            l += ["<b>A</b>",  TEMPLATE_HTML % graph_to_html(g1)]
        if show_g2:
            l += ["<b>A'</b>", TEMPLATE_HTML % graph_to_html(g2)]
        result = "A c A'" if obtained == 1 else \
                 "A = A'" if obtained == 0 else \
                 "A' c A" if obtained == -1 else \
                 "A ! A'" if obtained is None else \
                 "??????"
        l.append(result)
        html("<br/>".join(l))

    assert obtained == expected, "obtained = %s expected = %s" % (obtained, expected)

def test_deterministic_inclusion_dafsa():
    g1 = make_dafsa1()
    g2 = make_dafsa2()
    tests = [(g1, g2, -1), (g2, g1, 1), (g1, g1, 0), (g2, g2, 0)]
    for args in tests:
        check_deterministic_inclusion(*args)

def test_deterministic_inclusion_fda():
    g1 = make_dafsa1()
    g3 = make_fda1()
    g4 = make_fda2()
    tests = [
        (g1, g3, 1), (g3, g1, -1), (g1, g1, 0), (g3, g3, 0),
        (g1, g4, None), (g4, g1, None), (g3, g4, None), (g4, g3, None)
    ]
    for args in tests:
        check_deterministic_inclusion(*args)
