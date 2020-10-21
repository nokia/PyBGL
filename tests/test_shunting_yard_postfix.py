#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.shunting_yard_postfix import (
    OPERATORS_ALG, OPERATORS_RE,
    re_escape, shunting_yard_postfix,
    tokenize_re, tokenize_alg
)

def test_re_escape():
    assert re_escape("(") == "\\("
    assert re_escape(")") == "\\)"

def test_tokenize_alg():
    assert list(tokenize_alg("12+34-456*78/90")) == [
        "12", "+", "34", "-", "456", "*", "78", "/", "90"
    ]
    assert list(tokenize_alg("12+(34+56)")) == [
        "12", "+", "(", "34", "+", "56", ")"
    ]

def test_tokenize_alg_unary():
    assert list(tokenize_alg("+123")) == ["u+", "123"]
    assert list(tokenize_alg("-123")) == ["u-", "123"]
    assert list(tokenize_alg("1*-2")) == ["1", "*", "u-", "2"]
    assert list(tokenize_alg("1*+2")) == ["1", "*", "u+", "2"]
    assert list(tokenize_alg("1--2")) == ["1", "-", "u-", "2"]
    assert list(tokenize_alg("1-+2")) == ["1", "-", "u+", "2"]
    assert list(tokenize_alg("1+-2")) == ["1", "+", "u-", "2"]
    assert list(tokenize_alg("1++2")) == ["1", "+", "u+", "2"]
    assert list(tokenize_alg("1/(-2+3)")) == ["1", "/", "(", "u-", "2", "+", "3", ")"]
    assert list(tokenize_alg("1/(+2+3)")) == ["1", "/", "(", "u+", "2", "+", "3", ")"]

def test_tokenize_re():
    assert list(tokenize_re("11.2.(3+.4*.5?)")) == [
        "11", ".", "2", ".", "(", "3", "+", ".", "4", "*", ".", "5", "?", ")"
    ]

def test_tokenize_re_char_repetitions():
    assert list(tokenize_re("x{1,3}")) == ["x", "{1,3}"]
    assert list(tokenize_re("x{3}"))   == ["x", "{3}"]
    assert list(tokenize_re("x{3,}"))  == ["x", "{3,}"]
    assert list(tokenize_re("x{a}"))   == ["x{a}"]

def test_tokenize_re_escape_sequence():
    assert list(tokenize_re("a\\db")) == ["a", "\\d", "b"]
    assert list(tokenize_re("a\\sb")) == ["a", "\\s", "b"]
    assert list(tokenize_re("a\\wb")) == ["a", "\\w", "b"]
    assert list(tokenize_re("a\\xb")) == ["a\\xb"]

def test_tokenize_re_classes():
    assert list(tokenize_re("a[0-9]b"))  == ["a", "[0-9]",  "b"]
    assert list(tokenize_re("a[^0-9]b")) == ["a", "[^0-9]", "b"]
    assert list(tokenize_re("a[(]b"))    == ["a", "[(]",    "b"]
    assert list(tokenize_re("a[\\]]b"))  == ["a", "[\\]]",  "b"]

def test_shunting_yard_postfix_alg():
    assert list(shunting_yard_postfix("12+3*4+(5-6)/7", OPERATORS_ALG)) == [
        "12", "3", "4", "*", "+", "5", "6", "-", "7", "/", "+"
    ]

def test_shunting_yard_postfix_re():
    # Here the concatenation "." cannot be omitted.
    # See also pybgl.thompson_compile_nfa.catify
    assert list(shunting_yard_postfix("((1.1)?.2.2.2)*?.(3.3)+.(4.4)", OPERATORS_RE)) == [
        "1", "1", ".", "?", "2", ".", "2", ".", "2", ".", "*", "?", "3", "3", ".", "+",
        ".", "4", "4", ".", "."
    ]
