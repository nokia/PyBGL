#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the PyBGL project.
# https://github.com/nokia/pybgl

import sys
from collections import defaultdict
from .algebra import BinaryRelation, BinaryOperator, Less, ClosedPlus
from .breadth_first_search import DefaultBreadthFirstSearchVisitor
from .graph import Graph, EdgeDescriptor
from .graph_traversal import WHITE, GRAY, BLACK
from .heap import Comparable, Heap
from .property_map import (
    ReadPropertyMap, ReadWritePropertyMap, make_assoc_property_map
)

class DijkstraVisitor:
    """
    The :py:class:`DijkstraVisitor` class is the base class
    for any visitor that can be passed to the
    :py:func:`dijkstra_shortest_path` and
    :py:func:`dijkstra_shortest_paths` functions.
    """
    def initialize_vertex(self, u: int, g: Graph):
        """
        Method invoked on each vertex in the graph before the start of the algorithm.

        Args:
            u (int): The initialized vertex.
            g (Graph): The considered graph.
        """
        pass

    def examine_vertex(self, u: int, g: Graph):
        """
        Method invoked on a vertex as it is removed from the priority queue
        and added to set of vertices to process. At this point, we know that
        (pred[u], u) is a shortest-paths tree edge so
        d[u] = d(s, u) = d[pred[u]] + w(pred[u], u).
        Also, the distances of the examined vertices is monotonically
        increasing d[u1] <= d[u2] <= d[un].

        Args:
            u (int): The examined vertex.
            g (Graph): The considered graph.
        """
        pass

    def examine_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked on each out-edge of a vertex immediately after it has been
        added to set of vertices to process.

        Args:
            e (EdgeDescriptor): The examined edge.
            g (Graph): The considered graph.
        """
        pass

    def discover_vertex(self, u: int, g: Graph):
        """
        Method invoked on vertex ``v`` when an edge ``(u, v)`` is examined
        and ``v`` is :py:data:`WHITE`. Since a vertex is colored :py:data:`GRAY`
        when it is discovered, each reacable vertex is discovered exactly once.
        This is also when the vertex is inserted into the priority queue.

        Args:
            u (int): The discovered vertex.
            g (Graph): The considered graph.
        """
        pass

    def edge_relaxed(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked on edge (u, v) if d[u] + w(u,v) < d[v]. The edge (u, v)
        that participated in the last relaxation for vertex v is an edge in the
        shortest paths tree.

        Args:
            e (EdgeDescriptor): The relaxed edge.
            g (Graph): The considered graph.
        """
        pass

    def edge_not_relaxed(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked if the edge is not relaxed (see above).

        Args:
            e (EdgeDescriptor): The not-relaxed edge.
            g (Graph): The considered graph.
        """
        pass

    def finish_vertex(self, u: int, g: Graph):
        """
        Method invoked on a vertex after all of its out edges have been examined.

        Args:
            u (int): The discovered vertex.
            g (Graph): The considered graph.
        """
        pass

def dijkstra_shortest_paths_initialization(
    g: Graph,
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
    for u in g.vertices():
        pmap_vdist[u] = zero if u == s else infty
        vis.initialize_vertex(u, g)

# Remark:
# Contrary to BGL implementation, we map each vertex with its incident arc*s*
# in the shortest path "tree". This allows to manage parallel arcs and equally
# cost shortest path.

def dijkstra_shortest_paths_iteration(
    heap: Heap,
    g: Graph,
    pmap_eweight: ReadPropertyMap,
    pmap_vpreds: ReadWritePropertyMap,
    pmap_vdist: ReadWritePropertyMap,
    pmap_vcolor: ReadWritePropertyMap,
    compare: BinaryRelation = Less(),  # TODO Ignored, see Heap class.
    combine: BinaryOperator  = ClosedPlus(),
    vis: DijkstraVisitor = DijkstraVisitor()
):
    """
    Implementation function.
    See the :py:func:`dijkstra_shortest_paths` function.
    """
    if vis is None:
        vis = DijkstraVisitor()

    u = heap.pop()
    w_su = pmap_vdist[u]
    vis.examine_vertex(u, g)

    # Update weight and predecessors of each successor of u
    for e in g.out_edges(u):
        vis.examine_edge(e, g)
        v = g.target(e)
        w_sv = pmap_vdist[v]
        w_uv = pmap_eweight[e]
        w = combine(w_su, w_uv)
        if compare(w, w_sv):  # Traversing u is worth!
            pmap_vdist[v] = w
            pmap_vpreds[v] = {e}
            if pmap_vcolor[v] == WHITE:
                heap.push(v)  # As v is WHITE, v cannot be in the heap.
                pmap_vcolor[v] = GRAY
                vis.discover_vertex(v, g)
            elif pmap_vcolor[v] == GRAY:
                heap.decrease_key(v)
            vis.edge_relaxed(e, g)
        elif w == w_sv:  # Hence we discover equally-cost shortest paths
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
    g: Graph,
    s: int,
    pmap_eweight: ReadPropertyMap,
    pmap_vpreds: ReadWritePropertyMap,
    pmap_vdist: ReadWritePropertyMap,
    pmap_vcolor: ReadWritePropertyMap = None,
    compare: BinaryRelation = None,  # TODO Ignored, see Heap class.
    combine: BinaryOperator = ClosedPlus(),
    zero: int = 0,
    infty: int = INFINITY,
    vis: DijkstraVisitor = None
):
    """
    Computes the shortest path in a graph from a given source node
    and according to the `(Distance, compare, combine)` semi-ring
    using the `Dijkstra algorithm <https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm>`__.

    Args:
        g (Graph): The input graph.
        s (int): The vertex descriptor of the source node.
        pmap_eweight (ReadPropertyMap):
            A ``ReadPropertyMap{EdgeDescriptor:  Distance}``
            which map each edge with its weight.
        pmap_vpreds (ReadWritePropertyMap):
            A ``ReadWritePropertyMap{VertexDescriptor:  EdgeDescriptor}``
            which will map each vertex with its incident arcs in the shortest
            path Directed Acyclic Graph.
            Each element must be initially mapped with ``set()``.
        pmap_vdist (ReadWritePropertyMap):
            A ``ReadWritePropertyMap{VertexDescriptor:  Distance}``
            which will map each vertex with the weight of its shortest path(s)
            from ``s``.
            Each element must be initialized to `zero`.
        pmap_vcolor (ReadWritePropertyMap):
            A ``ReadWritePropertyMap{VertexDescriptor:  Distance}``
            which will map each vertex with the weight of its color.
            Each element must be initialized to `WHITE`.
        compare (BinaryRelation): The binary relation that compares two weight.
            This corresponds to the oplus operator in the semi-ring (e.g, min).
        combine (BinaryOperator): The binary relation that combines two weight.
            This corresponds to the otimes operator in the semi-ring (e.g, +).
        zero (float): The null distance (e.g., ``0``).
        infty (float): The infinite distance` (e.g., ``INFINITY``).
        vis (DijkstraVisitor): An optional visitor.

    Example:
        >>> g = Graph(2)
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

# TODO rename to make_shortest_paths_dag
def make_dag(
    g: Graph,
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
        g (Graph): The input graph.
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
        predecessors = {g.source(e) for e in es if e not in done}
        done |= to_process
        to_process = predecessors - done
    return kept_edges

# TODO rename to make_shortest_path
def make_path(
    g: Graph,
    s: int,
    t: int,
    pmap_vpreds: ReadPropertyMap
) -> list:
    """
    Extracts the path from ``s`` to ``t`` in a graph ``g``
    given the predecessors map computed
    using :py:func`dijkstra_shortest_paths` from ``s``.

    Args:
        g (Graph): The input graph.
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

from .aggregated_visitor import AggregatedVisitor

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

    def examine_vertex(self, u: int, g: Graph):
        if u == self.t:
            raise DijkstraStopException(self.t)

def dijkstra_shortest_path(
    g: Graph,
    s: int,
    t: int,
    pmap_eweight: ReadPropertyMap,
    pmap_vpreds: ReadWritePropertyMap,
    pmap_vdist: ReadWritePropertyMap,
    pmap_vcolor: ReadWritePropertyMap = None,
    compare: BinaryRelation = Less(), # TODO Ignored, see Heap class.
    combine: BinaryOperator = ClosedPlus(),
    zero: int = 0,
    infty: int = sys.maxsize,
    vis: DijkstraVisitor = None
) -> list:
    """
    Helper to find a single shortest path from s to t.

    Args:
        g (Graph): The input graph.
        s (int): The vertex descriptor of the source node.
        t (int): The target descriptor of the source node.
        pmap_eweight (ReadPropertyMap):
            A ``ReadPropertyMap{EdgeDescriptor:  Distance}``
            which map each edge with its weight.
        pmap_vpreds (ReadWritePropertyMap):
            A ``ReadWritePropertyMap{VertexDescriptor:  EdgeDescriptor}``
            which will map each vertex with its incident arcs in the shortest
            path Directed Acyclic Graph.
            Each element must be initially mapped with ``set()``.
        pmap_vdist (ReadWritePropertyMap):
            A ``ReadWritePropertyMap{VertexDescriptor:  Distance}``
            which will map each vertex with the weight of its shortest path(s)
            from ``s``.
            Each element must be initialized to `zero`.
        pmap_vcolor (ReadWritePropertyMap):
            A ``ReadWritePropertyMap{VertexDescriptor:  Distance}``
            which will map each vertex with the weight of its color.
            Each element must be initialized to `WHITE`.
        compare (BinaryRelation): The binary relation that compares two weight.
            This corresponds to the oplus operator in the semi-ring (e.g, min).
        combine (BinaryOperator): The binary relation that combines two weight.
            This corresponds to the otimes operator in the semi-ring (e.g, +).
        zero (float): The null distance (e.g., ``0``).
        infty (float): The infinite distance` (e.g., ``INFINITY``).
        vis (DijkstraVisitor): An optional visitor.
    """
    vis_towards = DijkstraTowardsVisitor(t)
    vis = AggregatedVisitor([vis, vis_towards]) if vis else vis_towards
    try:
        dijkstra_shortest_paths(
            g, s,
            pmap_eweight, pmap_vpreds, pmap_vdist, pmap_vcolor,
            compare, combine, zero, infty,
            vis=vis
        )
    except DijkstraStopException:
        return make_path(g, s, t, pmap_vpreds)
    return None
