#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.graphviz    import graph_to_html
from pybgl.html        import html
from pybgl.ipynb       import in_ipynb
from pybgl.matching    import matching
from pybgl.trie        import Trie

def test_matching_tries():
    both = {"an", "banana"}
    only1 = {"ananas", "x", "y", "z"}
    only2 = {"bananas", "bank", "t"}
    corpus1 = both | only1
    corpus2 = both | only2

    t1 = Trie()
    for w in corpus1:
        t1.insert(w)

    t2 = Trie()
    for w in corpus2:
        t2.insert(w)

    if in_ipynb():
        html(graph_to_html(t1))
        html(graph_to_html(t2))

    l = matching(t1, t2)
    assert l[1] == len(only1)
    assert l[2] == len(only2)
    assert l[3] == len(both)
