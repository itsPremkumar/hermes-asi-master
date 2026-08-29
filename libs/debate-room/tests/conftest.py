"""Pytest configuration and fixtures."""

import pytest
import sys
import os

# Add src directory to path so tests can import without installation
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(src_path))
