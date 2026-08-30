"""Tests for capability_graph.py."""

import pytest
from v9.learning.capability_graph import CapabilityGraph, CapabilityNode, Edge


class TestEdge:
    """Tests for Edge."""

    def test_edge_fields(self):
        edge = Edge(source="a", target="b", weight=0.8, edge_type="requires")
        assert edge.source == "a"
        assert edge.target == "b"
        assert edge.weight == 0.8

    def test_edge_to_dict(self):
        edge = Edge(source="a", target="b", weight=0.5, edge_type="requires")
        d = edge.to_dict()
        assert d["source"] == "a"
        assert d["target"] == "b"


class TestCapabilityNode:
    """Tests for CapabilityNode."""

    def test_node_fields(self):
        node = CapabilityNode(name="python", description="Python programming", level=0.7)
        assert node.name == "python"
        assert node.level == 0.7

    def test_node_to_dict(self):
        node = CapabilityNode(name="python", description="Python", level=0.5)
        d = node.to_dict()
        assert d["name"] == "python"
        assert d["level"] == 0.5


class TestCapabilityGraph:
    """Tests for CapabilityGraph."""

    def test_add_node(self):
        graph = CapabilityGraph()
        node = CapabilityNode(name="python", description="Python")
        graph.add_node(node)
        assert "python" in graph.nodes

    def test_add_edge(self):
        graph = CapabilityGraph()
        graph.add_edge(Edge(source="python", target="algorithms"))
        assert len(graph.edges) == 1

    def test_get_dependencies(self):
        graph = CapabilityGraph()
        graph.add_edge(Edge(source="algorithms", target="python", edge_type="requires"))
        deps = graph.get_dependencies("algorithms")
        assert "python" in deps

    def test_topological_sort(self):
        graph = CapabilityGraph()
        graph.add_edge(Edge(source="ml", target="python", edge_type="requires"))
        graph.add_edge(Edge(source="ml", target="math", edge_type="requires"))
        order = graph.topological_sort()
        assert "python" in order
        assert "math" in order
        assert order.index("python") < order.index("ml")
        assert order.index("math") < order.index("ml")

    def test_find_path(self):
        graph = CapabilityGraph()
        graph.add_edge(Edge(source="ml", target="python", edge_type="requires"))
        graph.add_edge(Edge(source="python", target="basics", edge_type="requires"))
        path = graph.find_path("ml", "basics")
        assert len(path) > 0
        assert path[0] == "ml"
        assert path[-1] == "basics"

    def test_find_path_no_path(self):
        graph = CapabilityGraph()
        graph.add_node(CapabilityNode(name="a", description=""))
        graph.add_node(CapabilityNode(name="b", description=""))
        path = graph.find_path("a", "b")
        assert path == []

    def test_get_prerequisites(self):
        graph = CapabilityGraph()
        graph.add_edge(Edge(source="ml", target="python", edge_type="requires"))
        graph.add_edge(Edge(source="python", target="basics", edge_type="requires"))
        prereqs = graph.get_prerequisites("ml")
        assert "python" in prereqs
        assert "basics" in prereqs

    def test_update_level(self):
        graph = CapabilityGraph()
        graph.add_node(CapabilityNode(name="python", description=""))
        graph.update_level("python", 0.85)
        assert graph.nodes["python"].level == 0.85

    def test_update_level_clamped(self):
        graph = CapabilityGraph()
        graph.add_node(CapabilityNode(name="python", description=""))
        graph.update_level("python", 1.5)
        assert graph.nodes["python"].level == 1.0
        graph.update_level("python", -0.5)
        assert graph.nodes["python"].level == 0.0

    def test_get_learnable_capabilities(self):
        graph = CapabilityGraph()
        graph.add_node(CapabilityNode(name="python", description="", level=0.9))
        graph.add_node(CapabilityNode(name="math", description="", level=0.8))
        graph.add_node(CapabilityNode(name="ml", description="", level=0.3))
        graph.add_edge(Edge(source="ml", target="python", edge_type="requires"))
        graph.add_edge(Edge(source="ml", target="math", edge_type="requires"))
        learnable = graph.get_learnable_capabilities()
        assert "ml" in learnable

    def test_to_dict(self):
        graph = CapabilityGraph()
        graph.add_node(CapabilityNode(name="python", description=""))
        d = graph.to_dict()
        assert "nodes" in d
        assert "edges" in d
