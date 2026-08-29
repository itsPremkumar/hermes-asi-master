#!/usr/bin/env python3
"""
state.py — StateGraph & Universal State Container for Super-Harness
Manages execution nodes, shared state, checkpoint rollback, and execution DAGs.
"""

import time
import json
import sqlite3
import pathlib
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class AgentState:
    """Universal state shared across all nodes in the workflow graph."""
    goal: str
    current_step: str = ""
    status: str = "initialized"
    artifacts: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    memory_context: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def log_step(self, node_name: str, action: str, output: Any, status: str = "success"):
        self.history.append({
            "node": node_name,
            "action": action,
            "output": output,
            "status": status,
            "timestamp": time.time()
        })

    def set_artifact(self, name: str, data: Any):
        self.artifacts[name] = data

    def get_artifact(self, name: str, default: Any = None) -> Any:
        return self.artifacts.get(name, default)

class StateGraph:
    """Lightweight, resilient StateGraph engine supporting Node chaining, conditional routing, and loops."""
    def __init__(self):
        self.nodes: Dict[str, Callable[[AgentState], AgentState]] = {}
        self.edges: Dict[str, List[str]] = {}
        self.conditional_edges: Dict[str, Callable[[AgentState], str]] = {}
        self.entry_node: Optional[str] = None

    def add_node(self, name: str, func: Callable[[AgentState], AgentState]):
        self.nodes[name] = func

    def set_entry_point(self, name: str):
        self.entry_node = name

    def add_edge(self, from_node: str, to_node: str):
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)

    def add_conditional_edges(self, from_node: str, routing_func: Callable[[AgentState], str]):
        self.conditional_edges[from_node] = routing_func

    def execute(self, initial_state: AgentState, max_steps: int = 20) -> AgentState:
        """Executes the StateGraph starting from entry_node until terminal or max_steps."""
        if not self.entry_node or self.entry_node not in self.nodes:
            raise ValueError(f"Entry node '{self.entry_node}' is not registered.")

        current_node_name = self.entry_node
        state = initial_state
        step_count = 0

        while current_node_name and step_count < max_steps:
            step_count += 1
            node_func = self.nodes[current_node_name]
            state.current_step = current_node_name
            
            # Execute node
            state = node_func(state)

            # Determine next node
            if current_node_name in self.conditional_edges:
                next_node_name = self.conditional_edges[current_node_name](state)
            elif current_node_name in self.edges and self.edges[current_node_name]:
                next_node_name = self.edges[current_node_name][0]
            else:
                next_node_name = None

            if not next_node_name or next_node_name == "END":
                break

            current_node_name = next_node_name

        state.status = "completed" if state.status != "failed" else "failed"
        return state
