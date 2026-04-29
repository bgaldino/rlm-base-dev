#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$ROOT_DIR/scripts/build_harness/tui/.venv/bin/python"
REQ_FILE="$ROOT_DIR/scripts/build_harness/tui/requirements.txt"

# VS Code/Cursor can fail shell-environment resolution when SHELL is unset or invalid.
if [[ -z "${SHELL:-}" || ! -x "${SHELL:-}" ]]; then
  if [[ -x "/bin/zsh" ]]; then
    export SHELL="/bin/zsh"
  elif [[ -x "/bin/bash" ]]; then
    export SHELL="/bin/bash"
  fi
fi

# Textual requires an interactive TTY; avoid blank output in non-interactive contexts.
if [[ ! -t 1 ]]; then
  echo "This TUI requires an interactive terminal."
  echo "Run it from a local terminal or VS Code integrated terminal."
  exit 1
fi

# Ensure TERM is set for full-screen rendering.
if [[ -z "${TERM:-}" || "${TERM:-}" == "dumb" ]]; then
  export TERM="xterm-256color"
fi

restore_terminal() {
  stty sane 2>/dev/null || true
  printf '\033[?25h\033[?1049l' || true
}

trap restore_terminal EXIT INT TERM

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Creating scoped TUI virtual environment..."
  python -m venv "$ROOT_DIR/scripts/build_harness/tui/.venv"
  "$VENV_PYTHON" -m pip install -r "$REQ_FILE"
fi

if ! "$VENV_PYTHON" -c "import textual, yaml" >/dev/null 2>&1; then
  echo "Installing/updating TUI dependencies..."
  "$VENV_PYTHON" -m pip install -r "$REQ_FILE"
fi

"$VENV_PYTHON" -m scripts.build_harness.tui "$@"
