#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Class allowing to aggregate a list of compatible visitors
# into a single visitor.
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

# Note: this module is complementary to colorsys.
# https://docs.python.org/2/library/colorsys.html

def hsv_to_hsl(h :float, s :float, v :float) -> tuple:
    """
    HSV to HSL color conversion.
    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    Args:
        h: Float in [0.0, 1.0] corresponding to hue.
        s: Float in [0.0, 1.0] corresponding to saturation.
        v: Float in [0.0, 1.0] corresponding to value.
    Returns:
        The corresponding HSL normalized tuple.
    """
    l = v * (1 - s / 2)
    s = 0 if l == 0 or l == 1 else (v - l) / min(l, 1 - l)
    return (h, s, l)

def hsl_to_hsv(h :float, s :float, l :float) -> tuple:
    """
    HSL to HSV color conversion.
    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    Args:
        h: `float` in [0.0, 1.0] corresponding to hue.
        s: `float` in [0.0, 1.0] corresponding to saturation.
        l: `float` in [0.0, 1.0] corresponding to light.
    Returns:
        The corresponding HSv normalized tuple.
    """
    v = l + s * min(l, 1 - l)
    s = 0 if v == 0 else 2 * (1 - l/v)
    return (h, s, v)

def normalize_color_tuple(h :int, s:int, x:int) -> tuple:
    """
    Normalize an HSV or HSL tuple.
    Args:
        h: `int` in {0, ..., 360} corresponding to hue.
        s: `int` in {0, ..., 100} corresponding to saturation.
        x: `int` in {0, ..., 100} corresponding to light or value.
    Returns:l
        The corresponding normalized tuple.
    """
    return (h / 360, s / 100, x / 100)

def html_to_graphviz(color :str) -> str:
    """
    HTML to Graphviz color conversion.
    Args:
        color: An HTML color e.g. "#40e0d0", "turquoise", "hsl(173, 71%, 56%)".
    Returns;
        The corresponding graphviz color. It's directly `color` if it does not
        start with hsl.
    """
    if color.startswith("hsl"):
        j = color.find("(")
        k = color.rfind(")")
        (h, s, l) = [
            int(val.replace("%", ""))
            for val in color[j+1:k].split(",")
        ]
        (h, s, v) = hsl_to_hsv(*normalize_color_tuple(h, s, l))
        return ", ".join([
            str(x)
            for x in (h, s, v)
        ])
    else:
        return color
