#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.automaton    import accepts
from pybgl.graph        import num_edges, num_vertices
from pybgl.ipynb        import in_ipynb, ipynb_display_graph
from pybgl.regexp       import compile_nfa, compile_dfa

if in_ipynb():
    display_graph = ipynb_display_graph if in_ipynb
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
        assert accepts("::1", g) == True
        assert accepts("2a02:a802:23::1", g) == True
        assert accepts("2a01:e35:2e49:10c0:eeb3:6f16:6bd4:d833", g) == True
        assert accepts("2A01:E35:2E49:10C0:EEB3:6F16:6BD4:D833", g) == True
        assert accepts("2A01:X35:2E49:10C0:EEB3:6F16:6BD4:D833", g) == False
        assert accepts(":", g) == False
        assert accepts("A", g) == False
        assert accepts(":A", g) == False
        assert accepts("1", g) == False
        assert accepts(":1", g) == False
