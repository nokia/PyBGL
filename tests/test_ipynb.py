#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.ipynb import in_ipynb, ipynb_get_background_color, ipynb_get_foreground_color

if not in_ipynb():
    def test_in_ipynb():
        assert in_ipynb() is False

    def test_ipynb_get_background_color():
        assert ipynb_get_background_color() is None

    def test_ipynb_get_foreground_color():
        assert ipynb_get_background_color() is None
else:
    def test_in_ipynb():
        assert in_ipynb() is True

    def test_ipynb_get_background_color():
        assert isinstance(ipynb_get_background_color(), str)

    def test_ipynb_get_foreground_color():
        assert isinstance(ipynb_get_background_color(), str)