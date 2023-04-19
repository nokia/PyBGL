#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.automaton import accepts
from pybgl.graph import num_edges, num_vertices
from pybgl.ipynb import in_ipynb, ipynb_display_graph
from pybgl.regexp import compile_nfa, compile_dfa

if in_ipynb():
    display_graph = ipynb_display_graph
else:
    display_graph = lambda g: None

# PATTERN_IPV6 accepts any IPv6 addresses, but is not strict enough to catch only IPv6.
HEX4 = "[a-fA-F0-9]{0,4}"
IPV6_SEP = ":"
PATTERN_IPV6 = "(" + HEX4 + ")?(" + IPV6_SEP + HEX4 + ")+" + IPV6_SEP + HEX4

def make_nfa_ipv6():
    return compile_nfa(PATTERN_IPV6)

def make_dfa_ipv6():
    return compile_dfa(PATTERN_IPV6)

def test_compile_nfa_ipv6():
    nfa = make_nfa_ipv6()
    assert num_vertices(nfa) >= 15 and num_edges(nfa) >= 279

def test_compile_dfa_ipv6():
    dfa = make_dfa_ipv6()
    assert num_vertices(dfa) == 15 and num_edges(dfa) == 279

def test_nfa_dfa_ipv6_correctness():
    for f in [make_nfa_ipv6, make_dfa_ipv6]:
        g = f()
        assert accepts("::1", g)
        assert accepts("2a02:a802:23::1", g)
        assert accepts("2a01:e35:2e49:10c0:eeb3:6f16:6bd4:d833", g)
        assert accepts("2A01:E35:2E49:10C0:EEB3:6F16:6BD4:D833", g)
        assert not accepts("2A01:X35:2E49:10C0:EEB3:6F16:6BD4:D833", g)
        assert not accepts(":", g)
        assert not accepts("A", g)
        assert not accepts(":A", g)
        assert not accepts("1", g)
        assert not accepts(":1", g)
