#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

from pybgl.graph import UndirectedGraph, add_vertex, add_edge, edges, in_degree, in_edges, num_edges, num_vertices, out_degree, out_edges, remove_edge, remove_vertex

g = UndirectedGraph()

assert num_vertices(g) == 0
u = add_vertex(g)
assert num_vertices(g) == 1
v = add_vertex(g)
assert num_vertices(g) == 2
w = add_vertex(g)
assert num_vertices(g) == 3

assert num_edges(g) == 0
e_uv,  _ = add_edge(u, v, g)
assert num_edges(g) == 1
e_uv1, _ = add_edge(v, u, g)
assert num_edges(g) == 2
e_uw,  _ = add_edge(u, w, g)
assert num_edges(g) == 3
e_vw,  _ = add_edge(v, w, g)
assert num_edges(g) == 4

print("Edges = %s" % {e for e in edges(g)})

print("In-edges(%s) = %s" % (u, {e for e in in_edges(u, g)}))
assert in_degree(u, g) == 3
assert in_degree(v, g) == 3
assert in_degree(w, g) == 2, "in_edges(%s) = %s" % (w, {u for u in in_edges(w, g)})

print("Out-edges(%s) = %s" % (u, {e for e in out_edges(u, g)}))
assert out_degree(u, g) == 3
assert out_degree(v, g) == 3
assert out_degree(w, g) == 2

print("Removing %s" % e_uv)
remove_edge(e_uv, g)
assert num_edges(g) == 3

print("Removing %s" % e_uv1)
remove_edge(e_uv1, g)
assert num_edges(g) == 2

print("Removing %s" % v)
remove_vertex(v, g)
assert num_vertices(g) == 2

print("Edges = %s" % {e for e in edges(g)})
assert num_edges(g) == 1

print("Out-edges(%s) = %s" % (u, {e for e in out_edges(u, g)}))
assert out_degree(u, g) == 1
assert out_degree(w, g) == 1
assert in_degree(u, g) == 1
assert in_degree(w, g) == 1

print(g.to_dot())
