#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

import heapq
from pybgl import Comparable, Heap, compare_to_key


def le(a, b):
    return a <= b


def ge(a, b):
    return a >= b


def test_comparable_le():
    one1 = Comparable(1, le)
    two = Comparable(2, le)
    assert one1 != two
    assert one1 < two
    assert one1 <= two
    assert two > one1
    assert two >= one1

    one2 = Comparable(1, le)
    assert one1 == one2
    assert one1 <= one2
    assert not one1 < one2
    assert one1 >= one2
    assert not one1 > one2
    assert not one1 != one2


def test_comparable_le_list_to_heap():
    values = [2, 1, 1, 3]
    comparables = [Comparable(x, le) for x in values]
    heapq.heapify(comparables)
    assert [x.obj for x in comparables] == [1, 1, 2, 3]


def test_comparable_ge():
    one1 = Comparable(1, ge)
    two = Comparable(2, ge)
    assert one1 != two
    assert one1 > two
    assert one1 >= two
    assert two < one1
    assert two <= one1

    one2 = Comparable(1, ge)
    assert one1 == one2
    assert one1 >= one2
    assert not one1 > one2
    assert one1 <= one2
    assert not one1 > one2
    assert not one1 != one2


def test_comparable_ge_list_to_heap():
    values = [2, 1, 1, 3]
    comparables = [Comparable(x, ge) for x in values]
    heapq.heapify(comparables)
    assert [x.obj for x in comparables] == [3, 2, 1, 1]


def test_heap_empty():
    h1 = Heap()
    assert list(h1) == list()
    assert not h1


def test_heap_le(debug: bool = False):
    if not debug:
        def print(*args, **kwargs):
            pass
    h = Heap([2, 1, 1, 3], lambda u: Comparable(u, le))
    print(h)
    assert h
    assert len(h) == 4
    assert list(h) == [1, 1, 2, 3]
    h.push(4)
    print(h)
    assert list(h) == [1, 1, 2, 3, 4]
    h.push(0)
    print(h)
    assert list(h) == [0, 1, 1, 2, 3, 4]
    x = h.pop()
    print(h)
    assert x == 0
    y = h.pop()
    print(h)
    assert y == 1
    assert list(h) == [1, 2, 3, 4]


def test_heap_ge(debug: bool = False):
    if not debug:
        def print(*args, **kwargs):
            pass
    h = Heap([2, 1, 1, 3], lambda u: Comparable(u, ge))
    print(h)
    assert h
    assert len(h) == 4
    assert list(h) == [3, 2, 1, 1]
    h.push(4)
    print(h)
    assert list(h) == [4, 3, 2, 1, 1]
    h.push(0)
    print(h)
    assert list(h) == [4, 3, 2, 1, 1, 0]
    x = h.pop()
    print(h)
    assert x == 4
    y = h.pop()
    print(h)
    assert y == 3
    assert list(h) == [2, 1, 1, 0]


def test_heap():
    h = Heap(
        [2, 1, 1, 3],
        lambda u: Comparable(u, le)
    )
    values = [h.pop() for _ in range(len(h))]
    assert values == [1, 1, 2, 3]
    assert len(h) == 0
    h.push(4)
    h.push(5)
    assert list(h) == [4, 5]


def test_heapq_compare_to_key():
    h = Heap(
        [1, 3, 4, 1, 2],
        compare_to_key(lambda a, b: a >= b)
    )
    assert list(h) == [4, 3, 2, 1, 1]
    h.push(2)
    assert list(h) == [4, 3, 2, 2, 1, 1]
    x = h.pop()
    assert x == 4
    assert list(h) == [3, 2, 2, 1, 1]
