#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pybgl import (
    DirectedGraph, Graph,
    DefaultTreeTraversalVisitor, dfs_tree, bfs_tree,
    ReadWritePropertyMap, make_assoc_property_map,
)


# This visitor marks for each visited vertex how many vertices
# have been discovered so far.
class MyVisitor(DefaultTreeTraversalVisitor):
    def __init__(
        self,
        pmap_order: ReadWritePropertyMap,
        debug: bool = False
    ):
        super().__init__()
        self.last_index = 0
        self.pmap_order = pmap_order
        self.debug = debug

    def discover_vertex(self, u: int, g: Graph):
        if self.debug:
            print(f"discover_vertex {u}")
        self.pmap_order[u] = self.last_index
        self.last_index += 1


def make_binary_tree(n: int = 10):
    g = DirectedGraph(n)
    for u in range(n - 1):
        g.add_edge(int(u / 2), u + 1)
    return g


def test_bfs_tree():
    map_order = defaultdict()
    pmap_order = make_assoc_property_map(map_order)
    g = make_binary_tree(10)
    vis = MyVisitor(pmap_order)
    bfs_tree(0, g, vis)
    assert map_order == {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
        8: 8,
        9: 9,
    }


def test_dfs_tree():
    map_order = defaultdict()
    pmap_order = make_assoc_property_map(map_order)
    g = make_binary_tree(10)
    vis = MyVisitor(pmap_order)
    dfs_tree(0, g, vis)
    assert map_order == {
        0: 0,
        1: 4,
        2: 1,
        3: 7,
        4: 5,
        5: 3,
        6: 2,
        7: 9,
        8: 8,
        9: 6,
    }
