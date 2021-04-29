#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

import sys
from collections                import defaultdict
from pybgl.algebra              import BinaryFunction, BinaryPredicate, Less, ClosedPlus
from pybgl.breadth_first_search import DefaultBreadthFirstSearchVisitor
from pybgl.graph                import (
    DirectedGraph, EdgeDescriptor, source, target, out_edges, vertices
)
from pybgl.graph_traversal      import WHITE, GRAY, BLACK
from pybgl.heap                 import Comparable, Heap
from pybgl.property_map         import (
    ReadPropertyMap, ReadWritePropertyMap, make_assoc_property_map
)

class DijkstraVisitor:
    def initialize_vertex(self, u :int, g :DirectedGraph): pass
    def examine_vertex(self, u :int, g :DirectedGraph): pass
    def examine_edge(self, e :EdgeDescriptor, g :DirectedGraph): pass
    def discover_vertex(self, u :int, g :DirectedGraph): pass
    def edge_relaxed(self, e :EdgeDescriptor, g :DirectedGraph): pass
    def edge_not_relaxed(self, e :EdgeDescriptor, g :DirectedGraph): pass
    def finish_vertex(self, u :int, g :DirectedGraph): pass

class DijkstraDebugVisitor(DijkstraVisitor):
    def initialize_vertex(self, u :int, g :DirectedGraph):
        print(f"initialize_vertex({u})")
    def examine_vertex(self, u :int, g :DirectedGraph):
        print(f"examine_vertex({u})")
    def examine_edge(self, e :EdgeDescriptor, g :DirectedGraph):
        print(f"examine_edge({e} {e.m_distinguisher})")
    def discover_vertex(self, u :int, g :DirectedGraph):
        print(f"discover_vertex({u})")
    def edge_relaxed(self, e :EdgeDescriptor, g :DirectedGraph):
        print(f"edge_relaxed({e}  {e.m_distinguisher})")
    def edge_not_relaxed(self, e :EdgeDescriptor, g :DirectedGraph):
        print(f"edge_not_relaxed({e}  {e.m_distinguisher})")
    def finish_vertex(self, u :int, g :DirectedGraph):
        print(f"finish_vertex({u})")

def dijkstra_shortest_paths_initialization(
    g           :DirectedGraph,
    s           :int,
    pmap_vcolor :ReadWritePropertyMap,
    pmap_vdist  :ReadWritePropertyMap,
    zero        :int,
    infty       :int,
    vis         :DijkstraVisitor = None
):
    if vis is None:
        vis = DijkstraVisitor()

    # WHITE: not yet processed, GRAY: under process, BLACK: processed.
    pmap_vcolor[s] = WHITE
    for u in vertices(g):
        pmap_vdist[u] = zero if u == s else infty
        vis.initialize_vertex(u, g)

# Remark:
# Contrary to BGL implementation, we map each vertex with its incident arc*s*
# in the shortest path "tree". This allows to manage parallel arcs and equally
# cost shortest path.

def dijkstra_shortest_paths_iteration(
    heap         :Heap,
    g            :DirectedGraph,
    pmap_eweight :ReadPropertyMap,
    pmap_vpreds  :ReadWritePropertyMap,
    pmap_vdist   :ReadWritePropertyMap,
    pmap_vcolor  :ReadWritePropertyMap,
    compare      :BinaryPredicate = Less(), # Ignored, see Heap class.
    combine      :BinaryFunction  = ClosedPlus(),
    vis          :DijkstraVisitor = DijkstraVisitor()
):
    if vis is None:
        vis = DijkstraVisitor()

    u = heap.pop()
    w_su = pmap_vdist[u]
    vis.examine_vertex(u, g)

    # Update weight and predecessors of each successor of u
    for e in out_edges(u, g):
        vis.examine_edge(e, g)
        v = target(e, g)
        w_sv = pmap_vdist[v]
        w_uv = pmap_eweight[e]
        w = combine(w_su, w_uv)
        if compare(w, w_sv): # Traversing u is worth!
            pmap_vdist[v] = w
            pmap_vpreds[v] = {e}
            if pmap_vcolor[v] == WHITE:
                heap.push(v) # As v is WHITE, v cannot be in the heap.
                pmap_vcolor[v] = GRAY
                vis.discover_vertex(v, g)
            elif pmap_vcolor[v] == GRAY:
                heap.decrease_key(v)
            vis.edge_relaxed(e, g)
        elif w == w_sv: # Hence we discover equally-cost shortest paths
            preds_v = pmap_vpreds[v]
            preds_v.add(e)
            pmap_vpreds[v] = preds_v
            vis.edge_relaxed(e, g)
        else:
            vis.edge_not_relaxed(e, g)
    pmap_vcolor[u] = BLACK
    vis.finish_vertex(u, g)
    return w_su

INFINITY = sys.maxsize

def dijkstra_shortest_paths(
    g            :DirectedGraph,
    s            :int,
    pmap_eweight :ReadPropertyMap,
    pmap_vpreds  :ReadWritePropertyMap,
    pmap_vdist   :ReadWritePropertyMap,
    pmap_vcolor  :ReadWritePropertyMap = None,
    compare      :BinaryPredicate = None, # Ignored, see Heap class.
    combine      :BinaryFunction  = ClosedPlus(),
    zero         :int = 0,
    infty        :int = INFINITY,
    vis          :DijkstraVisitor = None
):
    """
    Compute the shortest path in a graph from a given source node
    and according to the `(Distance, compare, combine)` semi-ring.
    Args:
        g: A `DirectedGraph` instance.
        s: The vertex descriptor of the source node.
        pmap_eweight: A `ReadPropertyMap{EdgeDescriptor : Distance}`
            which map each edge with its weight.
        pmap_vpreds: A `ReadWritePropertyMap{VertexDescriptor : EdgeDescriptor}`
            which will map each vertex with its incident arcs in the shortest
            path Directed Acyclic Graph.
            Each element must be initially mapped with `set()`.
        pmap_vdist: A `ReadWritePropertyMap{VertexDescriptor : Distance}`
            which will map each vertex with the weight of its shortest path(s)
            from `s`.
            Each element must be initialized to `zero`.
        zero: The null `Distance` (e.g. `0`).
        infty: The infinite `Distance` (e.g. `sys.maxsize`).
        vis: A `DijkstraVisitor` instance.

    Example:
        g = DirectedGraph(2)
        e, _ = add_edge(0, 1, g)
        map_eweight[e] = 10
        map_vpreds = defaultdict(set)
        map_vdist = dict()
        dijkstra_shortest_paths(
            g, u,
            make_assoc_property_map(map_eweight),
            make_assoc_property_map(map_vpreds),
            make_assoc_property_map(map_vdist)
        )
    """
    if vis is None:
        vis = DijkstraVisitor()

    if pmap_vcolor is None:
        color = defaultdict(int)
        pmap_vcolor = make_assoc_property_map(color)

    # Initialization
    dijkstra_shortest_paths_initialization(
        g, s, pmap_vcolor,
        pmap_vdist, zero, infty, vis
    )

    # Iteration
    if not compare:
        compare = Less()
        heap = Heap([s], to_comparable = lambda u: pmap_vdist[u])
    else:
        heap = Heap(
            [s],
            to_comparable = lambda u: Comparable(pmap_vdist[u], compare)
        )

    while heap:
        dijkstra_shortest_paths_iteration(
            heap, g,
            pmap_eweight,
            pmap_vpreds, pmap_vdist, pmap_vcolor,
            compare, combine, vis
        )

#--------------------------------------------------------------------
# Utilities to get the Shortest-Paths-DAG or an arbitary shortest
# path towards an arbitrary node t.
#--------------------------------------------------------------------

def make_dag(
    g :DirectedGraph,
    s :int,
    t :int,
    pmap_vpreds :ReadPropertyMap,
    single_path :bool = False
) -> set:
    """
    Extracts the arcs related to shortest paths from `s`
    to `t` in a graph `g` given the predecessors map computed
    using `dijkstra_shortest_paths` from `s`.
    Args:
        g: The graph.
        s: The target's vertex descriptor.
        t: The target's vertex descriptor.
        pmap_vpreds: The `ReadPropertyMap{int : set(int)}` mapping each
            vertex with its set of (direct) predecessors.
        single_path: Pass True to extract a single path. If multiple
            paths exist from `s` to `t`, this extracts an arbitrary
            path instead of all of them.
    Returns:
        The corresponding set of `EdgeDescriptor`s.
    """
    kept_edges = set()
    n_prev = -1
    n = 0
    to_process = {t}
    done = set()
    while to_process:
        es = {e for u in to_process if pmap_vpreds[u] for e in pmap_vpreds[u]}
        if single_path and es:
            es = {es.pop()}
        kept_edges |= es
        predecessors = {source(e, g) for e in es if e not in done}
        done |= to_process
        to_process = predecessors - done
    return kept_edges

def make_path(
    g :DirectedGraph,
    s :int,
    t :int,
    pmap_vpreds :ReadPropertyMap
) -> list:
    """
    Extract the path from `s` to `t` in a graph `g` gien
    to `t` in a graph `g` given the predecessors map computed
    using `dijkstra_shortest_paths` from `s`.
    Args:
        g: The graph.
        s: The target's vertex descriptor.
        t: The target's vertex descriptor.
        pmap_vpreds: A `ReadPropertyMap{int : set(int)}` mapping each
            vertex with its set of (direct) predecessors.
    Returns:
        A list of consecutive arcs forming a shortest path from `s` of `t`.
        If several shortest paths exist from `s` to `t`, this function returns
        an arbitrary path.
    """
    arcs = make_dag(g, s, t, pmap_vpreds, single_path=True)
    path = list(arcs)
    path.sort(key=lambda e: (source(e, g), target(e, g)))
    return path

#--------------------------------------------------------------------
# Optimization to stop Dijkstra iteration once distance from s to t
#--------------------------------------------------------------------

from pybgl.aggregated_visitor import AggregatedVisitor

class DijkstraStopException(Exception):
    pass

class DijkstraTowardsVisitor(DijkstraVisitor):
    """
    `DijkstraTowardsVisitor` can be passed to `dijkstra_shortest_paths`
    to abort computation once the cost of the shortest path to `t` is
    known.

    Important notes:
    - stopping when discovering t does not guarantee that we have find
    the shortest path.
    - stopping when discovering a vertex u farther than t from s always
    occur after finishing vertex t.

    As a sequel, we must wait that t is examined to guarantee that a
    a shortest path to t has been explored.
    """
    def __init__(self, t :int):
        self.t = t

    def examine_vertex(self, u :int, g :DirectedGraph):
        if u == self.t:
            raise DijkstraStopException(self.t)

def dijkstra_shortest_path(
    g            :DirectedGraph,
    s            :int,
    t            :int,
    pmap_eweight :ReadPropertyMap,
    pmap_vpreds  :ReadWritePropertyMap,
    pmap_vdist   :ReadWritePropertyMap,
    pmap_vcolor  :ReadWritePropertyMap = None,
    compare      :BinaryPredicate = Less(), # Ignored, see Heap class.
    combine      :BinaryFunction  = ClosedPlus(),
    zero         :int = 0,
    infty        :int = sys.maxsize,
    vis          :DijkstraVisitor = None
) -> list:
    """
    Helper to find a single shortest path from s to t.
    """
    vis_towards = DijkstraTowardsVisitor(t)
    vis = AggregatedVisitor([vis, vis_towards]) if vis else vis_towards
    try:
        dijkstra_shortest_paths(
            g, s,
            pmap_eweight, pmap_vpreds, pmap_vdist, pmap_vcolor,
            compare, combine, zero, infty,
            vis = vis
        )
    except DijkstraStopException:
        return make_path(g, s, t, pmap_vpreds)
    return None
