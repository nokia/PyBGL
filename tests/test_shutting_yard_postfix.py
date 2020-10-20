#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.shutting_yard_postfix import OPERATORS_ALG, OPERATORS_RE, shunting_yard_postfix

def test_shutting_yard_postfix_alg():
    assert list(shunting_yard_postfix("2+3*4+(5-6)/7", OPERATORS_ALG)) == [
        '2', '3', '4', '*', '+', '5', '6', '-', '7', '/', '+'
    ]

def testshutting_yard_postfix_re():
    assert list(shunting_yard_postfix("((1.1)?.2.2.2)*?.(3.3)+.(4.4)", OPERATORS_RE)) == [
        '1', '1', '.', '?', '2', '.', '2', '.', '2', '.', '*', '?', '3', '3', '.', '+',
        '.', '4', '4', '.', '.'
    ]
