#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the PyBGL project
# https://github.com/nokia/PyBGL

"""Top-level package."""

__author__ = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__ = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__ = "Copyright (C) 2018, Nokia"
__license__ = "BSD-3"
__version__ = "0.11.0"

from .aggregated_visitor import AggregatedVisitor
from .algebra import (
    INFINITY,
    BinaryRelation, Less, GreaterThan, BinaryOperator,
    ClosedOperator, ClosedPlus, ClosedTime, ClosedMin, ClosedMax
)
# from .automaton_copy import automaton_copy
from .automaton import BOTTOM, Automaton, make_automaton
from .bk_tree import BKTree, make_bk_tree
from .breadth_first_search import (
    DefaultBreadthFirstSearchVisitor,
    breadth_first_search, breadth_first_search_graph
)
from .color import (
    hsv_to_hsl, hsl_to_hsv,
    html_color_to_graphviz
)
from .cut import cut
from .damerau_levenshtein_distance import damerau_levenshtein_distance
from .depth_first_search import (
    DefaultDepthFirstSearchVisitor,
    depth_first_search, depth_first_search_graph
)
from .deterministic_inclusion import (
    DeterministicInclusionVisitor, deterministic_inclusion
)
from .deterministic_intersection import (
    DeterministicIntersectionVisitor, deterministic_intersection
)
from .deterministic_union import (
    DeterministicUnionVisitor, deterministic_union
)
from .digital_sequence import DigitalSequence
from .dijkstra_shortest_paths import (
    DijkstraVisitor, dijkstra_shortest_paths, dijkstra_shortest_path,
    make_shortest_paths_dag,
    make_shortest_path
)
# from .graph_copy import graph_copy
from .graph_dp import GraphDp
# from .graph_extract import graph_extract
from .graph import (
    EdgeDescriptor,
    Graph,
    DirectedGraph,
    UndirectedGraph,
)
from .graph_traversal import (
    WHITE, GRAY, BLACK,
    DefaultTreeTraversalVisitor, dfs_tree, bfs_tree
)
from .graph_view import GraphView
from .graphviz import (
    GraphvizStyle, ReadGraphvizVisitor,
    dotstr_to_html, graph_to_html, enrich_kwargs,
    read_graphviz,
    run_graphviz, to_dot
)
from .heap import Comparable, Heap, compare_to_key
from .hopcroft_minimize import hopcroft_minimize
from .html import html, beside
from .incidence_automaton import IncidenceAutomaton, make_incidence_automaton
from .incidence_graph import IncidenceGraph
from .incidence_node_automaton import (
    IncidenceNodeAutomaton, make_incidence_node_automaton
)
from .ipynb import (
    in_ipynb, background_template_html, ipynb_display_graph,
    display_svg, display_body
)
from .lcs_distance import lcs_distance
from .levenshtein_distance import levenshtein_distance
from .moore_determination import moore_determination
from .nfa import EPSILON, Nfa
from .node_automaton import (
    NodeAutomaton,
    make_node_automaton,
)
from .parallel_breadth_first_search import (
    ParallelBreadthFirstSearchVisitor, parallel_breadth_first_search
)
# from .product_mixin import
from .property_map import (
    ReadPropertyMap, ReadWritePropertyMap,
    make_func_property_map, make_assoc_property_map,
    identity_property_map, make_constant_property_map
)
from .prune_incidence_automaton import prune_incidence_automaton
from .regexp import compile_nfa, compile_dfa
from .reverse import reverse_graph, reverse_dict
from .revuz_minimize import DefaultRevuzMinimizeVisitor, revuz_minimize
from .shunting_yard_postfix import (
    MAP_OPERATORS_ALG, MAP_OPERATORS_RE,
    Ast, DefaultShuntingYardVisitor,
    RpnDequeAlg, RpnDequeAst,
    re_escape,
    shunting_yard_ast, shunting_yard_postfix, shunting_yard_compute,
    tokenizer_alg, tokenizer_re
)
from .singleton import Singleton
from .strong_components import strong_components
from .suffix_trie import slices, factors, make_suffix_trie
from .thompson_compile_nfa import thompson_compile_nfa
from .tokenize import tokenize
from .topological_sort import TopologicalSortVisitor, topological_sort
from .trie_matching import TrieMatchingVisitor, trie_matching
from .trie import Trie, TrieDeterministicFusion, trie_deterministic_fusion
