"""Pytest bootstrap for build harness unit tests.

Ensures the repo root is on ``sys.path`` so the tests can import the harness
package as ``scripts.build_harness.harness.*`` regardless of how pytest is
invoked. Mirrors the bootstrap that ``scripts/build_harness/harness.py``
performs when run as a script.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
