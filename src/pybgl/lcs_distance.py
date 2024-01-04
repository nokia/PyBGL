#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

def lcs_distance_naive(x: str, y: str) -> int:
    """
    Inefficient implementation of the
    `LCS (Longest Common Substring) distance
    <https://en.wikipedia.org/wiki/Longest_common_subsequence>`__
    (no memoization).

    Args:
        x (str): The left operand.
        y (str): The right operand.

    Returns:
        The minimal number of insertion/deletion operations needed to
        transform ``x`` into ``y``.
    """
    x_1 = x[1:]
    y_1 = y[1:]
    return (
        len(x) if not y else
        len(y) if not x else
        lcs_distance(x_1, y_1) if x[0] == y[0] else
        1 + min(
            lcs_distance(x_1, y),
            lcs_distance(x, y_1)
        )
    )


class LcsDistance:
    """
    The :py:class:`LcsDistance` class is used to implement the memoization
    used by the :py:func:`lcs_distance` function.
    """
    def __init__(self, x: str, y: str):
        """
        Constructor.

        Args:
            x (str): The left operand.
            y (str): The right operand.
        """
        self.memoize = dict()
        self.x = x
        self.y = y

    def compute(self, i: int = 0, j: int = 0) -> int:
        """
        Computes the `LCS (Longest Common Substring) distance
        <https://en.wikipedia.org/wiki/Longest_common_subsequence>`__,
        with memoization.

        Args:
            i (int): The current index in ``self.x``.
            j (int): The current index in ``self.y``.

        Returns:
            The minimal number of insertion/deletion operations needed to
            transform ``x`` into ``y``.
        """
        ret = self.memoize.get((i, j))
        if ret is None:
            ret = self.memoize[(i, j)] = (
                len(self.x) - i if not j < len(self.y) else
                len(self.y) - j if not i < len(self.x) else
                self.compute(i + 1, j + 1) if self.x[i] == self.y[j] else
                1 + min(
                    self.compute(i + 1, j),
                    self.compute(i, j + 1),
                )
            )
        return ret


def lcs_distance(x: str, y: str) -> int:
    """
    Computes the `LCS (Longest Common Substring) distance
    <https://en.wikipedia.org/wiki/Longest_common_subsequence>`__,
    with memoization.

    Args:
        x (str): The left operand.
        y (str): The right operand.

    Returns:
        The minimal number of insertion/deletion substitution operations
        needed to transform ``x`` into ``y``.
    """
    return LcsDistance(x, y).compute(0, 0)
