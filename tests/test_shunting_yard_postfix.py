#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    MAP_OPERATORS_ALG, MAP_OPERATORS_RE,
    Ast,
    RpnDequeAlg, RpnDequeAst,
    graph_to_html,
    re_escape,
    shunting_yard_ast, shunting_yard_postfix, shunting_yard_compute,
    tokenizer_re, tokenizer_alg,
)


# class DebugShuntingYardVisitor(DefaultShuntingYardVisitor):
#     def on_pop_operator(self, o: str):
#         print(f"pop op {o}")
#     def on_push_operator(self, o: str):
#         print(f"push op {o}")
#     def on_push_output(self, a: str):
#         print(f"push out {a}")


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
    assert list(tokenizer_alg("1/(-2+3)")) == [
        1, "/", "(", "u-", 2, "+", 3, ")"
    ]
    assert list(tokenizer_alg("1/(+2+3)")) == [
        1, "/", "(", "u+", 2, "+", 3, ")"
    ]


def test_tokenizer_alg_strip():
    assert list(tokenizer_alg(" 12 + 3 ")) == [12, "+", 3]
    assert list(tokenizer_alg("12 + 3")) == [12, "+", 3]
    assert list(tokenizer_alg(" 12+3 ")) == [12, "+", 3]
    assert list(tokenizer_alg("12+3")) == [12, "+", 3]


def test_re_escape():
    assert re_escape("(") == "\\("
    assert re_escape(")") == "\\)"
    assert re_escape("a") == "a"


def test_tokenizer_re_char_repetitions():
    # Explicit concatenation
    assert list(tokenizer_re("x{1,3}.y", cat=None)) == ["x", "{1,3}", ".", "y"]
    assert list(tokenizer_re("x{3}.y", cat=None)) == ["x", "{3}",   ".", "y"]
    assert list(tokenizer_re("x{3,}.y", cat=None)) == ["x", "{3,}",  ".", "y"]
    # Implicit concatenation
    assert list(tokenizer_re("x{1,3}y")) == ["x", "{1,3}", ".", "y"]
    assert list(tokenizer_re("x{3}y")) == ["x", "{3}",   ".", "y"]
    assert list(tokenizer_re("x{3,}y")) == ["x", "{3,}",  ".", "y"]


def test_tokenizer_re_escape_sequence():
    # Explicit concatenation
    assert list(tokenizer_re("a.\\d.b", cat=None)) == [
        "a", ".", "\\d", ".", "b"
    ]
    assert list(tokenizer_re("a.\\s.b", cat=None)) == [
        "a", ".", "\\s", ".", "b"
    ]
    assert list(tokenizer_re("a.\\w.b", cat=None)) == [
        "a", ".", "\\w", ".", "b"
    ]
    # Implicit concatenation
    assert list(tokenizer_re("a\\db")) == ["a", ".", "\\d", ".", "b"]
    assert list(tokenizer_re("a\\sb")) == ["a", ".", "\\s", ".", "b"]
    assert list(tokenizer_re("a\\wb")) == ["a", ".", "\\w", ".", "b"]


def test_tokenizer_re_classes():
    # Explicit concatenation
    assert list(tokenizer_re("a.[0-9].b", cat=None)) == [
        "a", ".", "[0-9]",  ".", "b"
    ]
    assert list(tokenizer_re("a.[^0-9].b", cat=None)) == [
        "a", ".", "[^0-9]", ".", "b"
    ]
    assert list(tokenizer_re("a.[(].b", cat=None)) == [
        "a", ".", "[(]",    ".", "b"
    ]
    assert list(tokenizer_re("[a-z].[0-9]", cat=None)) == [
        "[a-z]", ".", "[0-9]"
    ]
    # Implicit concatenation
    assert list(tokenizer_re("a[0-9]b")) == [
        "a", ".", "[0-9]",  ".", "b"
    ]
    assert list(tokenizer_re("a[^0-9]b")) == [
        "a", ".", "[^0-9]", ".", "b"
    ]
    assert list(tokenizer_re("a[(]b")) == [
        "a", ".", "[(]", ".", "b"
    ]
    assert list(tokenizer_re("[a-z][0-9]")) == [
        "[a-z]", ".", "[0-9]"
    ]


def test_tokenizer_re_parenthesis():
    assert list(tokenizer_re("(a.b.c)+", cat=None)) == [
        "(", "a", ".", "b", ".", "c", ")", "+"
    ]
    assert list(tokenizer_re("(abc)+")) == [
        "(", "a", ".", "b", ".", "c", ")", "+"
    ]


def test_tokenizer_re_explicit():
    assert list(tokenizer_re("11.2.(3+.4*.5?)", cat=None)) == [
        "11", ".", "2", ".", "(", "3", "+", ".", "4", "*", ".", "5", "?", ")"
    ]


def test_tokenizer_re_implicit():
    map_input_expected = {

        "123?(4|5)*67": "1.2.3?.(4|5)*.6.7",
        "(1?2)*?3+4": "(1?.2)*?.3+.4",
        "a\\dx": "a.\\d.x",
        "a\\d+x": "a.\\d+.x",
        "a[0-9]x": "a.[0-9].x",
        "a[0-9]+x": "a.[0-9]+.x",
        "a{1,2}+x": "a{1,2}+.x",
    }
    for (regexp, expected) in map_input_expected.items():
        obtained = "".join(tokenizer_re(regexp))
        assert obtained == expected


def test_shunting_yard_postfix_alg():
    assert list(shunting_yard_postfix(
        tokenizer_alg("12+3*4+(5-6)/7"),
        MAP_OPERATORS_ALG
    )) == [
        12, 3, 4, "*", "+", 5, 6, "-", 7, "/", "+"
    ]


def test_shunting_yard_postfix_re():
    assert list(shunting_yard_postfix(
        tokenizer_re("(12)?(345)*?(67)+89"),
        MAP_OPERATORS_RE
    )) == [
        '1', '2', '.', '?', '3', '4', '.', '5', '.',
        '*', '?', '.', '6', '7', '.', '+', '.', '8',
        '.', '9', '.'
    ]


def test_rpn_queue_alg():
    assert list(shunting_yard_postfix(
        tokenizer_alg("(10 + -2) * (9-3) ^ 2"),
        MAP_OPERATORS_ALG,
        output=RpnDequeAlg(map_operators=MAP_OPERATORS_ALG)
    )) == [288.0]


def test_shunting_yard_compute():
    assert shunting_yard_compute("(10 + -2) * (9-3) ^ 2") == 288.0


def test_rpn_deque_ast():
    tokenized = tokenizer_re("(a?b)*?c+d")
    ast = Ast()
    output = RpnDequeAst(map_operators=MAP_OPERATORS_RE, ast=ast)
    ret = shunting_yard_postfix(tokenized, MAP_OPERATORS_RE, output=output)
    assert ast.num_vertices() == 11
    assert ast.num_edges() == 10
    [root] = ret
    assert root == 10
    graph_to_html(ast)


def test_shunting_yard_ast():
    tokenized = tokenizer_re("(a?b)*?c+d")
    (ast, root) = shunting_yard_ast(tokenized, MAP_OPERATORS_RE)
    assert ast.num_vertices() == 11
    assert ast.num_edges() == 10
    assert root == 10
