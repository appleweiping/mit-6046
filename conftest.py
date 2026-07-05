"""Make every per-problem-set package importable when pytest is invoked from the
repository root (each ``code/psN`` directory is self-contained and uses flat
imports like ``from maxflow import MaxFlow``)."""
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
for _d in sorted(os.listdir(os.path.join(_ROOT, "code"))):
    _p = os.path.join(_ROOT, "code", _d)
    if os.path.isdir(_p):
        sys.path.insert(0, _p)
