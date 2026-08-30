"""
Tests for Context Compactor.
Test count: 14
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v9.horizon.context_compactor import (
    CompactionStrategy,
    CompactionResult,
    ContextCompactor,
    ContextWindow,
    EntityExtractor,
    SemanticCompressor,
    Summarizer,
)


class TestEntityExtractor:
    def test_extract_emails(self):
        extractor = EntityExtractor()
        text = "Contact us at hello@example.com or support@test.org"
        entities = extractor.extract(text)
        assert any("email:" in e for e in entities)

    def test_extract_urls(self):
        extractor = EntityExtractor()
        text = "Visit https://example.com or http://test.org"
        entities = extractor.extract(text)
        assert any("url:" in e for e in entities)

    def test_extract_uuids(self):
        extractor = EntityExtractor()
        text = "ID: 550e8400-e29b-41d4-a716-446655440000"
        entities = extractor.extract(text)
        assert any("uuid:" in e for e in entities)

    def test_extract_numbers(self):
        extractor = EntityExtractor()
        text = "There are 42 items costing 99.99 each"
        entities = extractor.extract(text)
        assert any("number:" in e for e in entities)


class TestSummarizer:
    def test_summarize_short(self):
        summarizer = Summarizer(max_sentences=3)
        text = "First sentence. Second sentence."
        result = summarizer.summarize(text)
        assert len(result) > 0

    def test_summarize_long(self):
        summarizer = Summarizer(max_sentences=2)
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = summarizer.summarize(text)
        assert len(result) > 0


class TestSemanticCompressor:
    def test_compress(self):
        compressor = SemanticCompressor(max_keywords=10)
        text = "Machine learning is a subset of artificial intelligence. Deep learning uses neural networks."
        compressed, keywords = compressor.compress(text)
        assert len(compressed) > 0
        assert len(keywords) > 0


class TestContextCompactor:
    def test_create_compactor(self):
        compactor = ContextCompactor(strategy=CompactionStrategy.HYBRID)
        assert compactor.strategy == CompactionStrategy.HYBRID

    def test_add_context(self):
        compactor = ContextCompactor()
        window = compactor.add_context("Test context content")
        assert isinstance(window, ContextWindow)
        assert window.content == "Test context content"

    def test_add_context_with_importance(self):
        compactor = ContextCompactor()
        window = compactor.add_context("Important context", importance=0.9)
        assert window.importance == 0.9

    def test_compact_sliding_window(self):
        compactor = ContextCompactor(
            strategy=CompactionStrategy.SLIDING_WINDOW,
            max_context_length=100,
            compaction_threshold=0.5,
        )
        for i in range(10):
            compactor.add_context(f"Context window {i}" * 10, importance=i / 10)
        result = compactor.compact()
        assert isinstance(result, CompactionResult)
        assert result.original_length > 0

    def test_compact_summarization(self):
        compactor = ContextCompactor(
            strategy=CompactionStrategy.SUMMARIZATION,
            max_context_length=100,
            compaction_threshold=0.5,
        )
        for i in range(5):
            compactor.add_context(f"Sentence one {i}. Sentence two {i}. Sentence three {i}." * 5)
        result = compactor.compact()
        assert isinstance(result, CompactionResult)
        assert result.compacted_length < result.original_length

    def test_compact_entity_extraction(self):
        compactor = ContextCompactor(
            strategy=CompactionStrategy.ENTITY_EXTRACTION,
            max_context_length=100,
            compaction_threshold=0.5,
        )
        compactor.add_context("Contact: test@example.com. Error: E12345.")
        compactor.add_context("Visit https://example.com for more info.")
        result = compactor.compact()
        assert isinstance(result, CompactionResult)
        assert len(result.preserved_entities) > 0

    def test_compact_semantic(self):
        compactor = ContextCompactor(
            strategy=CompactionStrategy.SEMANTIC,
            max_context_length=100,
            compaction_threshold=0.5,
        )
        for i in range(5):
            compactor.add_context(f"Machine learning algorithms process data. Deep learning uses neural networks." * 5)
        result = compactor.compact()
        assert isinstance(result, CompactionResult)
        assert result.compression_ratio <= 1.0

    def test_compact_hybrid(self):
        compactor = ContextCompactor(
            strategy=CompactionStrategy.HYBRID,
            max_context_length=100,
            compaction_threshold=0.5,
        )
        for i in range(5):
            compactor.add_context(f"Context {i} with important data. Another sentence." * 5)
        result = compactor.compact()
        assert isinstance(result, CompactionResult)
        assert result.strategy == CompactionStrategy.HYBRID

    def test_get_context(self):
        compactor = ContextCompactor()
        window = compactor.add_context("Test context")
        retrieved = compactor.get_context(window.id)
        assert retrieved is not None
        assert retrieved.content == "Test context"

    def test_get_all_contexts(self):
        compactor = ContextCompactor()
        compactor.add_context("First")
        compactor.add_context("Second")
        contexts = compactor.get_all_contexts()
        assert len(contexts) == 2

    def test_get_history(self):
        compactor = ContextCompactor(
            strategy=CompactionStrategy.SUMMARIZATION,
            max_context_length=50,
            compaction_threshold=0.5,
        )
        compactor.add_context("Test " * 20)
        compactor.compact()
        history = compactor.get_history()
        assert len(history) == 1

    def test_clear(self):
        compactor = ContextCompactor()
        compactor.add_context("First")
        compactor.add_context("Second")
        compactor.clear()
        assert len(compactor.get_all_contexts()) == 0
