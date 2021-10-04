#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl
#
# Adapted from: https://gist.github.com/nitely/497540eb017ed8a75aecb6a4e609c9a2
# Explanations: https://medium.com/@gregorycernera/converting-regular-expressions-to-postfix-notation-with-the-shunting-yard-algorithm-63d22ea1cf88

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

import re
from collections    import deque, namedtuple
from .tokenize      import TokenizeVisitor, tokenize as _tokenize

(RIGHT, LEFT) = range(2)

# cardinality is not required by shunting_yard_postfix algorithm, but
# might be useful to process the Reverse Polonese Notation it returns.
Op = namedtuple(
    "Op", ["cardinality", "precedence", "associativity"]
)

def re_escape(s :chr) -> str:
    return "".join(
        a if a not in "|[]{}.+*?()^$\\"
        else "\\" + a
        for a in s
    )

#------------------------------------------------------------------------
# Algebra tokenization
# See https://docs.python.org/3/library/re.html#writing-a-tokenizer
#------------------------------------------------------------------------

MAP_OPERATORS_ALG = {
    # Unary operators
    "u+" : Op(cardinality=1, precedence=3, associativity=RIGHT),
    "u-" : Op(cardinality=1, precedence=3, associativity=RIGHT),
    # Binary operators
    "^" : Op(cardinality=2, precedence=4, associativity=RIGHT),
    "*" : Op(cardinality=2, precedence=3, associativity=LEFT),
    "/" : Op(cardinality=2, precedence=3, associativity=LEFT),
    "+" : Op(cardinality=2, precedence=2, associativity=LEFT),
    "-" : Op(cardinality=2, precedence=2, associativity=LEFT),
}

RE_OPERATORS_ALG = [
    re_escape(op)
    for op in list(MAP_OPERATORS_ALG.keys()) + list("()")
]

class AlgTokenizeVisitor(TokenizeVisitor):
    def __init__(self, expression :list = None, cat :chr = "."):
        self.expression = list() if expression is None else expression
        self.prev_is_operator = True
    def on_unmatched(self, unmatched :str, start :int, end :int, s :str):
        self.expression.append(float(unmatched))
        self.prev_is_operator = False
    def on_matched(self, matched :str, start :int, end :int, s :str):
        operator = matched
        if self.prev_is_operator and matched not in {"(", ")"}:
            if   matched == "+": operator = "u+"
            elif matched == "-": operator = "u-"
            else: raise RuntimeError(f"Invalid unary matched '{matched}'")
        self.expression.append(operator)
        self.prev_is_operator = matched != ")"

def tokenizer_alg(expression :str) -> iter:
    pattern = "|".join(RE_OPERATORS_ALG)
    tokenizer = re.compile(pattern)
    expression = "".join(a for a in expression if not a.isspace())
    vis = AlgTokenizeVisitor()
    _tokenize(tokenizer, expression, vis)
    return vis.expression

#------------------------------------------------------------------------
# Regexp tokenization
#------------------------------------------------------------------------

MAP_OPERATORS_RE = {
    # Unary operators
    "*" : Op(cardinality=1, precedence=4, associativity=LEFT),
    "+" : Op(cardinality=1, precedence=4, associativity=LEFT),
    "?" : Op(cardinality=1, precedence=3, associativity=LEFT),
    # Binary operators
    "." : Op(cardinality=2, precedence=2, associativity=LEFT),
    "|" : Op(cardinality=2, precedence=1, associativity=LEFT),
}

RE_OPERATORS_RE = [
    re_escape(op)
    for op in list(MAP_OPERATORS_RE.keys()) + ["(", ")"]
] + [
    # Extra repetition operators
    "\\{\\s*\\d+(\\s*,)?(\\s*\\d+)?\\s*\\}",
    # Character classes
    #"\\[.*\\]",
    '\\[([^]])*\\]',
    # Escape sequences (not exhaustive)
    "(\\\\[abdDfnrsStvwW*+?.|\[\](){}])",
]

class CatifyTokenizeVisitor(TokenizeVisitor):
    def __init__(self, expression :list = None, cat :chr = "."):
        self.expression = list() if expression is None else expression
        self.prev_needs_cat = False
        self.cat = cat
    def on_unmatched(self, unmatched :str, start :int, end :int, s :str):
        if self.cat is not None:
            for a in unmatched:
                if self.prev_needs_cat:
                    self.expression.append(self.cat)
                self.expression.append(a)
                self.prev_needs_cat = True
        else:
            self.expression.append(unmatched)
            self.prev_needs_cat = True
    def on_matched(self, matched :str, start :int, end :int, s :str):
        if self.cat is not None and self.prev_needs_cat and matched[0] in {"[", "(", "\\"}:
            self.expression.append(self.cat)
        self.expression.append(matched)
        self.prev_needs_cat = (matched not in {"(", "|"})

def catify(s :str, cat :str = ".") -> iter:
    """
    Add concatenation operator in an input regular expression.
    Args:
        expression: A `str` containing a regular expression.
        is_binary: `Callback(chr) -> bool` returning `True`
            iff the character is a binary operator.
        cat: `chr` representing the concatenation operator.
    Returns:
        The `iter` corresponding to `expression` by adding `cat`
        in the appropriate places.
    """
    pattern = "|".join(re_operator for re_operator in set(RE_OPERATORS_RE))
    tokenizer = re.compile(pattern)
    vis = CatifyTokenizeVisitor(cat = cat)
    _tokenize(tokenizer, s, vis = vis)
    return vis.expression

def tokenizer_re(expression :str, cat :str = ".") -> iter:
    return catify(expression, cat = cat)

#------------------------------------------------------------------------
# Shutting Yard output sinks
#------------------------------------------------------------------------

class DefaultShuntingYardVisitor:
    def on_pop_operator(self, o :str): pass
    def on_push_operator(self, o :str): pass
    def on_push_output(self, a :str): pass

class DebugShuntingYardVisitor(DefaultShuntingYardVisitor):
    def on_pop_operator(self, o :str):  print(f"pop op {o}")
    def on_push_operator(self, o :str): print(f"push op {o}")
    def on_push_output(self, a :str):   print(f"push out {a}")

#------------------------------------------------------------------------
# Shutting Yard algorithm
#------------------------------------------------------------------------

def shunting_yard_postfix(
    expression    :iter,
    map_operators :dict,
    output :deque = None,
    vis :DefaultShuntingYardVisitor = None
) -> deque:
    """
    Shunting-yard algorithm (converts infix notation to Reverse Polish Notation).
    Args:
        expression: Tokenized `iter` containing the input infix notation.
            Each iteration must move to the next token.
            Functions like `tokenizer_alg`, `tokenizer_re` can help to transform
            a `str` to the appropriate iterable.
        map_operators: `dict{str : Op}` defining the grammar.
        output: The output `deque`. You could pass a custom class (which implements `.append`),
            e.g. to run streamed computations.
        vis: A `DefaultShuntingYardVisitor` instance handling event raised by this function.
    Returns:
        The corresponding Reverse Polish Notation.
    """
    if vis is None:
        vis = DefaultShuntingYardVisitor()
    if output is None:
        output = deque() # queue
    operators = deque() # stack

    # Internals
    def preceeds(o1 :chr, o2 :chr) -> bool:
        return (
            (
                map_operators[o2].associativity == RIGHT and
                map_operators[o1].precedence > map_operators[o2].precedence
            ) or (
                map_operators[o2].associativity == LEFT and
                map_operators[o1].precedence >= map_operators[o2].precedence
            )
        )

    def pop_operator() -> chr:
        o = operators.pop()
        vis.on_pop_operator(o)
        return o

    def push_operator(o :chr) -> chr:
        operators.append(o)
        vis.on_push_operator(o)

    def push_output(a :chr) -> chr:
        output.append(a)
        vis.on_push_output(a)

    for a in expression:
        if a == "(":
            push_operator(a)
        elif a == ")":
            o = pop_operator()
            while o and o != "(":
                push_output(o)
                o = pop_operator()
        elif a in map_operators.keys():
            while operators and operators[-1] in map_operators.keys() and preceeds(operators[-1], a):
                op = pop_operator()
                push_output(op)
            push_operator(a)
        else:
            push_output(a)

    while operators:
        push_output(pop_operator())
    return output

#------------------------------------------------------------------------
# Shunting Yard concrete examples.
# - shunting_yard_compute computes the result of an algebraic expression.
# - shunting_yard_ast builds the AST of an arbitrary expression.
# These two examples rely on specialized sinks used to translate
# on-the-fly the RPN expression returned by shunting_yard_postfix.
#------------------------------------------------------------------------

from collections        import defaultdict
from pybgl.graph        import DirectedGraph, add_edge
from pybgl.graphviz     import enrich_kwargs
from pybgl.property_map import (
    ReadWritePropertyMap, make_assoc_property_map, make_func_property_map
)

class RpnDequeOperation(deque):
    """
    Queue triggering `on_append`and `on_operation` events.
    """
    def __init__(self, map_operators :dict, **kwargs):
        super().__init__(**kwargs)
        self.map_operators = map_operators
    def on_append(self, a :str) -> object:
        return a
    def on_operation(self, a :str, op :Op, u :object, vs :iter) -> object:
        return a
    def append(self, a):
        op = self.map_operators.get(a)
        u = self.on_append(a)
        if op is not None:
            card = op.cardinality
            vs = list()
            for _ in range(card):
                v = self.pop()
                vs.insert(0, v)
            u = self.on_operation(a, op, u, vs)
        super().append(u)

class Ast(DirectedGraph):
    """
    Abstract Syntax Tree.
    """
    def __init__(self, pmap_vlabel :ReadWritePropertyMap = None, num_vertices = 0):
        super().__init__(num_vertices)
        if not pmap_vlabel:
            self.map_vlabel = defaultdict()
            self.pmap_vlabel = make_assoc_property_map(self.map_vlabel)
        else:
            self.pmap_vlabel = pmap_vlabel

    def add_vertex(self, a :chr):
        u = super().add_vertex()
        self.pmap_vlabel[u] = a
        return u

    def to_dot(self, **kwargs):
        dpv = {
            "label" : make_func_property_map(
                lambda u: "%s %s" % (u, self.pmap_vlabel[u])
            )
        }
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        return super().to_dot(**kwargs)

class RpnDequeAst(RpnDequeOperation):
    """
    Queue that can be passed to `shunting_yard_postfix` to build
    in streaming an AST. See `shunting_yard_ast`.
    """
    def __init__(self, ast :Ast = None, **kwargs):
        """
        Constructor.
        """
        super().__init__(**kwargs)
        self.ast = ast if ast else Ast()

    def on_append(self, a :str) -> int:
        """
        Build the vertex related to a token pushed in this `RpnDequeAst` instance.
        Args:
            a: `str` represening the processed token.
        Returns:
            The correspoding vertex descriptor.
        """
        u = self.ast.add_vertex(a)
        return u

    def on_operation(self, a, op :Op, u :int, vs :list) -> int:
        """
        Build edges from an operator to its operand in the `self.ast` AST.
        Args:
            a: `str` represening the processed operator.
            op: `Op` specification of `a`.
            u: parent vertex descriptor (operator).
            vs: list of child vertex descriptors (operands).
        Returns:
            The parent vertex descriptor.
        """
        for v in vs:
            add_edge(u, v, self.ast)
        return u

def shunting_yard_ast(
    expression    :iter,
    map_operators :dict,
    vis :DefaultShuntingYardVisitor = None
) -> tuple:
    """
    Compute the AST related to a tokenized expression.
    Args:
        expression: An `iter` containing a tokenized expression.
        map_operators: `dict{str : Op}` mapping operator representation
            in the input queue and the corresponding operator specification.
        vis: A `DefaultShuntingYardVisitor` instance or `None`.
    """
    ast = Ast()
    output = RpnDequeAst(map_operators = map_operators, ast = ast)
    ret = shunting_yard_postfix(expression, map_operators, output, vis)
    assert len(ret) == 1
    root = ret.pop()
    return (ast, root)

class RpnDequeAlg(RpnDequeOperation):
    """
    Queue that can be passed to `shunting_yard_postfix` to compute
    an operation result in streaming. See `shunting_yard_compute`.
    """
    def __init__(self, **kwargs):
        """
        Constructor.
        """
        map_operators = kwargs.pop("map_operators", None)
        super().__init__(
            map_operators = map_operators if map_operators else MAP_OPERATORS_ALG,
            **kwargs
        )
        self.result = None

    def on_operation(self, a, op :Op, u :None, vs :list) -> float:
        """
        Compute an operation.
        Args:
            a: The `str` containing the processed operator.
            op: The `Op` specification of `a`.
            u: Ignored
            vs: The `list` of operands.
        Returns:
            The `float` containing the operation result.
        """
        assert len(vs) == op.cardinality
        if op.cardinality == 1:
            x = vs[0]
        elif op.cardinality == 2:
            x = vs[0]
            y = vs[1]
        else:
            raise ValueError(f"Unsupported cardinality '{a}' (card={card})")
        if   a == "+":  return x + y
        elif a == "-":  return x - y
        elif a == "/":  return x / y
        elif a == "*":  return x * y
        elif a == "^":  return x ** y
        elif a == "u-": return -x
        elif a == "u-": return x
        else:
            raise ValueError(f"Unsupported operator '{a}'")
        return ret

def shunting_yard_compute(
    expression    :iter,
    map_operators :dict = MAP_OPERATORS_ALG,
    tokenize      :bool = True,
    vis :DefaultShuntingYardVisitor = None
) -> float:
    """
    Compute an operation and returns the corresponding results.
    Args:
        expression: The input operation, either as a string (pass `tokenize=True`),
            or already tokenized (see e.g. `tokenizer_alg`).
        map_operators: `dict{str : Op}` mapping the operator string representation
            in the tokenized input with the corresponding `Op` specification.
        tokenize: Pass `True` if `expression` must be tokenized, `False` otherwise.
        vis: A `DefaultShuntingYardVisitor` instance.
    Returns:
        The output `float` result.
    """
    if tokenize:
        output = RpnDequeAlg(map_operators = map_operators)
    ret = shunting_yard_postfix(tokenizer_alg(expression), map_operators, output, vis)
    assert len(ret) == 1
    result = ret.pop()
    return result
