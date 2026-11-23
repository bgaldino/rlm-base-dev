"""Tests for scripts.build_harness.harness.execution."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from threading import Event

import pytest

from scripts.build_harness.harness.execution import (
    ORG_PROBE_TIMEOUT_SECONDS,
    make_run_id,
    probe_org,
    run_command,
    run_command_stream,
    sf_alias_for,
    _parse_project_info_custom,
    verify_project_flags,
)


class TestMakeRunId:
    """``make_run_id`` must return a deterministic format used as directory names."""

    def test_starts_with_run_prefix(self) -> None:
        assert make_run_id().startswith("run-")

    def test_matches_iso_timestamp_pattern(self) -> None:
        rid = make_run_id()
        assert re.fullmatch(r"run-\d{8}T\d{6}Z", rid), f"unexpected format: {rid}"

    def test_consecutive_calls_are_equal_or_increasing(self) -> None:
        a = make_run_id()
        b = make_run_id()
        assert b >= a


def test_run_command_stream_emits_output(tmp_path) -> None:
    lines = []
    result = run_command_stream(
        [sys.executable, "-c", "print('hello-from-stream')"],
        cwd=tmp_path,
        on_line=lines.append,
    )
    assert result["exit_code"] == 0
    assert "hello-from-stream" in lines
    assert "hello-from-stream" in result["tail"]


def test_run_command_stream_honors_stop_event(tmp_path) -> None:
    stop_event = Event()
    seen = {"count": 0}

    def _on_line(line: str) -> None:
        if "tick-" in line:
            seen["count"] += 1
            if seen["count"] == 1:
                stop_event.set()

    result = run_command_stream(
        [
            sys.executable,
            "-c",
            (
                "import time\n"
                "for i in range(50):\n"
                "    print(f'tick-{i}', flush=True)\n"
                "    time.sleep(0.1)\n"
            ),
        ],
        cwd=tmp_path,
        stop_event=stop_event,
        on_line=_on_line,
    )
    assert seen["count"] >= 1
    assert result["exit_code"] != 0


def test_run_command_can_suppress_stdout(tmp_path, capsys) -> None:
    log_path = tmp_path / "scenario.log"
    run_command(
        tmp_path,
        [sys.executable, "-c", "print('hidden-line')"],
        log_path,
        emit_output=False,
    )
    captured = capsys.readouterr()
    assert "hidden-line" not in captured.out
    assert "hidden-line" in log_path.read_text(encoding="utf-8")


def _fake_sf(monkeypatch, *, stdout="", returncode=0, stderr="", raises=None, list_payload=None):
    """Fake `subprocess.run`: `sf org display` gets the given outcome; `sf org list` gets list_payload."""
    calls = []

    class _Result:
        pass

    def _run(command, **kwargs):
        calls.append((command, kwargs))
        result = _Result()
        if command[:3] == ["sf", "org", "list"]:
            result.returncode, result.stderr = (0, "") if list_payload is not None else (1, "")
            result.stdout = json.dumps(list_payload) if list_payload is not None else ""
            return result
        if raises is not None:
            raise raises
        result.stdout, result.returncode, result.stderr = stdout, returncode, stderr
        return result

    monkeypatch.setattr("scripts.build_harness.harness.execution.subprocess.run", _run)
    return calls


def test_sf_alias_for_joins_project_and_alias() -> None:
    assert sf_alias_for("rlm-base", "demo") == "rlm-base__demo"


def test_probe_org_present_uses_sf_not_cci(tmp_path, monkeypatch) -> None:
    payload = json.dumps({"status": 0, "result": {"status": "Active", "expirationDate": "2026-11-30"}})
    calls = _fake_sf(monkeypatch, stdout=payload)
    result = probe_org(tmp_path, "rlm-base__demo")
    assert result["state"] == "present"
    command, kwargs = calls[0]
    assert command[:3] == ["sf", "org", "display"]
    assert "cci" not in command
    assert kwargs["timeout"] == ORG_PROBE_TIMEOUT_SECONDS


def test_probe_org_timeout_is_not_missing(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, raises=subprocess.TimeoutExpired(cmd=["sf"], timeout=45))
    result = probe_org(tmp_path, "rlm-base__demo")
    assert result["state"] == "timeout"
    assert "45" in result["detail"]


def test_probe_org_not_found_is_missing(tmp_path, monkeypatch) -> None:
    payload = json.dumps({"status": 2, "name": "NamedOrgNotFoundError", "message": "No authorization"})
    _fake_sf(monkeypatch, stdout=payload, returncode=2)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "missing"


@pytest.mark.parametrize("status", ["Expired", "Deleted"])
def test_probe_org_expired_or_deleted_status_is_missing(tmp_path, monkeypatch, status) -> None:
    _fake_sf(monkeypatch, stdout=json.dumps({"status": 0, "result": {"status": status}}))
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "missing"


@pytest.mark.parametrize("expiration", ["2026-11-20", "2020-01-01", "2026-11-24", "2999-01-01"])
def test_probe_org_never_decides_from_expiration_date(tmp_path, monkeypatch, expiration) -> None:
    # ScratchOrgInfo.ExpirationDate has no time zone: a live org on its last day (or
    # one whose date looks past) must not be declared gone from the date alone.
    payload = json.dumps({"status": 0, "result": {"status": "Active", "expirationDate": expiration}})
    _fake_sf(monkeypatch, stdout=payload)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "present"


def test_probe_org_other_failure_is_error_not_missing(tmp_path, monkeypatch) -> None:
    payload = json.dumps({"status": 1, "name": "GenericTimeoutError", "message": "socket hang up"})
    _fake_sf(monkeypatch, stdout=payload, returncode=1)
    result = probe_org(tmp_path, "rlm-base__demo")
    assert result["state"] == "error"
    assert "GenericTimeoutError" in result["detail"]


def test_probe_org_unparseable_output_is_error(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, stdout="not json", stderr="boom", returncode=1)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


def test_probe_org_missing_sf_binary_is_error(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, raises=FileNotFoundError())
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


_FAILED_DISPLAY = json.dumps({"status": 1, "name": "RefreshTokenError", "message": "expired access/refresh token"})


def _org_list(*orgs):
    return {"status": 0, "result": {"scratchOrgs": list(orgs), "nonScratchOrgs": []}}


def test_probe_org_display_failure_with_locally_expired_org_is_missing(tmp_path, monkeypatch) -> None:
    listing = _org_list({"alias": "rlm-base__demo", "isExpired": True, "status": "Deleted", "expirationDate": "2026-11-13"})
    calls = _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=listing)
    result = probe_org(tmp_path, "rlm-base__demo")
    assert result["state"] == "missing"
    assert "RefreshTokenError" in result["detail"]
    commands = [c for c, _ in calls]
    assert ["sf", "org", "list", "--all", "--skip-connection-status", "--json"] in commands
    assert not any(c[0] == "cci" for c in commands)


def test_probe_org_real_expired_org_error_shape_is_missing(tmp_path, monkeypatch) -> None:
    # Measured 2026-11-24: `sf org display` on a deleted scratch org exits 2 with
    # DomainNotFoundError, not NamedOrgNotFoundError; `sf org list --all` marks it Deleted.
    display = json.dumps({"status": 2, "name": "DomainNotFoundError", "message": "The org cannot be found"})
    listing = _org_list({"alias": "rlm-base__demo", "isExpired": True, "status": "Deleted", "expirationDate": "2026-11-13"})
    _fake_sf(monkeypatch, stdout=display, returncode=2, list_payload=listing)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "missing"


def test_probe_org_display_failure_with_past_expiration_in_list_stays_error(tmp_path, monkeypatch) -> None:
    listing = _org_list({"alias": "rlm-base__demo", "isExpired": False, "status": "Active", "expirationDate": "2026-11-20"})
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=listing)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


def test_probe_org_display_failure_with_alias_absent_from_list_stays_error(tmp_path, monkeypatch) -> None:
    # plugin-org drops scratch orgs from the list when the dev hub cannot be queried, so
    # absence is not evidence the org is gone.
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=_org_list({"alias": "other"}))
    result = probe_org(tmp_path, "rlm-base__demo")
    assert result["state"] == "error"
    assert "not in `sf org list`" in result["detail"]


def test_probe_org_dns_failure_with_live_org_under_other_alias_stays_error(tmp_path, monkeypatch) -> None:
    display = json.dumps({"status": 2, "name": "DomainNotFoundError", "message": "getaddrinfo ENOTFOUND"})
    listing = _org_list({"alias": "something-else", "username": "u@example.test", "status": "Active"})
    _fake_sf(monkeypatch, stdout=display, returncode=2, list_payload=listing)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


@pytest.mark.parametrize(
    "record",
    [
        {"alias": "other", "aliases": ["x", "rlm-base__demo"], "status": "Deleted", "isExpired": True},
        {"alias": "other", "username": "rlm-base__demo", "status": "Deleted", "isExpired": True},
    ],
)
def test_probe_org_list_matches_aliases_list_and_username(tmp_path, monkeypatch, record) -> None:
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=_org_list(record))
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "missing"


def test_probe_org_display_failure_with_live_org_in_list_stays_error(tmp_path, monkeypatch) -> None:
    listing = _org_list({"alias": "rlm-base__demo", "isExpired": False, "expirationDate": "2026-11-30", "status": "Active"})
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=listing)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


def test_probe_org_display_failure_with_unreadable_list_stays_error(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=None)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


def test_probe_org_isexpired_in_display_result_is_missing(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, stdout=json.dumps({"status": 0, "result": {"status": "Active", "isExpired": True}}))
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "missing"


def test_probe_org_unhashable_aliases_entries_do_not_crash(tmp_path, monkeypatch) -> None:
    listing = _org_list({"alias": "other", "aliases": [["x"], {"a": 1}, None, "rlm-base__demo"], "status": "Deleted"})
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=listing)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "missing"


@pytest.mark.parametrize("raises", [PermissionError("denied"), OSError("boom"), UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad"), ValueError("v")])
def test_probe_org_os_and_decode_errors_are_error_not_a_crash(tmp_path, monkeypatch, raises) -> None:
    _fake_sf(monkeypatch, raises=raises)
    result = probe_org(tmp_path, "rlm-base__demo")
    assert result["state"] == "error"
    assert "Command not found" not in result["detail"]


def test_probe_org_missing_working_directory_is_not_reported_as_missing_sf(tmp_path, monkeypatch) -> None:
    calls = _fake_sf(monkeypatch, raises=FileNotFoundError())
    result = probe_org(tmp_path / "gone", "rlm-base__demo")
    assert result["state"] == "error"
    assert "Working directory does not exist" in result["detail"]
    assert calls == []


@pytest.mark.parametrize("result", [None, [], "Active"])
def test_probe_org_non_dict_result_is_error(tmp_path, monkeypatch, result) -> None:
    _fake_sf(monkeypatch, stdout=json.dumps({"status": 0, "result": result}))
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


def test_probe_timeout_is_well_below_two_minutes() -> None:
    assert 10 < ORG_PROBE_TIMEOUT_SECONDS <= 45


@pytest.fixture
def workspace(tmp_path):
    """A workspace root whose `.git` entry is a directory, as in a regular clone."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def _fake_cci_project_info(monkeypatch, *, output="", returncode=0, raises=None):
    calls = []

    class _Result:
        pass

    def _run(command, **kwargs):
        calls.append((command, kwargs))
        if raises is not None:
            raise raises
        result = _Result()
        result.returncode, result.stdout, result.stderr = returncode, output, ""
        return result

    monkeypatch.setattr("scripts.build_harness.harness.execution.subprocess.run", _run)
    return calls


def _render_recursive(data, indent=0):
    """Mirror of `cumulusci/cli/project.py::render_recursive` without click styling (piped output)."""
    pad = " " * indent
    lines = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, (bytes, str)):
                lines.append(f"{pad}- {item}")
            else:
                lines.append(f"{pad}-")
                lines.extend(_render_recursive(item, indent + 4))
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                lines.append(f"{pad}{key}:")
                lines.extend(_render_recursive(value, indent + 4))
            else:
                lines.append(f"{pad}{key}: {value}")
    return lines


def _project_info(custom):
    return "\n".join(
        _render_recursive({"name": "rlm-base", "git": {"push_prefix_sandbox": "Sandbox orgs: "}, "custom": custom, "tail": "x"})
    ) + "\n"


def test_verify_project_flags_passes_with_list_flags_in_effective_flags(workspace, monkeypatch) -> None:
    effective = {"inapp": True, "clm": False, "ps_inapp": ["RLM_A", "RLM_B"], "inapp_dataset": "datasets/x", "unset": None}
    calls = _fake_cci_project_info(monkeypatch, output=_project_info(effective))
    assert verify_project_flags(workspace, effective) is None
    assert calls[0][0] == ["cci", "project", "info"]
    assert calls[0][1]["cwd"] == str(workspace)


def test_verify_project_flags_passes_on_the_real_project_custom(workspace, monkeypatch) -> None:
    from scripts.build_harness.harness.config import CCI_FILE, compose_flags, load_cci, load_default_flags

    defaults = load_default_flags(load_cci(CCI_FILE))
    assert any(isinstance(v, list) for v in defaults.values()), "expected list-valued flags in project.custom"
    effective = compose_flags(defaults, {"inapp": True, "mcp": True})
    _fake_cci_project_info(monkeypatch, output=_project_info(effective))
    assert verify_project_flags(workspace, effective) is None
    # CumulusCI loading the repo defaults instead (another project root) is reported.
    _fake_cci_project_info(monkeypatch, output=_project_info(defaults))
    message = verify_project_flags(workspace, effective)
    assert message is not None and "inapp" in message and "mcp" in message


def test_verify_project_flags_reports_flags_cci_reads_from_another_root(workspace, monkeypatch) -> None:
    _fake_cci_project_info(monkeypatch, output=_project_info({"inapp": False, "mcp": False, "clm": False}))
    message = verify_project_flags(workspace, {"inapp": True, "mcp": True, "clm": False})
    assert "inapp: scenario True, CumulusCI loaded 'False'" in message
    assert "mcp: scenario True" in message
    assert "clm" not in message
    assert "git worktree" in message


def test_verify_project_flags_compares_exactly_not_case_insensitively(workspace, monkeypatch) -> None:
    _fake_cci_project_info(monkeypatch, output=_project_info({"inapp": "true"}))
    assert "inapp" in verify_project_flags(workspace, {"inapp": True})


def test_verify_project_flags_reports_a_flag_absent_from_the_output(workspace, monkeypatch) -> None:
    _fake_cci_project_info(monkeypatch, output=_project_info({"other": True}))
    assert "inapp: scenario True, absent" in verify_project_flags(workspace, {"inapp": True})


def test_verify_project_flags_ignores_non_boolean_values_and_none(workspace, monkeypatch) -> None:
    # A None-valued flag must not vacuously pass: only booleans are checked, and a run
    # whose flags contain none to check fails instead of passing on nothing.
    _fake_cci_project_info(monkeypatch, output=_project_info({"inapp": True}))
    assert verify_project_flags(workspace, {"inapp": True, "unset": None}) is None
    message = verify_project_flags(workspace, {"unset": None, "names": ["a"]})
    assert message is not None and "no boolean flags" in message


def test_verify_project_flags_fails_without_a_custom_block(workspace, monkeypatch) -> None:
    _fake_cci_project_info(monkeypatch, output="name: rlm-base\ngit:\n    prefix: x\n")
    assert "no `custom:` block" in verify_project_flags(workspace, {"inapp": True})


def test_verify_project_flags_fails_when_cci_cannot_report(workspace, monkeypatch) -> None:
    _fake_cci_project_info(monkeypatch, returncode=1)
    assert "cci project info" in verify_project_flags(workspace, {"inapp": True})
    _fake_cci_project_info(monkeypatch, raises=FileNotFoundError())
    assert "cci project info" in verify_project_flags(workspace, {"inapp": True})
    _fake_cci_project_info(monkeypatch, raises=subprocess.TimeoutExpired(cmd=["cci"], timeout=60))
    assert "cci project info" in verify_project_flags(workspace, {"inapp": True})


def test_parse_project_info_custom_reads_flags_and_blanks_list_keys() -> None:
    output = (
        "name: rlm-base\n"
        "git:\n"
        "    push_prefix_sandbox: Sandbox orgs: \n"
        "custom:\n"
        "    clm: False\n"
        "    inapp: True\n"
        "    ps_list:\n"
        "        - one\n"
        "        - two\n"
        "    mcp: True\n"
        "tail: x\n"
    )
    assert _parse_project_info_custom(output) == {"clm": "False", "inapp": "True", "ps_list": "", "mcp": "True"}


def test_parse_project_info_custom_ignores_multiline_string_continuations() -> None:
    output = (
        "custom:\n"
        "    inapp: True\n"
        "    notes: first line\n"
        "    continued text with: a colon\n"
        "    clm: False\n"
        "    URL: https://example.test/x\n"
        "tail: x\n"
    )
    parsed = _parse_project_info_custom(output)
    assert parsed["inapp"] == "True" and parsed["clm"] == "False"
    assert "continued text with" not in parsed


def test_parse_project_info_custom_reads_real_cci_output_fixture() -> None:
    fixture = Path(__file__).parent / "fixtures" / "cci_project_info.txt"
    parsed = _parse_project_info_custom(fixture.read_text(encoding="utf-8"))
    assert parsed["billing"] == "True" and parsed["qbrix"] == "False" and parsed["inapp"] == "False"
    assert parsed["locale"] == "en_US"
    assert parsed["rlm_psl_api_names"] == "" and parsed["rlm_ai_psg_api_names"] == ""
    assert "BREDesigner" not in parsed and "dependencies" not in parsed and "name" not in parsed


def test_verify_project_flags_accepts_real_cci_output_fixture(workspace, monkeypatch) -> None:
    fixture = Path(__file__).parent / "fixtures" / "cci_project_info.txt"
    _fake_cci_project_info(monkeypatch, output=fixture.read_text(encoding="utf-8"))
    assert verify_project_flags(workspace, {"billing": True, "inapp": False, "list_flag": ["x"]}) is None
    message = verify_project_flags(workspace, {"inapp": True})
    assert message is not None and "inapp: scenario True, CumulusCI loaded 'False'" in message


def test_verify_project_flags_fails_in_a_worktree_even_when_flags_match(tmp_path, monkeypatch) -> None:
    # A worktree's `.git` is a file; flags equal to the enclosing checkout's defaults
    # would pass the comparison, but CumulusCI still takes that checkout's tasks/.
    (tmp_path / ".git").write_text("gitdir: /elsewhere/.git/worktrees/w\n", encoding="utf-8")
    calls = _fake_cci_project_info(monkeypatch, output=_project_info({"inapp": True}))
    message = verify_project_flags(tmp_path, {"inapp": True})
    assert message is not None and ".git" in message and "worktree" in message
    assert message.failure_class == "deterministic"
    assert calls == [], "the git check must come before running cci"


def test_verify_project_flags_fails_when_there_is_no_git_entry(tmp_path, monkeypatch) -> None:
    _fake_cci_project_info(monkeypatch, output=_project_info({"inapp": True}))
    assert verify_project_flags(tmp_path, {"inapp": True}) is not None


def test_verify_project_flags_failure_classes(workspace, monkeypatch) -> None:
    _fake_cci_project_info(monkeypatch, raises=subprocess.TimeoutExpired(cmd=["cci"], timeout=60))
    assert verify_project_flags(workspace, {"inapp": True}).failure_class == "transient"
    _fake_cci_project_info(monkeypatch, raises=FileNotFoundError())
    assert verify_project_flags(workspace, {"inapp": True}).failure_class == "unknown"
    _fake_cci_project_info(monkeypatch, raises=PermissionError())
    assert verify_project_flags(workspace, {"inapp": True}).failure_class == "unknown"
    _fake_cci_project_info(monkeypatch, returncode=1)
    assert verify_project_flags(workspace, {"inapp": True}).failure_class == "unknown"
    _fake_cci_project_info(monkeypatch, output=_project_info({"inapp": False}))
    assert verify_project_flags(workspace, {"inapp": True}).failure_class == "deterministic"
