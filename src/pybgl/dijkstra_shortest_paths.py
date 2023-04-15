#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the PyBGL project.
# https://github.com/nokia/pybgl

import sys
from collections import defaultdict
from .algebra import BinaryFunction, BinaryPredicate, Less, ClosedPlus
from .breadth_first_search import DefaultBreadthFirstSearchVisitor
from .graph import (
    DirectedGraph, EdgeDescriptor, source, target, out_edges, vertices
)
from .graph_traversal import WHITE, GRAY, BLACK
from .heap import Comparable, Heap
from .property_map import (
    ReadPropertyMap, ReadWritePropertyMap, make_assoc_property_map
)

class DijkstraVisitor:
    def initialize_vertex(self, u: int, g: DirectedGraph):
        pass

    def examine_vertex(self, u: int, g: DirectedGraph):
        pass

    def examine_edge(self, e: EdgeDescriptor, g: DirectedGraph):
        pass

    def discover_vertex(self, u: int, g: DirectedGraph):
        pass

    def edge_relaxed(self, e: EdgeDescriptor, g: DirectedGraph):
        pass

    def edge_not_relaxed(self, e: EdgeDescriptor, g: DirectedGraph):
        pass

    def finish_vertex(self, u: int, g: DirectedGraph):
        pass

class DijkstraDebugVisitor(DijkstraVisitor):
    def initialize_vertex(self, u: int, g: DirectedGraph):
        print(f"initialize_vertex({u})")

    def examine_vertex(self, u: int, g: DirectedGraph):
        print(f"examine_vertex({u})")

    def examine_edge(self, e: EdgeDescriptor, g: DirectedGraph):
        print(f"examine_edge({e} {e.m_distinguisher})")

    def discover_vertex(self, u: int, g: DirectedGraph):
        print(f"discover_vertex({u})")

    def edge_relaxed(self, e: EdgeDescriptor, g: DirectedGraph):
        print(f"edge_relaxed({e}  {e.m_distinguisher})")

    def edge_not_relaxed(self, e: EdgeDescriptor, g: DirectedGraph):
        print(f"edge_not_relaxed({e}  {e.m_distinguisher})")

    def finish_vertex(self, u: int, g: DirectedGraph):
        print(f"finish_vertex({u})")

def dijkstra_shortest_paths_initialization(
    g: DirectedGraph,
    s: int,
    pmap_vcolor: ReadWritePropertyMap,
    pmap_vdist: ReadWritePropertyMap,
    zero: int,
    infty: int,
    vis: DijkstraVisitor = None
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
    heap        : Heap,
    g           : DirectedGraph,
    pmap_eweight: ReadPropertyMap,
    pmap_vpreds : ReadWritePropertyMap,
    pmap_vdist  : ReadWritePropertyMap,
    pmap_vcolor : ReadWritePropertyMap,
    compare     : BinaryPredicate = Less(), # Ignored, see Heap class.
    combine     : BinaryFunction  = ClosedPlus(),
    vis         : DijkstraVisitor = DijkstraVisitor()
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
    g: DirectedGraph,
    s: int,
    pmap_eweight: ReadPropertyMap,
    pmap_vpreds: ReadWritePropertyMap,
    pmap_vdist: ReadWritePropertyMap,
    pmap_vcolor: ReadWritePropertyMap = None,
    compare: BinaryPredicate = None, # Ignored, see Heap class.
    combine: BinaryFunction  = ClosedPlus(),
    zero: int = 0,
    infty: int = INFINITY,
    vis: DijkstraVisitor = None
):
    """
    Computes the shortest path in a graph from a given source node
    and according to the `(Distance, compare, combine)` semi-ring
    using the `Dijkstra algorithm <https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm>`__.

    Args:
        g (DirectedGraph): The input graph.
        s (int): The vertex descriptor of the source node.
        pmap_eweight (ReadPropertyMap):
            A ``ReadPropertyMap{EdgeDescriptor:  Distance}``
            which map each edge with its weight.
        pmap_vpreds (ReadWritePropertyMap):
            A ``ReadWritePropertyMap{VertexDescriptor:  EdgeDescriptor}``
            which will map each vertex with its incident arcs in the shortest
            path Directed Acyclic Graph.
            Each element must be initially mapped with ``set()``.
        pmap_vdist: A ``ReadWritePropertyMap{VertexDescriptor:  Distance}``
            which will map each vertex with the weight of its shortest path(s)
            from ``s``.
            Each element must be initialized to `zero`.
        zero (float): The null distance (e.g., ``0``).
        infty (float): The infinite distance` (e.g., ``INFINITY``).
        vis (DijkstraVisitor): An optional visitor.

    Example:
        >>> g = DirectedGraph(2)
        >>> e, _ = add_edge(0, 1, g)
        >>> map_eweight[e] = 10
        >>> map_vpreds = defaultdict(set)
        >>> map_vdist = dict()
        >>> dijkstra_shortest_paths(
        ...    g, u,
        ...    make_assoc_property_map(map_eweight),
        ...    make_assoc_property_map(map_vpreds),
        ...    make_assoc_property_map(map_vdist)
        ... )
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
    g: DirectedGraph,
    s: int,
    t: int,
    pmap_vpreds: ReadPropertyMap,
    single_path: bool = False
) -> set:
    """
    Extracts the set of arcs related to shortest paths from ``s``
    to ``t`` in a graph ``g`` given the predecessors map computed
    using :py:func:`dijkstra_shortest_paths` from ``s``.
    The corresponding subgraph is a DAG where the source is ``s`` and
    the sink is ``t``.

    Args:
        g (DirectedGraph): The input graph.
        s (int): The source vertex descriptor.
        t (int): The target vertex descriptor.
        pmap_vpreds (ReadPropertyMap): The
            ``ReadPropertyMap{int:  set(int)}`` mapping each
            vertex with its set of (direct) predecessors.
        single_path (bool): Pass ``True`` to extract an arbitrary
            single shortest path, ``False`` to extrac of all them.
            Note that if ``single_path is True`` and if multiple
            paths exist from ``s`` to ``t``, :py:func:`make_dag`
            extracts an arbitrary shortest path instead of all of them.

    Returns:
        The corresponding set of arcs.
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
    g: DirectedGraph,
    s: int,
    t: int,
    pmap_vpreds: ReadPropertyMap
) -> list:
    """
    Extracts the path from ``s`` to ``t`` in a graph ``g``
    given the predecessors map computed
    using :py:func`dijkstra_shortest_paths` from ``s``.

    Args:
        g (DirectedGraph): The input graph.
        s (int): The target's vertex descriptor.
        t (int): The target's vertex descriptor.
        pmap_vpreds (ReadPropertyMap):
            A ``ReadPropertyMap{int:  set(int)}`` mapping each
            vertex with its set of (direct) predecessors.

    Returns:
        A list of consecutive arcs forming a shortest path from ``s`` of ``t``.
        If several shortest paths exist from ``s`` to ``t``, this function returns
        an arbitrary shortest path.
    """
    arcs = make_dag(g, s, t, pmap_vpreds, single_path=True)
    u = t
    path = list()
    while u != s:
        e = list(pmap_vpreds[u])[0]
        path.insert(0, e)
        u = g.source(e)
    return path

#--------------------------------------------------------------------
# Optimization to stop Dijkstra iteration once distance from s to t
#--------------------------------------------------------------------

from pybgl.aggregated_visitor import AggregatedVisitor

class DijkstraStopException(Exception):
    pass

class DijkstraTowardsVisitor(DijkstraVisitor):
    """
    The :py:class:`DijkstraTowardsVisitor` may be passed to
    the :py:func:`dijkstra_shortest_paths` function
    to abort computation once the cost of the shortest path to ``t`` is
    definitely known.

    Important notes:

    - stopping when discovering ``t`` (the first time) does not guarantee
      that we have find the shortest path towards ``t``. We must
      wait the :py:meth:`DijkstraVisitor.examine_vertex` method to be
      triggered.
    - stopping when discovering a vertex ``u`` farther than ``t`` from ``s``
      always occurs after finishing vertex ``t``.

    As a sequel, we must wait that ``t`` is examined to guarantee that a
    a shortest path to t has been explored.
    """
    def __init__(self, t: int):
        self.t = t

    def examine_vertex(self, u: int, g: DirectedGraph):
        if u == self.t:
            raise DijkstraStopException(self.t)

def dijkstra_shortest_path(
    g: DirectedGraph,
    s: int,
    t: int,
    pmap_eweight: ReadPropertyMap,
    pmap_vpreds: ReadWritePropertyMap,
    pmap_vdist: ReadWritePropertyMap,
    pmap_vcolor: ReadWritePropertyMap = None,
    compare: BinaryPredicate = Less(), # Ignored, see Heap class.
    combine: BinaryFunction  = ClosedPlus(),
    zero: int = 0,
    infty: int = sys.maxsize,
    vis: DijkstraVisitor = None
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
