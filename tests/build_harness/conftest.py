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


import pytest


@pytest.fixture(autouse=True)
def _no_real_cci_flag_verification(monkeypatch):
    """Runner tests mock their subprocesses; skip the real `cci project info` preflight.

    ``execution.verify_project_flags`` itself is tested directly in test_execution.py.
    """
    from scripts.build_harness.harness import scenario_runner
    from scripts.build_harness.tui import runner

    monkeypatch.setattr(scenario_runner, "verify_project_flags", lambda *_a, **_k: None)
    monkeypatch.setattr(runner, "verify_project_flags", lambda *_a, **_k: None)
