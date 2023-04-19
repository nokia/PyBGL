#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.color import (
    hsv_to_hsl,
    hsl_to_hsv,
    html_to_graphviz,
    normalize_color_tuple,
)

def test_hsv_to_hsl():
    assert hsv_to_hsl(0.482, 0.714, 0.878) == (0.482, 0.7198274872199998, 0.564554)

def test_hsl_to_hsv():
    assert hsl_to_hsv(0.482, 0.7198274872199998, 0.564554) == (0.482, 0.714, 0.878)

def test_normalize_color_tuple():
    assert normalize_color_tuple(173, 71, 56) == (0.48055555555555557, 0.71, 0.56)

def test_html_to_graphviz():
    assert html_to_graphviz("turquoise") == "turquoise"
    assert html_to_graphviz("#40e0d0") == "#40e0d0"
    assert html_to_graphviz("hsl(173, 71%, 56%)") == "0.48055555555555557, 0.7161852361302155, 0.8724000000000001"
