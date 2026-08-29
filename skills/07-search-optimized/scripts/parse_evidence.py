#!/usr/bin/env python3
"""
parse_evidence.py — Hermes Search-Optimized Helper Script
Per official Hermes skill guideline: Include Helper Scripts — don't expect LLM to write parsers inline.

Parses Hermes evidence files (evidence-graph.md, sources.md) and validates completeness.
Usage: python parse_evidence.py ./evidence/evidence-graph.md
"""

import sys
import pathlib
import re

def parse_evidence_graph(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    # Count claims
    claims = re.findall(r"^\| *\d+ *\|", text, re.MULTILINE)
    # Check for confidence column
    has_confidence = "Confidence" in text
    # Check for source URLs
    urls = re.findall(r"https?://\S+", text)
    return {
        "claims": len(claims),
        "has_confidence": has_confidence,
        "urls": len(urls),
        "path": str(path),
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_evidence.py <evidence-graph.md> [sources.md]")
        sys.exit(1)
    graph_path = pathlib.Path(sys.argv[1])
    if not graph_path.exists():
        print(f"Not found: {graph_path}")
        sys.exit(1)
    result = parse_evidence_graph(graph_path)
    print(f"Evidence Graph: {result['path']}")
    print(f"  Claims: {result['claims']}")
    print(f"  Has Confidence: {result['has_confidence']}")
    print(f"  URLs: {result['urls']}")
    if result["claims"] == 0:
        print("  ⚠️ No claims found — check template filled")
        sys.exit(1)
    if not result["has_confidence"]:
        print("  ⚠️ Missing Confidence column")
        sys.exit(1)
    print("  ✅ Evidence graph OK")

    if len(sys.argv) >= 3:
        sources_path = pathlib.Path(sys.argv[2])
        if sources_path.exists():
            sources_text = sources_path.read_text(encoding="utf-8")
            primary = len(re.findall(r"Primary", sources_text))
            print(f"Sources: {sources_path} — Primary: {primary}")

if __name__ == "__main__":
    main()
