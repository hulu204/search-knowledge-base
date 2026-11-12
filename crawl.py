# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Compatibility entry point for :mod:`sgt_kb.collection.crawl`."""
from importlib import import_module as _import_module
import sys as _sys

_implementation = _import_module("sgt_kb.collection.crawl")

if __name__ == "__main__":
    _implementation.main()
else:
    _sys.modules[__name__] = _implementation


def __getattr__(name):
    return getattr(_implementation, name)
