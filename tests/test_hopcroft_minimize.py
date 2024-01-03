#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    hopcroft_minimize,
    make_incidence_automaton,
    make_func_property_map,
)


G6 = make_incidence_automaton(
    [
        (0, 1, 'a'), (0, 2, 'b'),
        (1, 1, 'a'), (1, 3, 'b'),
        (2, 1, 'a'), (2, 2, 'b'),
        (3, 1, 'a'), (3, 4, 'b'),
        (4, 1, 'a'), (4, 2, 'b')
    ], 0,
    make_func_property_map(lambda q: q in {4})
)

G7 = make_incidence_automaton(
    [
        (0, 1, 'a'), (0, 2, 'b'),
        (1, 0, 'a'), (1, 3, 'b'),
        (2, 4, 'a'), (2, 5, 'b'),
        (3, 4, 'a'), (3, 5, 'b'),
        (4, 4, 'a'), (4, 5, 'b'),
        (5, 5, 'a'), (5, 5, 'b')
    ], 0, make_func_property_map(lambda q: q in {2, 3, 4})
)

G8 = make_incidence_automaton(
    [
        (0, 1, 'a'),
        (1, 2, 'a'),
        (2, 3, 'a'),
        (3, 4, 'a'),
        (4, 5, 'a'),
        (5, 6, 'a'),
        (6, 7, 'a'),
        (7, 8, 'a'),
        (8, 9, 'a'),
        (9, 10, 'a'),
        (10, 11, 'a'),
        (11, 12, 'a'),
        (12, 11, 'a')
    ], 0, make_func_property_map(lambda q: q in {0, 2, 4, 6, 8, 10, 12})
)

G9 = make_incidence_automaton(
    [
        (0, 1, 'a'),
        (1, 2, 'a'),
        (2, 3, 'a'),
        (3, 4, 'a'),
        (4, 5, 'a'),
        (5, 6, 'a'),
        (6, 7, 'a'),
        (7, 8, 'a'),
        (8, 9, 'a'),
        (9, 10, 'a'),
        (10, 11, 'a'),
        (11, 12, 'a'),
        (12, 12, 'a')
    ], 0, make_func_property_map(lambda q: q in {0, 2, 4, 6, 8, 10, 12})
)


def test_automaton_hopcroft_minimize():
    min_G6 = hopcroft_minimize(G6)
    assert min_G6.num_vertices() == 4
    assert min_G6.num_edges() == 8
    min_G7 = hopcroft_minimize(G7)
    assert min_G7.num_vertices() == 3
    assert min_G7.num_edges() == 6
    min_G8 = hopcroft_minimize(G8)
    assert min_G8.num_vertices() == 2
    assert min_G8.num_edges() == 2
    min_G9 = hopcroft_minimize(G9)
    assert min_G9.num_vertices() == 13
    assert min_G9.num_edges() == 13
