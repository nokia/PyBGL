#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.ipynb import in_ipynb

if not in_ipynb():
    def test_in_ipynb():
        assert in_ipynb() is False
else:
    def test_in_ipynb():
        assert in_ipynb() is True
