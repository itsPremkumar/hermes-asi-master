"""
capability_graph.py — Map agent capabilities and dependencies.

A directed graph where nodes are capabilities and edges represent
dependencies between them.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from collections import deque


@dataclass
class Edge:
    """An edge in the capability graph."""
    source: str
    target: str
    weight: float = 1.0  # Strength of dependency
    edge_type: str = "requires"  # requires, enhances, conflicts

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "weight": self.weight,
            "edge_type": self.edge_type,
        }


@dataclass
class CapabilityNode:
    """A node in the capability graph."""
    name: str
    description: str
    level: float = 0.0  # 0.0 to 1.0 (mastery level)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "tags": self.tags,
        }


class CapabilityGraph:
    """
    Directed graph of agent capabilities.

    Nodes are capabilities, edges are dependencies.
    Supports topological sorting and path finding.
    """

    def __init__(self):
        self.nodes: dict[str, CapabilityNode] = {}
        self.edges: list[Edge] = []
        self.adjacency: dict[str, list[Edge]] = {}  # source -> edges (outgoing)
        self.reverse_adj: dict[str, list[Edge]] = {}  # target -> edges (incoming)

    def add_node(self, node: CapabilityNode) -> None:
        """Add a capability node."""
        self.nodes[node.name] = node
        if node.name not in self.adjacency:
            self.adjacency[node.name] = []

    def add_edge(self, edge: Edge) -> None:
        """Add a dependency edge."""
        if edge.source not in self.nodes:
            self.add_node(CapabilityNode(name=edge.source, description=""))
        if edge.target not in self.nodes:
            self.add_node(CapabilityNode(name=edge.target, description=""))
        self.edges.append(edge)
        self.adjacency[edge.source].append(edge)
        if edge.target not in self.reverse_adj:
            self.reverse_adj[edge.target] = []
        self.reverse_adj[edge.target].append(edge)

    def get_node(self, name: str) -> Optional[CapabilityNode]:
        """Get a node by name."""
        return self.nodes.get(name)

    def get_dependencies(self, name: str) -> list[str]:
        """Get direct dependencies of a capability."""
        edges = self.adjacency.get(name, [])
        return [e.target for e in edges if e.edge_type == "requires"]

    def get_dependents(self, name: str) -> list[str]:
        """Get capabilities that depend on this one."""
        return [e.source for e in self.edges if e.target == name and e.edge_type == "requires"]

    def topological_sort(self) -> list[str]:
        """
        Topological sort of capabilities.

        Returns capabilities in dependency order (prerequisites first).
        """
        in_degree = {name: 0 for name in self.nodes}
        for edge in self.edges:
            if edge.edge_type == "requires":
                in_degree[edge.source] = in_degree.get(edge.source, 0) + 1

        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)
            # Find all edges where this node is the prerequisite (target)
            # and decrement the in_degree of the dependent (source)
            for edge in self.reverse_adj.get(node, []):
                if edge.edge_type == "requires":
                    in_degree[edge.source] -= 1
                    if in_degree[edge.source] == 0:
                        queue.append(edge.source)

        return result

    def find_path(self, start: str, end: str) -> list[str]:
        """
        Find a path from start to end capability.

        Returns:
            List of capability names forming the path, or empty if no path.
        """
        if start not in self.nodes or end not in self.nodes:
            return []

        visited = set()
        queue = deque([(start, [start])])

        while queue:
            current, path = queue.popleft()
            if current == end:
                return path
            if current in visited:
                continue
            visited.add(current)
            for edge in self.adjacency.get(current, []):
                if edge.edge_type == "requires" and edge.target not in visited:
                    queue.append((edge.target, path + [edge.target]))

        return []

    def get_prerequisites(self, name: str) -> list[str]:
        """Get all transitive prerequisites for a capability."""
        visited = set()
        prereqs = []

        def dfs(node):
            for dep in self.get_dependencies(node):
                if dep not in visited:
                    visited.add(dep)
                    prereqs.append(dep)
                    dfs(dep)

        dfs(name)
        return prereqs

    def update_level(self, name: str, level: float) -> None:
        """Update the mastery level of a capability."""
        if name in self.nodes:
            self.nodes[name].level = max(0.0, min(1.0, level))

    def get_learnable_capabilities(self) -> list[str]:
        """
        Get capabilities that can be learned next.

        Returns capabilities whose prerequisites are all satisfied
        (level >= 0.7).
        """
        learnable = []
        for name, node in self.nodes.items():
            if node.level >= 0.7:
                continue
            prereqs = self.get_prerequisites(name)
            if all(self.nodes.get(p, CapabilityNode(name="", description="")).level >= 0.7 for p in prereqs):
                learnable.append(name)
        return learnable

    def to_dict(self) -> dict:
        return {
            "nodes": {name: node.to_dict() for name, node in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
        }
