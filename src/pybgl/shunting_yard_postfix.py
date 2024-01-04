#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the PyBGL project.
# https://github.com/nokia/pybgl

import re
from collections import deque, namedtuple
from .tokenize import TokenizeVisitor, tokenize as _tokenize

# Imports for the code related to the concrete examples
from collections import defaultdict
# from .graph import *
from .graph import DirectedGraph
from .graphviz import enrich_kwargs
from .property_map import (
    ReadWritePropertyMap, make_assoc_property_map, make_func_property_map
)


(RIGHT, LEFT) = range(2)

# Cardinality is not required by shunting_yard_postfix algorithm, but
# might be useful to process the Reverse Polonese Notation it returns.
Op = namedtuple(
    "Op", ["cardinality", "precedence", "associativity"]
)


def re_escape(s: chr) -> str:
    """
    Escapes a string that contains that must not be confused
    with regular expression operators.

    Args:
        s (str): The string to be escaped.

    Example:
        >>> re_escape("(a.b)+")
        ... '\\(a\\.b\\)\\+'

    Returns:
        The escaped string.
    """
    return "".join(
        a if a not in "|[]{}.+*?()^$\\"
        else "\\" + a
        for a in s
    )


# ------------------------------------------------------------------------
# Algebra tokenization
# See https://docs.python.org/3/library/re.html#writing-a-tokenizer
# ------------------------------------------------------------------------

MAP_OPERATORS_ALG = {
    # Unary operators
    "u+":  Op(cardinality=1, precedence=3, associativity=RIGHT),
    "u-":  Op(cardinality=1, precedence=3, associativity=RIGHT),
    # Binary operators
    "^":  Op(cardinality=2, precedence=4, associativity=RIGHT),
    "*":  Op(cardinality=2, precedence=3, associativity=LEFT),
    "/":  Op(cardinality=2, precedence=3, associativity=LEFT),
    "+":  Op(cardinality=2, precedence=2, associativity=LEFT),
    "-":  Op(cardinality=2, precedence=2, associativity=LEFT),
}

RE_OPERATORS_ALG = [
    re_escape(op)
    for op in list(MAP_OPERATORS_ALG.keys()) + list("()")
]


class AlgTokenizeVisitor(TokenizeVisitor):
    """
    The :py:class:`AlgTokenizeVisitor` specializes the
    :py:class:`TokenizeVisitor`
    used to implement the :py:func:`tokenizer_alg` function.
    """
    def __init__(self):
        """
        Constructor.
        """
        self.expression = list()
        # self.precedence is True iff the previous token is an operator
        self.prev_is_operator = True

    def on_unmatched(self, unmatched: str, start: int, end: int, s: str):
        # Overloaded method
        self.expression.append(float(unmatched))
        self.prev_is_operator = False

    def on_matched(self, matched: str, start: int, end: int, s: str):
        # Overloaded method
        operator = matched
        if self.prev_is_operator and matched not in {"(", ")"}:
            if matched == "+":
                operator = "u+"
            elif matched == "-":
                operator = "u-"
            else:
                raise RuntimeError(f"Invalid unary matched '{matched}'")
        self.expression.append(operator)
        self.prev_is_operator = matched != ")"


def tokenizer_alg(expression: str) -> iter:
    """
    Tokenize an algebraic expression.

    Args:
        expression (str): The input algebraic expression.

    Returns:
        A list where each element is either a string corresponding
        to an algebraic operator or a parenthesis, or either a
        numerical value corresponding to an operand.

    Example:
        >>> tokenizer_alg("(-1 + 22) * 333 / 444")
        ['(', 'u-', 1.0, '+', 22.0, ')', '*', 333.0, '/', 444.0]
    """
    pattern = "|".join(RE_OPERATORS_ALG)
    tokenizer = re.compile(pattern)
    expression = "".join(a for a in expression if not a.isspace())
    vis = AlgTokenizeVisitor()
    _tokenize(tokenizer, expression, vis)
    return vis.expression


# ------------------------------------------------------------------------
# Regexp tokenization
# ------------------------------------------------------------------------

MAP_OPERATORS_RE = {
    # Unary operators
    "*":  Op(cardinality=1, precedence=4, associativity=LEFT),
    "+":  Op(cardinality=1, precedence=4, associativity=LEFT),
    "?":  Op(cardinality=1, precedence=3, associativity=LEFT),
    # Binary operators
    ".":  Op(cardinality=2, precedence=2, associativity=LEFT),
    "|":  Op(cardinality=2, precedence=1, associativity=LEFT),
}

RE_OPERATORS_RE = [
    re_escape(op)
    for op in list(MAP_OPERATORS_RE.keys()) + ["(", ")"]
] + [
    # Extra repetition operators
    "\\{\\s*\\d+(\\s*,)?(\\s*\\d+)?\\s*\\}",
    # Character classes
    # "\\[.*\\]",
    '\\[([^]])*\\]',
    # Escape sequences (not exhaustive)
    "(\\\\[abdDfnrsStvwW*+?.|\\[\\](){}])",
]


class CatifyTokenizeVisitor(TokenizeVisitor):
    """
    The :py:class:`AlgTokenizeVisitor` specializes the
    :py:class:`TokenizeVisitor`
    used to implement the :py:func:`catify` function.
    """
    def __init__(self, cat: str = "."):
        """
        Constructor.

        Args:
            cat (str): The metacharacter used to represent the
                concatenation operator.
        """
        self.expression = list()
        # self.prev_needs_cat is True iff the previous token requires
        # a concatenation operator
        self.prev_needs_cat = False
        self.cat = cat

    def on_unmatched(self, unmatched: str, start: int, end: int, s: str):
        # Overloaded method
        if self.cat is not None:
            for a in unmatched:
                if self.prev_needs_cat:
                    self.expression.append(self.cat)
                self.expression.append(a)
                self.prev_needs_cat = True
        else:
            self.expression.append(unmatched)
            self.prev_needs_cat = True

    def on_matched(self, matched: str, start: int, end: int, s: str):
        # Overloaded method
        if (
            self.cat is not None
            and self.prev_needs_cat
            and matched[0] in {"[", "(", "\\"}
        ):
            self.expression.append(self.cat)
        self.expression.append(matched)
        self.prev_needs_cat = (matched not in {"(", "|"})


def catify(s: str, cat: str = ".") -> iter:
    """
    Adds concatenation operator in an input regular expression.
    It is needed as in standard regular expression, the concatenation
    operator is implicit. Still, it is required when running the
    Shunting Yard algorithm. In other words, this function is a
    pre-processing step required before parsing a regular expression
    using the Shunting Yard algorithm.

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
    vis = CatifyTokenizeVisitor(cat=cat)
    _tokenize(tokenizer, s, vis=vis)
    return vis.expression


def tokenizer_re(expression: str, cat: str = ".") -> iter:
    """
    Tokenize a regular expression.

    Args:
        expression (str): The input reular expression.

    Returns:
        A list where each element is either a string corresponding
        to a regular expression operator, a parenthesis, or either a
        literal.

    Example:
        >>> tokenizer_re("[abc]d|e*f+g")
        ['[abc]', '.', 'd', '|', 'e', '*', '.', 'f', '+', '.', 'g']
    """
    return catify(expression, cat=cat)


# ------------------------------------------------------------------------
# Shutting Yard output sinks
# ------------------------------------------------------------------------

class DefaultShuntingYardVisitor:
    """
    The :py:class:`DefaultShuntingYardVisitor` is the base class to any
    visitor passed to the :py:func:`shunting_yard_postfix` function.
    """
    def on_pop_operator(self, o: str):
        """
        Method invoked when popping an operator from the input queue.

        Args:
            o (str): The popped operator.
        """
        pass

    def on_push_operator(self, o: str):
        """
        Method invoked when pushing an operator to the operator queue.

        Args:
            o (str): The popped operator.
        """
        pass

    def on_push_output(self, a: str):
        """
        Method invoked when pushing a token to the output queue.

        Args:
            o (str): The popped operator.
        """
        pass


# ------------------------------------------------------------------------
# Shutting Yard algorithm
# ------------------------------------------------------------------------

def shunting_yard_postfix(
    expression: iter,
    map_operators: dict,
    output: deque = None,
    vis: DefaultShuntingYardVisitor = None
) -> deque:
    """
    Shunting-yard algorithm (converts infix notation to Reverse
    Polish Notation).

    See `this tutorial
    <https://gregorycernera.medium.com/converting-regular-expressions-to-postfix-notation-with-the-shunting-yard-algorithm-63d22ea1cf88>`__.
    The implementation is based on `this snippet
    <https://gist.github.com/nitely/497540eb017ed8a75aecb6a4e609c9a2>`__.

    Args:
        expression (iter): Tokenized `iter` containing the input infix
            notation. Each iteration must move to the next token.
            Functions like `tokenizer_alg`, `tokenizer_re` can help to
            transform a `str` to the appropriate iterable.
        map_operators (dict): ``dict{str:  Op}`` defining the grammar.
        output (deque): The output `deque`.
            You could pass a custom class (which implements the method
            ``.append``), e.g., to run computation in a streaming fashion.
            See the :py:class:`RpnDequeAlg` and the
            :py:class:`RpnDequeAst` classes.
        vis (DefaultShuntingYardVisitor): An optional visitor handling the
            events raised by this function.

    Returns:
        The corresponding Reverse Polish Notation.
    """
    if vis is None:
        vis = DefaultShuntingYardVisitor()
    if output is None:
        output = deque()  # queue
    operators = deque()  # stack

    # Internals
    def preceeds(o1: str, o2: str) -> bool:
        """
        Compares the priority of two operators.

        Args:
            o1 (str): The first operator.
            o2 (str): The second operator.

        Returns:
            ``o1`` is priorer than ``o2``.
        """
        return (
            (
                map_operators[o2].associativity == RIGHT and
                map_operators[o1].precedence > map_operators[o2].precedence
            ) or (
                map_operators[o2].associativity == LEFT and
                map_operators[o1].precedence >= map_operators[o2].precedence
            )
        )

    def pop_operator() -> str:
        """
        Pops an operator from the input queue.
        """
        o = operators.pop()
        vis.on_pop_operator(o)
        return o

    def push_operator(o: str):
        """
        Pushes an operator to the operator queue.

        Args:
            o (str): The token of the operator to be pushed to
                the operator stack.
        """
        operators.append(o)
        vis.on_push_operator(o)

    def push_output(a: str):
        """
        Pushes a token to the output queue.

        Args:
            a (str): The token of the symbol to be pushed
                to the output queue.
        """
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
            while (
                operators
                and operators[-1] in map_operators.keys()
                and preceeds(operators[-1], a)
            ):
                op = pop_operator()
                push_output(op)
            push_operator(a)
        else:
            push_output(a)

    while operators:
        push_output(pop_operator())
    return output


# ------------------------------------------------------------------------
# Shunting Yard concrete examples.
# - shunting_yard_compute computes the result of an algebraic expression.
# - shunting_yard_ast builds the AST of an arbitrary expression.
# These two examples rely on specialized sinks used to translate
# on-the-fly the RPN expression returned by shunting_yard_postfix.
# ------------------------------------------------------------------------

class RpnDequeOperation(deque):
    """
    :py:class:`RpnDequeOperation` is the base class that implements
    a queue triggering `on_append` and `on_operation` events for the
    :py:func:`shunting_yard_postfix` function.

    Such a queue is
    handy to process the process handle tokens arriving in the
    `Reverse Polish Notation (RPN)
    <https://en.wikipedia.org/wiki/Reverse_Polish_notation>`__.
    """
    def __init__(self, map_operators: dict, **kwargs):
        """
        Constructor.

        Args:
            map_operators (dict): Maps each operator with its corresponding
                characteristics. `Examples:` :py:data:`MAP_OPERATORS_ALG` and
                :py:data:`MAP_OPERATORS_RE`.
        """
        super().__init__(**kwargs)
        self.map_operators = map_operators

    def on_append(self, a: str) -> object:
        """
        Method invoked when processing a token is about to be appended
        to this :py:class:`RpnDequeOperation` instance.

        Args:
            a (str): The token being processed.

        Returns:
            The parameter ``u`` that will be passed in the next
            :py:meth:`on_operation` call.
        """
        return a

    def on_operation(self, a: str, op: Op, u: object, vs: iter) -> object:
        """
        Method invoked when processing a token related to an operator.

        Args:
            a (str): The token representing the operator being processed.
            op (Op): The specification of the operator.
            u (object): The value returned by the last
                :py:meth:`on_append` call.
            vs (list): The operands.

        Returns:
            The result of the operation.
        """
        return a

    def append(self, a: str):
        """
        Triggers the :py:meth:`RpnDequeOperation.on_append` and
        :py:meth:`RpnDequeOperation.on_operation` methods, possibly
        overloaded in the children class.

        Args:
            a (str): The processed token, which may be an operator
                or an operand.
        """
        op = self.map_operators.get(a)
        u = self.on_append(a)
        if op is not None:
            # We are processing an operator. The next token(s) are
            # its operands.
            card = op.cardinality
            vs = list()
            for _ in range(card):
                v = self.pop()
                vs.insert(0, v)
            u = self.on_operation(a, op, u, vs)
        super().append(u)


class Ast(DirectedGraph):
    """
    The :py:class:`Ast` class implements an `Abstract Syntax Tree (AST)
    <https://en.wikipedia.org/wiki/Abstract_syntax_tree>`__.
    """
    def __init__(
        self,
        pmap_vsymbol: ReadWritePropertyMap = None,
        num_vertices: int = 0,
        root: int = None
    ):
        """
        Constructor.

        Args:
            pmap_vsymbol (ReadWritePropertyMap):
                Maps each vertex with its token.
                Pass an empty property map.
            num_vertices (int): The number of vertices in the AST.
                If the AST is empty, pass ``0``.
            root (int): The vertex descriptor of the root of the
                AST. If the AST is empty, pass ``None``.
        """
        super().__init__(num_vertices)
        if not pmap_vsymbol:
            self.map_vlabel = defaultdict()
            self.pmap_vsymbol = make_assoc_property_map(self.map_vlabel)
        else:
            self.pmap_vsymbol = pmap_vsymbol
        self.root = root

    def add_vertex(self, a: str) -> int:
        """
        Adds a node to this :py:class:`Ast` instance.

        Args:
            a (str): The token assigned to the newly added vertex.

        Returns:
            The vertex descriptor of the newly added vertex.
        """
        u = super().add_vertex()
        self.pmap_vsymbol[u] = a
        return u

    def to_dot(self, *cls, **kwargs) -> str:
        # Overloaded method
        dpv = {
            "label":  make_func_property_map(
                lambda u: "%s %s" % (u, self.pmap_vsymbol[u])
            )
        }
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        return super().to_dot(*cls, **kwargs)

    def symbol(self, u: int) -> str:
        """
        Retrieves the token assigned to a vertex of this
        :py:class:`Ast` instance.

        Args:
            u (int): The corresponding vertex descriptor.

        Returns:
            The corresponding token.
        """
        return self.pmap_vsymbol[u]

    def children(self, u: int) -> iter:
        """
        Retrieves the children of a vertex of this
        :py:class:`Ast` instance.

        Args:
            u (int): The corresponding vertex descriptor.

        Returns:
            The corresponding children iterator.
        """

        return (self.target(e) for e in self.out_edges(u))

    def to_expr(self) -> str:
        """
        Converts this :py:class:`Ast` instance to the
        corresponding expression.

        Returns:
            The string containing the expression modeled
            by this :py:class:`Ast` instance.
        """
        def to_expr_rec(u) -> str:
            a = str(self.symbol(u))
            d = self.out_degree(u)
            if d == 0:
                return a
            elif d == 1:
                child = self.children(u)[0]
                return f"({to_expr_rec(child)}){a}"
            else:
                return "(%s)" % a.join(
                    to_expr_rec(child)
                    for child in self.children(u)
                )
        if self.root:
            raise RuntimeError("self.root is not initialized")
        return to_expr_rec(self.root)


class RpnDequeAst(RpnDequeOperation):
    """
    The :py:class:`RpnDequeAst` class implements a queue
    that can be passed to :py:func:`shunting_yard_postfix` to build
    in streaming an AST (up-bottom).

    For example, if you push ``"+"``, then ``3``, then ``2``, you are
    building the AST where the parent node is + and its operands
    are 2 and 3 and which models the addition ``2 + 3``.

    See the :py:func:`shunting_yard_ast` function.
    """
    def __init__(self, *cls, ast: Ast = None, **kwargs):
        """
        Constructor.

        Args:
            ast (Ast): The output AST.
        """
        super().__init__(*cls, **kwargs)
        self.ast = ast if ast else Ast()

    def on_append(self, a: str) -> int:
        """
        Builds the vertex related to a token pushed in this
        :py:class:`RpnDequeAst` instance.

        Args:
            a (str): The processed token.

        Returns:
            The vertex descriptor that corresponds to this token.
        """
        u = self.ast.add_vertex(a)
        return u

    def on_operation(self, a, op: Op, u: int, vs: list) -> int:
        """
        Builds the edges from an operator to its operand in the `self.ast` AST.

        Args:
            a (str): The token represening the processed operator.
            op (Op): The operator specifications.
            u (int): The vertex descriptor (operator) of the parent node
                of the operator node in the AST (another operator).
            vs (list): The list of of vertex descriptors corresponding
                to each children of the operator node in the AST (operands).

        Returns:
            The parent vertex descriptor.
        """
        for v in vs:
            self.ast.add_edge(u, v)
        return u


def shunting_yard_ast(
    expression: iter,
    map_operators: dict,
    vis: DefaultShuntingYardVisitor = None
) -> tuple:
    """
    Computes the AST related to a tokenized expression.

    Args:
        expression (iter): An `iter` containing a tokenized expression.
        map_operators (dict): A `dict{str:  Op}` mapping operator
            representation in the input queue and the corresponding
            operator specification.
        vis (DefaultShuntingYardVisitor): An optional visitor or `None`.

    Returns:
        A pair ``(ast, root)`` where ``ast`` is the :py:class:`Ast`
        instance representing the expression and ``root`` is its
        root node.
    """
    ast = Ast()
    output = RpnDequeAst(map_operators=map_operators, ast=ast)
    ret = shunting_yard_postfix(expression, map_operators, output, vis)
    assert len(ret) == 1
    root = ret.pop()
    return (ast, root)


class RpnDequeAlg(RpnDequeOperation):
    """
    The :py:class:`RpnDequeAlg` implements a queue that can
    be passed to :py:func:`shunting_yard_postfix` to compute
    an operation result in a streaming fashion.

    See possible applications:

    - :py:func:`shunting_yard_compute`
    - :py:func:`shunting_yard_ast`
    """
    def __init__(self, **kwargs):
        """
        Constructor.
        """
        map_operators = kwargs.pop("map_operators", None)
        super().__init__(
            map_operators=(
                map_operators if map_operators
                else MAP_OPERATORS_ALG
            ),
            **kwargs
        )
        self.result = None

    def on_operation(self, a, op: Op, u: None, vs: list) -> float:
        """
        Computes an operation.

        Args:
            a (str): The token corresponding to the processed operator.
            op (Op): The operator specification.
            u: Ignored.
            vs (list): The operands.

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
            raise ValueError(
                "Unsupported cardinality: "
                f"a='{a}' "
                f"op.cardinality={op.cardinality})"
            )
        if a == "+":
            return x + y
        elif a == "-":
            return x - y
        elif a == "/":
            return x / y
        elif a == "*":
            return x * y
        elif a == "^":
            return x ** y
        elif a == "u-":
            return -x
        elif a == "u-":
            return x
        else:
            raise ValueError(f"Unsupported operator '{a}'")


def shunting_yard_compute(
    expression: iter,
    map_operators: dict = MAP_OPERATORS_ALG,
    tokenize: bool = True,
    vis: DefaultShuntingYardVisitor = None
) -> float:
    """
    Computes the result of an algebraic operation.

    Args:
        expression (iter): The input operation. It may be either
            a string (pass `tokenize=True`), or the corresponding list
            of tokens (see :py:func:`tokenizer_alg`).
        map_operators (dict): ``dict{str:  Op}`` mapping the operator
            string representation in the tokenized input with the
            corresponding `Op` specification.
        tokenize (bool): Pass ``True`` if ``expression`` must be tokenized,
            ``False`` otherwise.
        vis (DefaultShuntingYardVisitor): An optional visitor instance.

    Example:
        >>> shunting_yard_compute("2 + (3 * 40)")
        122.0

    Returns:
        The output ``float`` result.
    """
    if tokenize:
        output = RpnDequeAlg(map_operators=map_operators)
    ret = shunting_yard_postfix(
        tokenizer_alg(expression),
        map_operators,
        output,
        vis
    )
    assert len(ret) == 1
    result = ret.pop()
    return result
