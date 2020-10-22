#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.shunting_yard_postfix import (
    MAP_OPERATORS_ALG, MAP_OPERATORS_RE,
    catify, re_escape, shunting_yard_postfix,
    tokenizer_re, tokenizer_alg
)

def test_re_escape():
    assert re_escape("(") == "\\("
    assert re_escape(")") == "\\)"
    assert re_escape("a") == "a"

def test_tokenizer_alg():
    assert list(tokenizer_alg("12+34-456*78/90")) == [
        12, "+", 34, "-", 456, "*", 78, "/", 90
    ]
    assert list(tokenizer_alg("12+(34+56)")) == [
        12, "+", "(", 34, "+", 56, ")"
    ]

def test_tokenizer_alg_unary():
    assert list(tokenizer_alg("+123")) == ["u+", 123]
    assert list(tokenizer_alg("-123")) == ["u-", 123]
    assert list(tokenizer_alg("1*-2")) == [1, "*", "u-", 2]
    assert list(tokenizer_alg("1*+2")) == [1, "*", "u+", 2]
    assert list(tokenizer_alg("1--2")) == [1, "-", "u-", 2]
    assert list(tokenizer_alg("1-+2")) == [1, "-", "u+", 2]
    assert list(tokenizer_alg("1+-2")) == [1, "+", "u-", 2]
    assert list(tokenizer_alg("1++2")) == [1, "+", "u+", 2]
    assert list(tokenizer_alg("1/(-2+3)")) == [1, "/", "(", "u-", 2, "+", 3, ")"]
    assert list(tokenizer_alg("1/(+2+3)")) == [1, "/", "(", "u+", 2, "+", 3, ")"]

def test_tokenizer_alg_strip():
    assert list(tokenizer_alg(" 12 + 3 ")) == [12, "+", 3]
    assert list(tokenizer_alg("12 + 3"))   == [12, "+", 3]
    assert list(tokenizer_alg(" 12+3 "))   == [12, "+", 3]
    assert list(tokenizer_alg("12+3"))     == [12, "+", 3]

def test_tokenizer_re():
    assert list(tokenizer_re("11.2.(3+.4*.5?)")) == [
        "11", ".", "2", ".", "(", "3", "+", ".", "4", "*", ".", "5", "?", ")"
    ]

def test_tokenizer_re_char_repetitions():
    assert list(tokenizer_re("x{1,3}")) == ["x", "{1,3}"]
    assert list(tokenizer_re("x{3}"))   == ["x", "{3}"]
    assert list(tokenizer_re("x{3,}"))  == ["x", "{3,}"]
    assert list(tokenizer_re("x{a}"))   == ["x{a}"]

def test_tokenizer_re_escape_sequence():
    assert list(tokenizer_re("a\\db")) == ["a", "\\d", "b"]
    assert list(tokenizer_re("a\\sb")) == ["a", "\\s", "b"]
    assert list(tokenizer_re("a\\wb")) == ["a", "\\w", "b"]
    assert list(tokenizer_re("a\\xb")) == ["a\\xb"]

def test_tokenizer_re_classes():
    assert list(tokenizer_re("a[0-9]b"))  == ["a", "[0-9]",  "b"]
    assert list(tokenizer_re("a[^0-9]b")) == ["a", "[^0-9]", "b"]
    assert list(tokenizer_re("a[(]b"))    == ["a", "[(]",    "b"]
    assert list(tokenizer_re("a[\\]]b"))  == ["a", "[\\]]",  "b"]

def test_shunting_yard_postfix_alg():
    assert list(shunting_yard_postfix(tokenizer_alg("12+3*4+(5-6)/7"), MAP_OPERATORS_ALG)) == [
        12, 3, 4, "*", "+", 5, 6, "-", 7, "/", "+"
    ]


def test_shunting_yard_postfix_re():
    # Here the concatenation "." cannot be omitted.
    # See also pybgl.thompson_compile_nfa.catify
    assert list(shunting_yard_postfix(tokenizer_re("((1.1)?.2.2.2)*?.(3.3)+.(4.4)"), MAP_OPERATORS_RE)) == [
        "1", "1", ".", "?", "2", ".", "2", ".", "2", ".", "*", "?", "3", "3", ".", "+",
        ".", "4", "4", ".", "."
    ]

def test_catify():
    assert "".join(catify("123?(4|5)*67")) == "1.2.3?.(4|5)*.6.7"
    assert "".join(catify("(1?2)*?3+5")) == "(1?.2)*?.3+.5"

def test_catify_tokenized():
    assert list(catify(["a", "\\d"])) == ["a", ".", "\\d"]
    assert list(catify(["a", "\\d", "+"])) == ["a", ".", "\\d", "+"]
    assert list(catify(["a", "[0-9]", "+"])) == ["a", "[0-9]", "+"]

def test_catify_tokenizer_re():
    assert list(catify(tokenizer_re("a\\d"))) == ["a", ".", "\\d"]
    assert list(catify(tokenizer_re("a\\d+"))) == ["a", ".", "\\d", "+"]
    assert list(catify(tokenizer_re("a[0-9]+"))) == ["a", "[0-9]", "+"]
    assert list(catify(tokenizer_re("a{2,3}b"))) == ["a", "{2,3}", ".", "b"]


