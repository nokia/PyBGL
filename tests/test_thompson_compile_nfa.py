#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    Nfa,
    in_ipynb,
    ipynb_display_graph,
    thompson_compile_nfa
)

# thompson_compile_nfa internals
from pybgl.thompson_compile_nfa import (
    DEFAULT_ALPHABET,
    alternation, bracket, concatenation, literal,
    one_or_more,
    parse_bracket, parse_escaped, parse_repetition,
    repetition, repetition_range,
    zero_or_one, zero_or_more,
)


def nfa_to_triple(nfa) -> tuple:
    q0s = set(nfa.initials)
    assert len(q0s) == 1
    q0 = q0s.pop()
    fs = set(nfa.finals())
    assert len(fs) == 1
    f = fs.pop()
    return (nfa, q0, f)


def make_nfa1() -> Nfa:
    (nfa, q0, f) = literal("x")
    return nfa


def make_nfa2() -> Nfa:
    g = Nfa(2)
    g.add_edge(0, 0, "a")
    g.add_edge(0, 1, "b")
    g.set_final(1)
    return g


def test_literal():
    (nfa, q0, f) = literal("a")
    assert set(nfa.initials) == {0}
    assert set(nfa.finals()) == {1}
    assert nfa.delta(0, "a") == {1}


def test_concatenation():
    (nfa1, q01, f1) = nfa_to_triple(make_nfa1())
    (nfa2, q02, f2) = nfa_to_triple(make_nfa2())
    (nfa, q0, f) = concatenation(nfa1, q01, f1, nfa2, q02, f2)
    assert nfa.accepts("xaab") is True
    assert nfa.accepts("x") is False
    assert nfa.accepts("aab") is False


def test_alternation():
    (nfa1, q01, f1) = nfa_to_triple(make_nfa1())
    (nfa2, q02, f2) = nfa_to_triple(make_nfa2())
    (nfa, q0, f) = alternation(nfa1, q01, f1, nfa2, q02, f2)
    assert nfa.accepts("xaab") is False
    assert nfa.accepts("x") is True
    assert nfa.accepts("aab") is True


def test_zero_or_one():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    (nfa, q0, f) = zero_or_one(nfa, q0, f)
    assert nfa.accepts("") is True
    assert nfa.accepts("x") is True
    assert nfa.accepts("xx") is False
    assert nfa.accepts("a") is False


def test_zero_or_more():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    (nfa, q0, f) = zero_or_more(nfa, q0, f)
    assert nfa.accepts("") is True
    assert nfa.accepts("x") is True
    assert nfa.accepts("xx") is True
    assert nfa.accepts("a") is False


def test_one_or_more():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    (nfa, q0, f) = one_or_more(nfa, q0, f)
    assert nfa.accepts("") is False
    assert nfa.accepts("x") is True
    assert nfa.accepts("xx") is True
    assert nfa.accepts("a") is False


def test_parse_repetition():
    for (m, n) in [(0, 1), (0, None), (1, None), (3, 3), (2, 4), (2, None)]:
        for fmt in ["{%s,%s}", "{   %s , %s  }"]:
            s = fmt % (
                m if m is not None else "",
                n if n is not None else ""
            )
            assert parse_repetition(s) == (m, n)


def test_repetition():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    m = 4
    (nfa, q0, f) = repetition(nfa, q0, f, m)
    words = ["x" * i for i in range(10)]
    # Exactly m repetition
    for (i, w) in enumerate(words):
        assert nfa.accepts(w) == (i == m)


def test_repetition_range():
    a = "a"
    for (m, n) in [(3, 5), (0, 3), (3, 3), (3, None)]:
        (nfa, q0, f) = literal(a)
        (nfa, q0, f) = repetition_range(nfa, q0, f, m, n)
        for i in range(10):
            expected = (m <= i) and (n is None or i <= n)
            w = a * i
            obtained = nfa.accepts(w)
            assert obtained == expected, f"(m, n) = {(m, n)} i = {i} w = {w}"


def test_parse_bracket():
    map_input_expected = {
        "[a-z]": [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
        ],
        "[a-zA-Z]": [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
        ],
        "[a-e0-9P-T]": [
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'P', 'Q', 'R',
            'S', 'T', 'a', 'b', 'c', 'd', 'e'
        ],
        "[^a-zA-Z]": [
            '\t', '\n', '\x0b', '\x0c', '\r', ' ', '!', '"', '#', '$', '%',
            '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2',
            '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?',
            '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~'
        ],
    }

    for (s, expected) in map_input_expected.items():
        assert sorted(parse_bracket(s)) == expected


def test_parse_bracket_custom():
    s = "[X-Z03a-e]"
    chars = parse_bracket(s)
    (nfa, q0, f) = bracket(chars)
    for a in "XYZ03abcde":
        assert nfa.accepts(a) is True
    for a in "ABC12456789fghi":
        assert nfa.accepts(a) is False


def test_parse_bracket_escaped():
    s = r"[\s]"
    assert parse_bracket(s) == {' ', '\t'}


def test_parse_escaped():
    assert parse_escaped(r"\.") == {"."}
    assert parse_escaped(r"\|") == {"|"}
    assert parse_escaped(r"\?") == {"?"}
    assert parse_escaped(r"\*") == {"*"}
    assert parse_escaped(r"\+") == {"+"}
    assert parse_escaped(r"\(") == {"("}
    assert parse_escaped(r"\)") == {")"}
    assert parse_escaped(r"\[") == {"["}
    assert parse_escaped(r"\]") == {"]"}
    assert parse_escaped(r"\{") == {"{"}
    assert parse_escaped(r"\}") == {"}"}
    assert parse_escaped(r"\w") == parse_bracket("[a-zA-Z0-9]")
    assert parse_escaped(r"\W") == parse_bracket("[^a-zA-Z0-9]")
    assert parse_escaped(r"\d") == parse_bracket("[0-9]")
    assert parse_escaped(r"\D") == parse_bracket("[^0-9]")
    assert parse_escaped(r"\a") == {"\a"}
    assert parse_escaped(r"\b") == {"\b"}
    assert parse_escaped(r"\f") == {"\f"}
    assert parse_escaped(r"\n") == {"\n"}
    assert parse_escaped(r"\r") == {"\r"}
    assert parse_escaped(r"\t") == {"\t"}
    assert parse_escaped(r"\v") == {"\v"}


def test_escaped_operator():
    (nfa, q0, f) = thompson_compile_nfa("a\\?b")
    assert nfa.accepts("a?b") is True
    assert nfa.accepts("ab") is False
    assert nfa.accepts("b") is False

    (nfa, q0, f) = thompson_compile_nfa("a?b")
    assert nfa.accepts("a?b") is False
    assert nfa.accepts("ab") is True
    assert nfa.accepts("b") is True

    for regexp in (
        r"\|", r"\.", r"\*", r"\+", r"\(", r"\)",
        r"\{", r"\}", r"\[", r"\]"
    ):
        (nfa, q0, f) = thompson_compile_nfa(regexp)
        assert nfa.accepts(regexp.replace("\\", ""))

    regexp = r"\|\.\*\+\(\)\{\}\[\]"
    (nfa, q0, f) = thompson_compile_nfa(regexp)
    nfa.accepts(regexp.replace("\\", ""))


def test_escaped_classes():
    whole_alphabet = DEFAULT_ALPHABET
    escaped_classes = [r"\d", r"\w", r"\s", r"\D", r"\W", r"\S"]
    map_escape_allowed = {
        r: set(parse_escaped(r, whole_alphabet))
        for r in escaped_classes
    }
    for regexp in [r"\d", r"\w", r"\s", r"\D", r"\W", r"\S"]:
        allowed = map_escape_allowed[regexp.lower()]
        if regexp.lower() != regexp:
            allowed = set(whole_alphabet) - allowed
        (nfa, q0, f) = thompson_compile_nfa(regexp, whole_alphabet)
        for a in whole_alphabet:
            assert nfa.accepts(a) == (a in allowed), (
                f"regexp = {regexp} "
                f"a = '{a}' ({ord(a)}) "
                f"allowed = '{allowed}' "
                f"obtained = {nfa.accepts(a)} "
                f"expected = {a in allowed}"
            )


def test_class_s():
    for r in (r"\s+", r"[\s]+"):
        # print(r)
        (nfa, q0, f) = thompson_compile_nfa(r)
        assert nfa.accepts(" ")
        assert nfa.accepts("   ")
        assert nfa.accepts("\t\t")
        assert nfa.accepts(" \t \t ")


def test_thompson_compile_nfa():
    (nfa, q0, f) = thompson_compile_nfa("(a?b)*?c+d")
    if in_ipynb():
        ipynb_display_graph(nfa)
    assert nfa.accepts("babbbababcccccd")


def test_thompson_compile_nfa_alternation():
    (nfa, q0, f) = thompson_compile_nfa("a*|b")
    if in_ipynb():
        ipynb_display_graph(nfa)
    assert not nfa.accepts("bbbbb")
    assert nfa.accepts("b")
    assert nfa.accepts("aaaaaa")


def test_thompson_compile_nfa_concatenation():
    (nfa, q0, f) = thompson_compile_nfa("a+b+")
    if in_ipynb():
        ipynb_display_graph(nfa)
    assert not nfa.accepts("abab")
    assert not nfa.accepts("aaa")
    assert not nfa.accepts("bbb")
    assert nfa.accepts("ab")
    assert nfa.accepts("aaaaaabbbbbb")


def test_thompson_compile_nfa_zero_or_one():
    (nfa, q0, f) = thompson_compile_nfa("(ab?)*")
    if in_ipynb():
        ipynb_display_graph(nfa)
    assert nfa.accepts("")
    assert not nfa.accepts("b")
    assert nfa.accepts("a")
    assert nfa.accepts("ab")
    assert nfa.accepts("aba")
    assert not nfa.accepts("abb")


def test_thompson_compile_nfa_zero_or_more():
    (nfa, q0, f) = thompson_compile_nfa("(ab+)*")
    if in_ipynb():
        ipynb_display_graph(nfa)
    assert nfa.accepts("")
    assert not nfa.accepts("b")
    assert nfa.accepts("abbbbb")
    assert nfa.accepts("abbbbbabbbbbabbbbb")


def test_thompson_compile_nfa_one_or_more():
    (nfa, q0, f) = thompson_compile_nfa("(ab+)+")
    if in_ipynb():
        ipynb_display_graph(nfa)
    assert not nfa.accepts("")
    assert not nfa.accepts("b")
    assert nfa.accepts("abbbbb")
    assert nfa.accepts("abbbbbabbbbbabbbbb")


def test_thompson_compile_nfa_repetition():
    (nfa, q0, f) = thompson_compile_nfa("((ab){3})*")
    if in_ipynb():
        ipynb_display_graph(nfa)
    for i in range(7):
        assert nfa.accepts("ab" * i) == (i % 3 == 0), (
            f"w = {'ab' * i}, i = {i}"
        )


def test_thompson_compile_nfa_bracket_repetitions():
    (nfa, q0, f) = thompson_compile_nfa("[x-z]{1,3}")
    if in_ipynb():
        ipynb_display_graph(nfa)
    for w in ["x", "y", "xx", "xy", "zy", "xxx", "yyy", "zzz", "xyz", "zyx"]:
        assert nfa.accepts(w) is True
    for w in ["", "xxxx", "aaa"]:
        assert nfa.accepts(w) is False

    (nfa, q0, f) = thompson_compile_nfa("x{3}")
    assert nfa.accepts("xxx")


def test_thompson_compile_nfa_escaped_operators():
    regexp = r"\|\.\*\+\(\)\{\}\[\]aa"
    (nfa, q0, f) = thompson_compile_nfa(regexp)
    nfa.accepts(regexp.replace("\\", ""))
    if in_ipynb():
        ipynb_display_graph(nfa)
