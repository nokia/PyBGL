#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.automaton import \
    BOTTOM, Automaton, EdgeDescriptor, \
    add_edge, add_vertex, delta, \
    initial, is_initial, is_final, label, set_initial, set_final, source, target

class ProductMixin:
    def __init__(self, g12 :Automaton, operator):
        self.map_product_vertices = dict()
        self.g12 = g12
        self.operator = operator

    def add_product_vertex(self, q1 :int, g1 :Automaton, q2 :int, g2 :Automaton) -> int:
        q12 = add_vertex(self.g12)
        if self.operator(is_initial(q1, g1), is_initial(q2, g2)):
            set_initial(q12, self.g12)
        if self.operator(is_final(q1, g1), is_final(q2, g2)):
            set_final(q12, self.g12)
        self.map_product_vertices[(q1, q2)] = q12
        return q12

    def add_product_edge(self, e1 :EdgeDescriptor, g1 :Automaton, e2 :EdgeDescriptor, g2 :Automaton):
        if e1:
            q1 = source(e1, g1)
            r1 = target(e1, g1)
            a = label(e1, g1)
        else:
            q1 = r1 = BOTTOM

        if e2:
            q2 = source(e2, g2)
            r2 = target(e2, g2)
            a = label(e2, g2)
        else:
            q2 = r2 = BOTTOM

        q12 = self.get_or_create_product_vertex(q1, g1, q2, g2)
        r12 = self.get_or_create_product_vertex(r1, g1, r2, g2)
        return add_edge(q12, r12, a, self.g12)

    def get_product_vertex(self, q1 :int, q2 :int) -> int:
        return self.map_product_vertices.get((q1, q2))

    def get_or_create_product_vertex(self, q1 :int, g1 :Automaton, q2 :int, g2 :Automaton) -> int:
        if q1 is BOTTOM and q2 is BOTTOM:
            raise RuntimeError("Tried to create (BOTTOM, BOTTOM) state.")
        q12 = self.get_product_vertex(q1, q2)
        if q12 is None:
            q12 = self.add_product_vertex(q1, g1, q2, g2)
        return q12

