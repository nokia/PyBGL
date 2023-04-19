#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

def damerau_levenshtein_distance_naive(x: str, y: str) -> int:
    """
    Inefficient implementation of the
    `Damerau Levenshtein distance <https://en.wikipedia.org/wiki/Damerau–Levenshtein_distance>`__
    (no memoization).
    Prefer the :py:func:`damerau_levenshtein_distance` function.

    Args:
        x (str): The left operand.
        y (str): The right operand.

    Returns:
        The minimal number of insertion/deletion/substitution/swap operations needed to
        transform `x` into `y`.
    """
    x_1 = x[1:]
    y_1 = y[1:]
    return (
        len(x) if not y else
        len(y) if not x else
        damerau_levenshtein_distance_naive(x_1, y_1) if x[0] == y[0] else
        1 + min(
            [
                damerau_levenshtein_distance_naive(x_1, y),
                damerau_levenshtein_distance_naive(x, y_1),
                damerau_levenshtein_distance_naive(x_1, y_1),
            ] + (
                [damerau_levenshtein_distance_naive(x[2:], y[2:])] if (
                    len(x) >= 2
                    and len(y) >= 2
                    and x[0] == y[1]
                    and x[1] == y[0]
                ) else []
            )
        )
    )

class DamerauLevenshteinDistance:
    """
    The :py:class:`DamerauLevenshteinDistance` class is used to implement the memoization
    used by the :py:func:`damerau_levenshtein_distance_naive` function.
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
        Computes the
        `Damerau Levenshtein distance <https://en.wikipedia.org/wiki/Damerau–Levenshtein_distance>`__,
        with memoization.

        Args:
            i (int): The current index in ``self.x``.
            j (int): The current index in ``self.y``.

        Returns:
            The minimal number of insertion/deletion/substitution/swap operations needed to
            transform ``x`` into ``y``.
        """

        ret = self.memoize.get((i, j))
        if ret is None:
            ret = self.memoize[(i, j)] = (
                len(self.x) - i if not j < len(self.y) else
                len(self.y) - j if not i < len(self.x) else
                self.compute(i + 1, j + 1) if self.x[i] == self.y[j] else
                1 + min(
                    [
                        self.compute(i + 1, j),
                        self.compute(i, j + 1),
                        self.compute(i + 1, j + 1)
                    ] + (
                        [self.compute(i + 2, j + 2)] if (
                            i + 1 < len(self.x) and j + 1 < len(self.y)
                            and self.x[i] == self.y[j + 1]
                            and self.x[i + 1] == self.y[j]
                        ) else []
                    )
                )
            )
        return ret

def damerau_levenshtein_distance(x: str, y: str) -> int:
    """
    Computes the
    `Damerau Levenshtein distance <https://en.wikipedia.org/wiki/Damerau–Levenshtein_distance>`__,
    with memoization.

    Args:
        x (str): The left operand.
        y (str): The right operand.

    Returns:
        The minimal number of insertion/deletion/substitution/swap operations needed to
        transform `x` into `y`.
    """
    return DamerauLevenshteinDistance(x, y).compute(0, 0)
