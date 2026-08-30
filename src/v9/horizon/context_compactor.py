"""
v9 Long-Horizon Engineering — Context Compactor

Context compaction for long-running workflows.
Supports sliding window summarization, entity extraction, and semantic compression.
"""

from __future__ import annotations
import hashlib
import logging
import re
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CompactionStrategy(Enum):
    SLIDING_WINDOW = "sliding_window"
    SUMMARIZATION = "summarization"
    ENTITY_EXTRACTION = "entity_extraction"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass
class ContextWindow:
    """A window of context with metadata."""
    id: str
    content: str
    start_pos: int
    end_pos: int
    importance: float = 0.5
    entities: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    is_compacted: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "importance": self.importance,
            "entities": self.entities,
            "timestamp": self.timestamp,
            "is_compacted": self.is_compacted,
        }


@dataclass
class CompactionResult:
    """Result of a compaction operation."""
    original_length: int
    compacted_length: int
    strategy: CompactionStrategy
    preserved_entities: list[str]
    summary: str = ""
    timestamp: float = field(default_factory=time.time)

    @property
    def compression_ratio(self) -> float:
        if self.original_length == 0:
            return 1.0
        return self.compacted_length / self.original_length

    def to_dict(self) -> dict:
        return {
            "original_length": self.original_length,
            "compacted_length": self.compacted_length,
            "strategy": self.strategy.value,
            "preserved_entities": self.preserved_entities,
            "summary": self.summary,
            "timestamp": self.timestamp,
        }


class EntityExtractor:
    """Extract named entities from text."""

    # Common entity patterns
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "url": r'https?://[^\s<>"]+|www\.[^\s<>"]+',
        "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "uuid": r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        "date": r'\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2})?\b',
        "error_code": r'(?:error|err|exception|fail)\s*[:#]?\s*(\w+)',
        "file_path": r'(?:[A-Za-z]:)?[\\/](?:[^\\/:*?"<>|\r\n]+[\\/])*[^\\/:*?"<>|\r\n]*',
        "number": r'\b\d+(?:\.\d+)?\b',
    }

    def extract(self, text: str) -> list[str]:
        """Extract all entities from text."""
        entities = []
        for entity_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                if match:
                    entities.append(f"{entity_type}:{match}")
        return entities

    def extract_by_type(self, text: str, entity_type: str) -> list[str]:
        """Extract entities of a specific type."""
        pattern = self.PATTERNS.get(entity_type)
        if not pattern:
            return []
        return re.findall(pattern, text, re.IGNORECASE)


class Summarizer:
    """Simple extractive summarization."""

    def __init__(self, max_sentences: int = 3):
        self.max_sentences = max_sentences

    def summarize(self, text: str) -> str:
        """Generate extractive summary."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= self.max_sentences:
            return " ".join(sentences)

        # Score sentences by position and length
        scored = []
        for i, sentence in enumerate(sentences):
            position_score = 1.0 / (1 + abs(i - len(sentences) / 2))
            length_score = min(len(sentence.split()), 20) / 20
            score = position_score * 0.6 + length_score * 0.4
            scored.append((score, sentence))

        scored.sort(reverse=True)
        top_sentences = [s for _, s in scored[:self.max_sentences]]
        return ". ".join(top_sentences) + "."


class SemanticCompressor:
    """Semantic compression using keyword extraction."""

    def __init__(self, max_keywords: int = 20):
        self.max_keywords = max_keywords

    def compress(self, text: str) -> tuple[str, list[str]]:
        """Extract key phrases and return compressed version."""
        # Simple TF-based keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [word for word, _ in keywords[:self.max_keywords]]

        # Extract sentences containing keywords
        sentences = re.split(r'[.!?]+', text)
        preserved = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw in sentence_lower for kw in top_keywords[:10]):
                preserved.append(sentence.strip())

        compressed = ". ".join(preserved)
        return compressed, top_keywords


class ContextCompactor:
    """Main context compaction engine."""

    def __init__(
        self,
        strategy: CompactionStrategy = CompactionStrategy.HYBRID,
        max_context_length: int = 10000,
        compaction_threshold: float = 0.7,
    ):
        self.strategy = strategy
        self.max_context_length = max_context_length
        self.compaction_threshold = compaction_threshold
        self._contexts: OrderedDict[str, ContextWindow] = OrderedDict()
        self._history: list[CompactionResult] = []
        self._entity_extractor = EntityExtractor()
        self._summarizer = Summarizer()
        self._semantic_compressor = SemanticCompressor()

    def add_context(self, content: str, importance: float = 0.5) -> ContextWindow:
        """Add a new context window."""
        context_id = hashlib.md5(content[:100].encode()).hexdigest()[:12]
        entities = self._entity_extractor.extract(content)

        window = ContextWindow(
            id=context_id,
            content=content,
            start_pos=0,
            end_pos=len(content),
            importance=importance,
            entities=entities,
        )

        self._contexts[context_id] = window

        # Check if we need to compact
        total_length = sum(len(w.content) for w in self._contexts.values())
        if total_length > self.max_context_length * self.compaction_threshold:
            self.compact()

        return window

    def compact(self) -> CompactionResult:
        """Compact all context windows."""
        if not self._contexts:
            return CompactionResult(
                original_length=0,
                compacted_length=0,
                strategy=self.strategy,
                preserved_entities=[],
            )

        all_content = "\n".join(w.content for w in self._contexts.values())
        all_entities = []
        for window in self._contexts.values():
            all_entities.extend(window.entities)

        if self.strategy == CompactionStrategy.SLIDING_WINDOW:
            compacted = self._sliding_window_compact()
        elif self.strategy == CompactionStrategy.SUMMARIZATION:
            compacted = self._summarize_compact()
        elif self.strategy == CompactionStrategy.ENTITY_EXTRACTION:
            compacted = self._entity_compact(all_entities)
        elif self.strategy == CompactionStrategy.SEMANTIC:
            compacted, keywords = self._semantic_compressor.compress(all_content)
            all_entities.extend(keywords)
        elif self.strategy == CompactionStrategy.HYBRID:
            compacted = self._hybrid_compact(all_content, all_entities)
        else:
            compacted = all_content

        result = CompactionResult(
            original_length=len(all_content),
            compacted_length=len(compacted),
            strategy=self.strategy,
            preserved_entities=list(set(all_entities)),
            summary=compacted[:500] if len(compacted) > 500 else compacted,
        )

        self._history.append(result)
        return result

    def _sliding_window_compact(self) -> str:
        """Keep only the most recent and important windows."""
        windows = list(self._contexts.values())
        # Sort by importance and timestamp
        windows.sort(key=lambda w: (w.importance, w.timestamp), reverse=True)
        # Keep top 70%
        keep_count = max(1, len(windows) * 7 // 10)
        kept = windows[:keep_count]
        return "\n".join(w.content for w in kept)

    def _summarize_compact(self) -> str:
        """Summarize all contexts."""
        all_content = "\n".join(w.content for w in self._contexts.values())
        return self._summarizer.summarize(all_content)

    def _entity_compact(self, entities: list[str]) -> str:
        """Keep only contexts containing important entities."""
        unique_entities = list(set(entities))
        # Keep windows with most entities
        windows = list(self._contexts.values())
        windows.sort(key=lambda w: len(w.entities), reverse=True)
        kept = windows[:max(1, len(windows) // 2)]
        return "\n".join(w.content for w in kept)

    def _hybrid_compact(self, content: str, entities: list[str]) -> str:
        """Combine multiple strategies."""
        # Step 1: Extract summary
        summary = self._summarizer.summarize(content)

        # Step 2: Get semantic keywords
        _, keywords = self._semantic_compressor.compress(content)

        # Step 3: Combine
        return f"Summary: {summary}\n\nKey entities: {', '.join(set(entities[:20]))}\n\nKeywords: {', '.join(keywords[:10])}"

    def get_context(self, context_id: str) -> Optional[ContextWindow]:
        """Get a specific context window."""
        return self._contexts.get(context_id)

    def get_all_contexts(self) -> list[ContextWindow]:
        """Get all context windows."""
        return list(self._contexts.values())

    def get_history(self) -> list[CompactionResult]:
        """Get compaction history."""
        return self._history

    def clear(self):
        """Clear all contexts."""
        self._contexts.clear()

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy.value,
            "contexts": {cid: w.to_dict() for cid, w in self._contexts.items()},
            "history": [r.to_dict() for r in self._history],
        }
