"""
CLI module for evaluation framework.

Provides command-line interface for running evaluations.
"""

import sys
import os

# Add parent directory to path to allow importing main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import main

__all__ = ["main"]
