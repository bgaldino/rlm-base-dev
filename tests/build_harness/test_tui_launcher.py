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


def test_tui_launcher_loads_dotenv_local_without_overriding_env(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    source_launcher = repo_root / "tui-cci"
    launcher = tmp_path / "tui-cci"
    launcher.write_text(source_launcher.read_text(encoding="utf-8"), encoding="utf-8")
    _make_executable(launcher)
    parser = Path("scripts", "build_harness", "tui", "dotenv_local.py")
    (tmp_path / parser).parent.mkdir(parents=True)
    (tmp_path / parser).write_text((repo_root / parser).read_text(encoding="utf-8"), encoding="utf-8")

    home = tmp_path / "home"
    home.mkdir()
    (tmp_path / ".env.local").write_text(
        "\n".join(
            [
                '# workstation overrides',
                'CHROME_BINARY="$HOME/Chrome for Testing" # managed build',
                'export CHROMEDRIVER_PATH = "/from/file"',
                'EMPTY_OVERRIDE="file value must not apply"',
                'EVIL="$(touch should-not-run)"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    venv_python = tmp_path / ".harness" / "tui-venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                'if [[ "${1:-}" == "-c" ]]; then',
                "  exit 0",
                "fi",
                # The launcher must parse .env.local with this venv interpreter,
                # so the parser script runs on the real python3.
                'if [[ "${1:-}" == *.py ]]; then',
                '  exec python3 "$@"',
                "fi",
                'if [[ "${1:-}" == "-m" && "${2:-}" == "scripts.build_harness.tui" ]]; then',
                '  printf "CHROME_BINARY=%s\\n" "$CHROME_BINARY"',
                '  printf "CHROMEDRIVER_PATH=%s\\n" "$CHROMEDRIVER_PATH"',
                '  printf "EMPTY_OVERRIDE=[%s]\\n" "${EMPTY_OVERRIDE-<unset>}"',
                '  printf "EVIL=%s\\n" "${EVIL-<unset>}"',
                "  exit 0",
                "fi",
                "exit 0",
            ]
        ),
        encoding="utf-8",
    )
    _make_executable(venv_python)

    env = os.environ.copy()
    env["TUI_CCI_SKIP_TTY_CHECK"] = "1"
    env["HOME"] = str(home)
    env.pop("CHROME_BINARY", None)
    env.pop("EVIL", None)
    env["CHROMEDRIVER_PATH"] = "/already/set/by/shell"
    env["EMPTY_OVERRIDE"] = ""

    result = subprocess.run(
        [str(launcher)],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert f"CHROME_BINARY={home}/Chrome for Testing" in result.stdout
    assert "CHROMEDRIVER_PATH=/already/set/by/shell" in result.stdout
    assert "EMPTY_OVERRIDE=[]" in result.stdout
    assert "EVIL=<unset>" in result.stdout
    assert "skipping EVIL" in result.stderr
    assert not (tmp_path / "should-not-run").exists()


# The bootstrap picks the interpreter that creates .harness/tui-venv: pyenv's
# newest 3.13 when it exists and can import ssl, else the first python3 on PATH.
_FAKE_PYTHON = """#!/usr/bin/env bash
# Stands in for an interpreter. `-m venv DIR` records who built the venv and
# writes DIR/bin/python, a fake that accepts every later call.
if [[ "${1:-}" == "-m" && "${2:-}" == "venv" ]]; then
  echo "@NAME@" >"$BOOT_LOG"
  mkdir -p "$3/bin"
  printf '#!/usr/bin/env bash\\nexit 0\\n' >"$3/bin/python"
  chmod +x "$3/bin/python"
  exit 0
fi
if [[ "${1:-}" == "-c" && "${2:-}" == "import ssl" ]]; then
  exit "${FAKE_SSL_EXIT:-0}"
fi
exit 0
"""

_FAKE_PYENV = """#!/usr/bin/env bash
case "${1:-}" in
  latest) [[ -n "${FAKE_PYENV_VER:-}" ]] && echo "$FAKE_PYENV_VER" || exit 1 ;;
  prefix) [[ -n "${FAKE_PYENV_PREFIX:-}" ]] && echo "$FAKE_PYENV_PREFIX" || exit 1 ;;
  *) exit 1 ;;
esac
"""


def _run_bootstrap(tmp_path: Path, *, with_pyenv: bool, extra_env: dict) -> str:
    repo_root = Path(__file__).resolve().parents[2]
    launcher = tmp_path / "tui-cci"
    launcher.write_text((repo_root / "tui-cci").read_text(encoding="utf-8"), encoding="utf-8")
    _make_executable(launcher)
    req = tmp_path / "scripts" / "build_harness" / "tui" / "requirements.txt"
    req.parent.mkdir(parents=True)
    req.write_text("textual\n", encoding="utf-8")

    fake_bin = tmp_path / "fakebin"
    fake_bin.mkdir()
    path_python = fake_bin / "python3"
    path_python.write_text(_FAKE_PYTHON.replace("@NAME@", "path-python3"), encoding="utf-8")
    _make_executable(path_python)

    pyenv_prefix = tmp_path / "pyenv-3.13.99"
    (pyenv_prefix / "bin").mkdir(parents=True)
    pyenv_python = pyenv_prefix / "bin" / "python3"
    pyenv_python.write_text(_FAKE_PYTHON.replace("@NAME@", "pyenv-python3"), encoding="utf-8")
    _make_executable(pyenv_python)
    if with_pyenv:
        (fake_bin / "pyenv").write_text(_FAKE_PYENV, encoding="utf-8")
        _make_executable(fake_bin / "pyenv")

    log = tmp_path / "boot.log"
    env = {
        "HOME": str(tmp_path),
        "PATH": f"{fake_bin}:/usr/bin:/bin",
        "TUI_CCI_SKIP_TTY_CHECK": "1",
        "BOOT_LOG": str(log),
        "FAKE_PYENV_VER": "3.13.99",
        "FAKE_PYENV_PREFIX": str(pyenv_prefix),
    }
    env.update(extra_env)
    result = subprocess.run([str(launcher)], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return log.read_text(encoding="utf-8").strip()


def test_tui_bootstrap_prefers_pyenv_313(tmp_path) -> None:
    assert _run_bootstrap(tmp_path, with_pyenv=True, extra_env={}) == "pyenv-python3"


def test_tui_bootstrap_skips_pyenv_python_without_ssl(tmp_path) -> None:
    assert _run_bootstrap(tmp_path, with_pyenv=True, extra_env={"FAKE_SSL_EXIT": "1"}) == "path-python3"


def test_tui_bootstrap_falls_back_without_a_pyenv_313(tmp_path) -> None:
    assert _run_bootstrap(tmp_path, with_pyenv=True, extra_env={"FAKE_PYENV_VER": ""}) == "path-python3"


def test_tui_bootstrap_falls_back_when_pyenv_prefix_fails(tmp_path) -> None:
    assert _run_bootstrap(tmp_path, with_pyenv=True, extra_env={"FAKE_PYENV_PREFIX": ""}) == "path-python3"


def test_tui_bootstrap_uses_path_python_without_pyenv(tmp_path) -> None:
    assert _run_bootstrap(tmp_path, with_pyenv=False, extra_env={}) == "path-python3"
