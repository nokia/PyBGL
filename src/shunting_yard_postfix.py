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
from collections import deque, namedtuple

(RIGHT, LEFT) = range(2)

# cardinality is not required by shunting_yard_postfix algorithm, but
# might be useful to process the Reverse Polonese Notation it returns.
Op = namedtuple(
    "Op", ["cardinality", "precedence", "associativity"]
)

#------------------------------------------------------------------------
# Tokenization (token = atomic sequence of characters)
#------------------------------------------------------------------------

# See https://docs.python.org/3/library/re.html#writing-a-tokenizer
def re_escape(s :chr) -> str:
    return "".join(
        a if a not in "|[]{}.+*?()^$\\"
        else "\\" + a
        for a in s
    )

def tokenize(
    expression        :str,
    re_operators      :set,
    operator_to_token :callable = None,
    operand_to_token  :callable = None
) -> iter:
    """
    Tokenize an input string.
    Args:
        expression: `str` containing the input expression to tokenize.
        re_operators: `set(str)` storing the regular expression to recognize operators.
            Each string must be compatible with `re.compile`.
            Examples: `RE_OPERATORS_ALG`, `RE_OPERATORS_RE`.
        operator_to_token: `None` or Callback used to convert an operator to a dedicated type.
            Can be used to determine whether we process the unary or binary version
            of an operator (see e.g. `alg_operator_to_token`)
        operand_to_token; `None` or Callback used to process an operand (strip, cast, etc.)
    Returns:
        An iterator over the tokenized expression.
    """
    if not operator_to_token:
        operator_to_token = lambda prev_token, prev_is_operator, operator: operator
    if not operand_to_token:
        operand_to_token = lambda operand: operand

    pattern = "|".join(re_operator for re_operator in set(re_operators))
    tokenizer = re.compile(pattern)
    start = 0
    (prev_token, prev_is_operator) = (None, True)
    for match in tokenizer.finditer(expression):
        operand = expression[start:match.start()]
        if operand:
            yield operand_to_token(operand)
            (prev_token, prev_is_operator) = (operand, False)
        operator = match.group(0)
        if operator:
            yield operator_to_token(prev_token, prev_is_operator, operator)
            (prev_token, prev_is_operator) = (operator, True)
        start = match.end()
    operand = expression[start:]
    if operand:
        yield operand_to_token(operand)

#------------------------------------------------------------------------
# Algebra tokenization
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

def alg_operator_to_token(prev_token :str, prev_is_operator :bool, operator :str) -> str:
    if prev_is_operator and prev_token != ")" and operator != "(":
        if   operator == "+": return "u+"
        elif operator == "-": return "u-"
        else: raise RuntimeError(f"Invalid unary operator '{operator}'")
    else:
        return operator

def alg_operand_to_token(operand):
    return float(operand.strip())

def tokenizer_alg(expression :str) -> iter:
    return tokenize(
        "".join(a for a in expression if not a.isspace()),
        RE_OPERATORS_ALG,
        operator_to_token = alg_operator_to_token,
        operand_to_token = alg_operand_to_token
    )

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
    "\\[.*\\]",
    # Escape sequences (not exhaustive)
    "(\\\\[abdDfnrsStvwW*+?.|\[\](){}])",
]

def catify(expression :str, cat :str = ".") -> iter:
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
    is_binary = lambda o: o == "|"

    pattern = "|".join(re_operator for re_operator in set(RE_OPERATORS_RE))
    tokenizer = re.compile(pattern)

    start = 0
    prev_needs_dot = False
    for match in tokenizer.finditer(expression):
        operand = expression[start:match.start()]
        if operand:
            for a in operand:
                if prev_needs_dot:
                    yield cat
                yield a
                prev_needs_dot = True
        operator = match.group(0)
        if operator:
            if (operator == "(" or operator[0] == "\\") and prev_needs_dot:
                yield cat
            yield operator
            prev_needs_dot = not is_binary(operator) and operator != "("
        start = match.end()
    operand = expression[start:]
    if operand:
        for a in operand:
            if prev_needs_dot:
                yield cat
            yield a
            prev_needs_dot = True

def tokenizer_re(expression :str, cat = ".") -> iter:
    if cat:
        expression = "".join(catify(expression, cat))
    return tokenize(expression, RE_OPERATORS_RE)

#------------------------------------------------------------------------
# Shutting Yard algorithm
#------------------------------------------------------------------------

class DefaultShuntingYardVisitor:
    def on_pop_operator(self, o :str): pass
    def on_push_operator(self, o :str): pass
    def on_push_output(self, a :str): pass

class DebugShuntingYardVisitor(DefaultShuntingYardVisitor):
    def on_pop_operator(self, o :str):  print(f"pop op {o}")
    def on_push_operator(self, o :str): print(f"push op {o}")
    def on_push_output(self, a :str):   print(f"push out {a}")

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
# RPN specialized queues
#------------------------------------------------------------------------

from collections        import defaultdict
from pybgl.graph        import DirectedGraph, add_edge
from pybgl.graphviz     import to_dot
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
        kwargs.pop("dpv", None)
        return to_dot(
            self,
            dpv = {
                "label" : make_func_property_map(
                    lambda u: "%s %s" % (u, self.pmap_vlabel[u])
                )
            },
            **kwargs
        )

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
        map_operators = kwargs.pop("map_operators")
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
