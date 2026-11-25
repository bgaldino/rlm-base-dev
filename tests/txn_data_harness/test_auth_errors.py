"""`_run_sf` error messages never echo raw `sf` output, which can carry a token."""

from __future__ import annotations

import json
import subprocess

import pytest

from scripts.txn_data_harness import auth
from scripts.txn_data_harness.auth import SfCliError

TOKEN = "00DWt000000TOKEN!AQEAQsecretsecretsecret"


def _fake_run(returncode: int, stdout: str, stderr: str = ""):
    def run(cmd, capture_output, text):  # noqa: ARG001 - signature of subprocess.run
        return subprocess.CompletedProcess(cmd, returncode, stdout=stdout, stderr=stderr)
    return run


def test_non_json_output_is_not_shown(monkeypatch):
    monkeypatch.setattr(auth.subprocess, "run", _fake_run(0, f"accessToken: {TOKEN}\n"))
    with pytest.raises(SfCliError) as err:
        auth._run_sf(["org", "auth", "show-access-token", "--target-org", "x"])
    assert TOKEN not in str(err.value)
    assert "not JSON" in str(err.value)


def test_failure_without_stderr_does_not_show_raw_stdout(monkeypatch):
    monkeypatch.setattr(auth.subprocess, "run", _fake_run(1, f"partial {TOKEN}"))
    with pytest.raises(SfCliError) as err:
        auth._run_sf(["org", "auth", "show-access-token", "--target-org", "x"])
    assert TOKEN not in str(err.value)
    assert "not shown" in str(err.value)


def test_failure_shows_the_json_error_message(monkeypatch):
    body = json.dumps({"status": 1, "name": "NamedOrgNotFoundError",
                       "message": "No authorization information found for x."})
    monkeypatch.setattr(auth.subprocess, "run", _fake_run(1, body))
    with pytest.raises(SfCliError) as err:
        auth._run_sf(["org", "display", "--target-org", "x"])
    assert "No authorization information found for x." in str(err.value)


def test_failure_prefers_stderr(monkeypatch):
    monkeypatch.setattr(auth.subprocess, "run", _fake_run(2, f"{TOKEN}", stderr="boom"))
    with pytest.raises(SfCliError) as err:
        auth._run_sf(["org", "display", "--target-org", "x"])
    assert "boom" in str(err.value)
    assert TOKEN not in str(err.value)
