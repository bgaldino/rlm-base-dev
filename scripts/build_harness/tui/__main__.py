"""Module entrypoint for the CCI build manager TUI."""

from __future__ import annotations

import sys

def main() -> int:
    try:
        from scripts.build_harness.tui.app import BuildManagerApp
    except ModuleNotFoundError as exc:
        if exc.name in {"textual", "yaml"}:
            print(
                "Missing dependency for TUI startup. Install with "
                "`scripts/build_harness/tui/.venv/bin/python -m pip install -r scripts/build_harness/tui/requirements.txt`.",
                file=sys.stderr,
            )
            return 2
        raise

    app = BuildManagerApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
