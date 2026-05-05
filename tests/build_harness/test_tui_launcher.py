from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path


def _make_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def test_tui_launcher_reports_nonzero_exit(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    source_launcher = repo_root / "tui-cci"
    launcher = tmp_path / "tui-cci"
    launcher.write_text(source_launcher.read_text(encoding="utf-8"), encoding="utf-8")
    _make_executable(launcher)

    venv_python = tmp_path / ".harness" / "tui-venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                'if [[ "${1:-}" == "-c" ]]; then',
                "  exit 0",
                "fi",
                'if [[ "${1:-}" == "-m" && "${2:-}" == "scripts.build_harness.tui" ]]; then',
                '  exit "${FAKE_TUI_EXIT:-0}"',
                "fi",
                "exit 0",
            ]
        ),
        encoding="utf-8",
    )
    _make_executable(venv_python)

    env = os.environ.copy()
    env["TUI_CCI_SKIP_TTY_CHECK"] = "1"
    env["FAKE_TUI_EXIT"] = "7"

    result = subprocess.run(
        [str(launcher)],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 7
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "[tui-cci] TUI exited with code 7" in combined_output
    assert "[tui-cci] Re-run with --debug-launch for startup diagnostics." in combined_output
