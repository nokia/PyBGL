#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.nfa import *
from pybgl.graphviz import graph_to_html

def make_nfa1(eps=EPSILON):
    g = Nfa(4)
    (e01a, _) = add_edge(0, 1, "a", g)
    assert label(e01a, g) == "a"
    assert is_epsilon_transition(e01a, g) is False
    (e02a, _) = add_edge(0, 2, "a", g)
    (e02b, _) = add_edge(0, 2, "b", g)
    (e02a, _) = add_edge(0, 2, "a", g)
    (e21b, _) = add_edge(2, 1, "a", g)
    (e03e, _) = add_edge(0, 3, eps, g)
    assert label(e03e, g) == epsilon(g)
    assert is_epsilon_transition(e03e, g) is True
    (e33c, _) = add_edge(3, 3, "c", g)
    set_final(1, g)
    set_final(3, g)
    assert set(vertices(g)) == {0, 1, 2, 3}
    return g

def make_nfa2(eps=EPSILON):
    g = Nfa(3)
    add_edge(0, 1, "a", g)
    add_edge(0, 1, "a", g)
    add_edge(0, 3, eps, g)
    add_edge(1, 1, eps, g)
    add_edge(1, 2, eps, g)
    add_edge(2, 2, eps, g)
    add_edge(0, 3, "a", g)
    add_edge(3, 3, eps, g)
    set_final(1, g)
    set_final(3, g)
    return g

def test_num_vertices():
    g = make_nfa1()
    assert num_vertices(g) == 4

def test_num_edges():
    g = make_nfa1()
    assert num_edges(g) == 6

def test_alphabet():
    g = make_nfa1()
    assert alphabet(g) == {"a", "b", "c"}

def test_sigma():
    # sigma(q, g) list symbols != epsilon carried by egress transition
    # starting from q or any state reachable from q via one or more
    # epsilon transitions.
    g = make_nfa1()
    assert sigma(0, g) == {"a", "b", "c"}
    assert sigma(1, g) == set()
    assert sigma(2, g) == {"a"}
    assert sigma(3, g) == {"c"}

def test_accepts():
    g = make_nfa1()
    assert accepts("a", g) is True
    assert accepts("aa", g) is True
    assert accepts("b", g) is False
    assert accepts("ba", g) is True
    assert accepts("c", g) is True
    assert accepts("cc", g) is True
    assert accepts("", g) is True

def test_finals():
    g = make_nfa1()
    f = set(finals(g))
    assert f == {1, 3}
    for q in vertices(g):
        assert is_final(q, g) == bool(q in f)

def test_initials():
    g = make_nfa1()
    i = set(initials(g))
    assert i == {0}
    for q in vertices(g):
        assert is_initial(q, g) == bool(q in i)

def test_delta1():
    g = make_nfa1()
    assert delta(0, "a", g) == {1, 2}
    assert delta(0, "b", g) == {2}
    assert delta(0, "c", g) == {3}
    assert delta(1, "a", g) == set()
    assert delta(1, "b", g) == set()
    assert delta(1, "c", g) == set()
    assert delta(2, "a", g) == {1}
    assert delta(2, "b", g) == set()
    assert delta(2, "c", g) == set()
    assert delta(3, "a", g) == set()
    assert delta(3, "b", g) == set()
    assert delta(3, "c", g) == {3}

def test_delta2():
    g = make_nfa2()
    for q in vertices(g):
        qs = delta(q, 'a', g)
        print(f"delta({q}, 'a') = {qs}")
        assert qs == set() if q != 0 else {1,3}

def test_delta_word():
    g = make_nfa1()
    assert delta_word("a", g) == {1, 2}
    assert delta_word("aa", g) == {1}
    assert delta_word("z", g) == set()
    assert delta_word("ccc", g) == {3}

def test_set_initials():
    g = make_nfa1()
    assert set(initials(g)) == {0}
    set_initial(2, g, True)
    assert accepts("a", g) is True
    assert accepts("aa", g) is True
    assert accepts("ccc", g) is True
    set_initial(0, g, False)
    assert accepts("a", g) is True
    assert accepts("aa", g) is False
    assert accepts("ccc", g) is False

def test_nfa_graphviz():
    nfa = make_nfa1()
    svg = graph_to_html(nfa)
