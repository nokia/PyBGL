#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    deterministic_union,
    in_ipynb,
    make_automaton,
    make_func_property_map,
)


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


def test_deterministic_union(
    show_g1: bool = True,
    show_g2: bool = True,
    show_g12: bool = True
):
    g1 = make_dafsa1()
    g2 = make_dafsa2()
    g12 = deterministic_union(g1, g2)

    if in_ipynb():
        from pybgl import graph_to_html
        from pybgl import html
        lines = list()
        if show_g1:
            lines += ["<b>A</b>",  graph_to_html(g1)]
        if show_g2:
            lines += ["<b>A'</b>", graph_to_html(g2)]
        if show_g12:
            lines += ["<b>A &#x222a; A'</b><br/>", graph_to_html(g12)]
        html("<br/>".join(lines))
    assert g12.num_vertices() == 12
    assert g12.num_edges() == 11
