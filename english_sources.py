"""Compatibility entry point for :mod:`sgt_kb.collection.english_sources`."""
from importlib import import_module as _import_module
import sys as _sys

_implementation = _import_module("sgt_kb.collection.english_sources")

if __name__ != "__main__":
    _sys.modules[__name__] = _implementation


def __getattr__(name):
    return getattr(_implementation, name)
