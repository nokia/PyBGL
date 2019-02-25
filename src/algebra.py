#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

import sys

class BinaryPredicate:
    pass

class Less(BinaryPredicate):
    def __call__(self, x, y) -> bool:
        return x < y

class GreaterThan(BinaryPredicate):
    def __call__(self, x, y) -> bool:
        return x > y

class BinaryFunction:
    pass

class ClosedOperator(BinaryFunction):
    def __init__(self, infty):
        self.infty = infty
    def impl(self, x, y):
        raise NotImplemented
    def __call__(self, x, y):
        return self.infty if x == self.infty or y == self.infty else self.impl(x, y)

class ClosedPlus(ClosedOperator):
    def __init__(self, infty = sys.maxsize):
        super().__init__(infty)
    def impl(self, x, y):
        return x + y

class ClosedTime(ClosedOperator):
    def __init__(self, infty = sys.maxsize):
        super().__init__(infty)
    def impl(self, x, y):
        return x * y
    
class ClosedMax(ClosedOperator):
    def __init__(self, infty = sys.maxsize):
        super().__init__(infty)
    def impl(self, x, y):
        return max(x, y)
    
class ClosedMin(ClosedOperator):
    def __init__(self, infty = sys.maxsize):
        super().__init__(infty)
    def impl(self, x, y):
        return min(x, y)
