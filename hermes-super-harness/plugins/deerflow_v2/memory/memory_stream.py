#!/usr/bin/env python3
"""
memory_stream.py — DeerFlow 2.0 Long-Term Fact Extraction & Memory Stream
Extracts atomic facts from agent steps and injects relevant context without prompt bloat.
"""

import time
import re
from typing import List, Dict, Any, Optional

class DeerFlowMemoryStream:
    def __init__(self):
        self.facts: List[Dict[str, Any]] = []
        self.checkpoints: Dict[str, Any] = {}

    def extract_facts(self, text: str, source_node: str) -> List[str]:
        """Extracts key factual statements, constraints, and decisions from step output."""
        extracted = []
        lines = text.split("\n")
        for line in lines:
            cleaned = line.strip()
            # Capture bullet points, numbered items, and decision markers
            if cleaned.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.", "[Fact]", "[Decision]", "[Rule]")):
                fact_content = re.sub(r"^[-*\d.\s\[\]A-Za-z]+:\s*", "", cleaned).strip()
                if len(fact_content) > 10:
                    extracted.append(fact_content)
                    self.facts.append({
                        "fact": fact_content,
                        "source": source_node,
                        "timestamp": time.time()
                    })
        return extracted

    def get_relevant_context(self, query: str, limit: int = 5) -> List[str]:
        """Retrieves top relevant facts matching query tokens."""
        q_tokens = set(query.lower().split())
        scored = []
        for item in self.facts:
            f_tokens = set(item["fact"].lower().split())
            overlap = len(q_tokens.intersection(f_tokens))
            if overlap > 0:
                scored.append((overlap, item["fact"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:limit]]

    def save_checkpoint(self, checkpoint_id: str, state_snapshot: Dict[str, Any]):
        self.checkpoints[checkpoint_id] = {
            "timestamp": time.time(),
            "data": state_snapshot
        }

    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        if checkpoint_id in self.checkpoints:
            return self.checkpoints[checkpoint_id]["data"]
        return None
