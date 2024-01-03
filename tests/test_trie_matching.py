#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    Trie,
    graph_to_html,
    html,
    in_ipynb,
    trie_matching,
)


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

    ret = trie_matching(t1, t2)
    assert ret[1] == len(only1)
    assert ret[2] == len(only2)
    assert ret[3] == len(both)
