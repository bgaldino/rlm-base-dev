"""Tests for scripts.build_harness.harness.execution."""

from __future__ import annotations

import re
import subprocess
import sys
from threading import Event

from scripts.build_harness.harness.execution import make_run_id, org_exists, run_command, run_command_stream


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


def test_org_exists_returns_false_on_timeout(tmp_path, monkeypatch) -> None:
    def _timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd=["cci", "org", "info", "demo"], timeout=30)

    monkeypatch.setattr("scripts.build_harness.harness.execution.subprocess.run", _timeout)
    assert org_exists(tmp_path, "demo") is False


def test_org_exists_returns_true_on_zero_exit(tmp_path, monkeypatch) -> None:
    class _Result:
        returncode = 0

    monkeypatch.setattr(
        "scripts.build_harness.harness.execution.subprocess.run",
        lambda *_args, **_kwargs: _Result(),
    )
    assert org_exists(tmp_path, "demo") is True
