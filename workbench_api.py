# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.0", "FlagEmbedding>=1.3", "torch", "numpy", "scipy"]
# ///
"""Compatibility entry point for :mod:`sgt_kb.service.workbench_api`."""
from importlib import import_module as _import_module
import sys as _sys

_implementation = _import_module("sgt_kb.service.workbench_api")

if __name__ == "__main__":
    _implementation.main()
else:
    _sys.modules[__name__] = _implementation


def __getattr__(name):
    return getattr(_implementation, name)
