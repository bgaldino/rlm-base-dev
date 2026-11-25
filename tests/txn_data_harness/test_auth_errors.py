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
    assert err.value.__cause__ is None
    assert err.value.__suppress_context__


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
    assert "NamedOrgNotFoundError: No authorization information found for x." in str(err.value)


def test_json_error_wins_over_a_warning_on_stderr(monkeypatch):
    body = json.dumps({"status": 1, "name": "NamedOrgNotFoundError", "message": "No org x."})
    warning = "Warning: @salesforce/cli update available from 2.159.7 to 2.160.0."
    monkeypatch.setattr(auth.subprocess, "run", _fake_run(1, body, stderr=warning))
    with pytest.raises(SfCliError) as err:
        auth._run_sf(["org", "display", "--target-org", "x"])
    assert "No org x." in str(err.value)
    assert "update available" not in str(err.value)


def test_failure_without_a_json_error_shows_stderr(monkeypatch):
    monkeypatch.setattr(auth.subprocess, "run", _fake_run(2, f"{TOKEN}", stderr="boom"))
    with pytest.raises(SfCliError) as err:
        auth._run_sf(["org", "display", "--target-org", "x"])
    assert "boom" in str(err.value)
    assert TOKEN not in str(err.value)


def test_json_that_is_not_an_object_is_a_clear_error(monkeypatch):
    monkeypatch.setattr(auth.subprocess, "run", _fake_run(0, json.dumps([TOKEN])))
    with pytest.raises(SfCliError) as err:
        auth._run_sf(["org", "display", "--target-org", "x"])
    assert "not an object" in str(err.value)
    assert TOKEN not in str(err.value)


def test_client_repr_does_not_show_the_token():
    client = auth.SfRestClient(alias="x", access_token=TOKEN, instance_url="https://example.my.salesforce.com")
    assert TOKEN not in repr(client)
