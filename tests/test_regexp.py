#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.automaton import accepts
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
    assert nfa.num_vertices() >= 15 and nfa.num_edges() >= 279

def test_compile_dfa_ipv6():
    dfa = make_dfa_ipv6()
    assert dfa.num_vertices() == 15 and dfa.num_edges() == 279

def test_nfa_dfa_ipv6_correctness():
    for f in [make_nfa_ipv6, make_dfa_ipv6]:
        g = f()
        assert g.accepts("::1")
        assert g.accepts("2a02:a802:23::1")
        assert g.accepts("2a01:e35:2e49:10c0:eeb3:6f16:6bd4:d833")
        assert g.accepts("2A01:E35:2E49:10C0:EEB3:6F16:6BD4:D833")
        assert not g.accepts("2A01:X35:2E49:10C0:EEB3:6F16:6BD4:D833")
        assert not g.accepts(":")
        assert not g.accepts("A")
        assert not g.accepts(":A")
        assert not g.accepts("1")
        assert not g.accepts(":1")
