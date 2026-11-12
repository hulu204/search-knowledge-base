#!/usr/bin/env python3
"""Compatibility entry point for :mod:`sgt_kb.service.start_workbench`."""
from importlib import import_module as _import_module
import sys as _sys

_implementation = _import_module("sgt_kb.service.start_workbench")

if __name__ == "__main__":
    _sys.exit(_implementation.main())
else:
    _sys.modules[__name__] = _implementation


def __getattr__(name):
    return getattr(_implementation, name)
