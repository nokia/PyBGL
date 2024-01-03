#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import EPSILON, Nfa, graph_to_html


def make_nfa1(eps=EPSILON):
    g = Nfa(4)
    (e01a, _) = g.add_edge(0, 1, "a")
    assert g.label(e01a) == "a"
    assert g.is_epsilon_transition(e01a) is False
    (e02a, _) = g.add_edge(0, 2, "a")
    (e02b, _) = g.add_edge(0, 2, "b")
    (e02a, _) = g.add_edge(0, 2, "a")
    (e21b, _) = g.add_edge(2, 1, "a")
    (e03e, _) = g.add_edge(0, 3, eps)
    assert g.label(e03e) == g.epsilon
    assert g.is_epsilon_transition(e03e) is True
    (e33c, _) = g.add_edge(3, 3, "c")
    g.set_final(1)
    g.set_final(3)
    assert set(g.vertices()) == {0, 1, 2, 3}
    return g


def make_nfa2(eps=EPSILON):
    g = Nfa(3)
    g.add_edge(0, 1, "a")
    g.add_edge(0, 1, "a")
    g.add_edge(0, 3, eps)
    g.add_edge(1, 1, eps)
    g.add_edge(1, 2, eps)
    g.add_edge(2, 2, eps)
    g.add_edge(0, 3, "a")
    g.add_edge(3, 3, eps)
    g.set_final(1)
    g.set_final(3)
    return g


def test_num_vertices():
    g = make_nfa1()
    assert g.num_vertices() == 4


def test_num_edges():
    g = make_nfa1()
    assert g.num_edges() == 6


def test_alphabet():
    g = make_nfa1()
    assert g.alphabet() == {"a", "b", "c"}


def test_sigma():
    # sigma(q, g) list symbols != epsilon carried by egress transition
    # starting from q or any state reachable from q via one or more
    # epsilon transitions.
    g = make_nfa1()
    assert g.sigma(0) == {"a", "b", "c"}
    assert g.sigma(1) == set()
    assert g.sigma(2) == {"a"}
    assert g.sigma(3) == {"c"}


def test_accepts():
    g = make_nfa1()
    assert g.accepts("a") is True
    assert g.accepts("aa") is True
    assert g.accepts("b") is False
    assert g.accepts("ba") is True
    assert g.accepts("c") is True
    assert g.accepts("cc") is True
    assert g.accepts("") is True


def test_finals():
    g = make_nfa1()
    f = set(g.finals())
    assert f == {1, 3}
    for q in g.vertices():
        assert g.is_final(q) == bool(q in f)


def test_initials():
    g = make_nfa1()
    i = set(g.initials)
    assert i == {0}
    for q in g.vertices():
        assert g.is_initial(q) == bool(q in i)


def test_delta1():
    g = make_nfa1()
    assert g.delta(0, "a") == {1, 2}
    assert g.delta(0, "b") == {2}
    assert g.delta(0, "c") == {3}
    assert g.delta(1, "a") == set()
    assert g.delta(1, "b") == set()
    assert g.delta(1, "c") == set()
    assert g.delta(2, "a") == {1}
    assert g.delta(2, "b") == set()
    assert g.delta(2, "c") == set()
    assert g.delta(3, "a") == set()
    assert g.delta(3, "b") == set()
    assert g.delta(3, "c") == {3}


def test_delta2(debug: bool = False):
    g = make_nfa2()
    for q in g.vertices():
        qs = g.delta(q, 'a')
        if debug:
            print(f"g.delta({q}, 'a') = {qs}")
        assert qs == set() if q != 0 else {1, 3}


def test_delta_word():
    g = make_nfa1()
    assert g.delta_word("a") == {1, 2}
    assert g.delta_word("aa") == {1}
    assert g.delta_word("z") == set()
    assert g.delta_word("ccc") == {3}


def test_set_initials():
    g = make_nfa1()
    assert set(g.initials) == {0}
    g.set_initial(2, True)
    assert g.accepts("a") is True
    assert g.accepts("aa") is True
    assert g.accepts("ccc") is True
    g.set_initial(0, False)
    assert g.accepts("a") is True
    assert g.accepts("aa") is False
    assert g.accepts("ccc") is False


def test_nfa_graphviz():
    nfa = make_nfa1()
    _ = graph_to_html(nfa)
