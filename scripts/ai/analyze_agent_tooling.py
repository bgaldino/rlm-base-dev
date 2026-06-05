#!/usr/bin/env python3
"""Static checks for repository agent-tooling guidance.

The script intentionally uses only the Python standard library so scheduled
workflows can run in static-only mode without installing Salesforce, CumulusCI,
or other project dependencies.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = REPO_ROOT / "reports" / "agent-tooling-optimization"


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def status(ok: bool) -> str:
    return "pass" if ok else "fail"


def check_paths(paths: Iterable[str], category: str) -> list[dict[str, str | bool]]:
    results: list[dict[str, str | bool]] = []
    for raw_path in sorted(set(paths)):
        path = REPO_ROOT / raw_path
        results.append(
            {
                "category": category,
                "check": f"{raw_path} exists",
                "status": status(path.exists()),
                "path": raw_path,
            }
        )
    return results


def extract_agent_references(agent_text: str) -> list[str]:
    """Return path-like backtick references from AGENTS.md."""
    references: list[str] = []
    prefixes = (
        ".cursor/",
        ".github/",
        "docs/",
        "scripts/",
        "tasks/",
        "tests/",
        "robot/",
    )
    for match in re.finditer(r"`([^`]+)`", agent_text):
        token = match.group(1).strip()
        if token.startswith(prefixes) and not any(ch.isspace() for ch in token):
            references.append(token)
    return references


def check_python_syntax(paths: Iterable[Path]) -> list[dict[str, str | bool]]:
    results: list[dict[str, str | bool]] = []
    for path in sorted(paths):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            results.append(
                {
                    "category": "python-syntax",
                    "check": f"{rel(path)} parses",
                    "status": "fail",
                    "path": rel(path),
                    "message": f"{exc.msg} at line {exc.lineno}",
                }
            )
        else:
            results.append(
                {
                    "category": "python-syntax",
                    "check": f"{rel(path)} parses",
                    "status": "pass",
                    "path": rel(path),
                }
            )
    return results


def write_reports(report_dir: Path, results: list[dict[str, str | bool]]) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    failures = [item for item in results if item["status"] != "pass"]

    payload = {
        "generated_at": generated_at,
        "summary": {
            "checks": len(results),
            "failures": len(failures),
        },
        "results": results,
    }
    (report_dir / "agent-tooling-analysis.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Agent Tooling Analysis",
        "",
        f"Generated at: `{generated_at}`",
        "",
        "## Summary",
        "",
        f"- Checks: {len(results)}",
        f"- Failures: {len(failures)}",
        "",
        "## Results",
        "",
        "| Status | Category | Check |",
        "| --- | --- | --- |",
    ]
    for item in results:
        icon = "✅" if item["status"] == "pass" else "❌"
        lines.append(f"| {icon} | {item['category']} | {item['check']} |")
    lines.append("")
    (report_dir / "agent-tooling-analysis.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> int:
    report_dir = Path(os.environ.get("REPORT_DIR", DEFAULT_REPORT_DIR)).resolve()
    agent_path = REPO_ROOT / "AGENTS.md"
    results: list[dict[str, str | bool]] = [
        {
            "category": "entrypoint",
            "check": "AGENTS.md exists",
            "status": status(agent_path.exists()),
            "path": "AGENTS.md",
        },
        {
            "category": "entrypoint",
            "check": ".github/copilot-instructions.md exists",
            "status": status((REPO_ROOT / ".github/copilot-instructions.md").exists()),
            "path": ".github/copilot-instructions.md",
        },
    ]

    if agent_path.exists():
        agent_text = agent_path.read_text(encoding="utf-8")
        results.extend(check_paths(extract_agent_references(agent_text), "agent-reference"))

    results.extend(check_python_syntax((REPO_ROOT / "scripts" / "ai").glob("*.py")))
    write_reports(report_dir, results)

    failures = [item for item in results if item["status"] != "pass"]
    if failures:
        print(f"Agent tooling analysis found {len(failures)} failure(s).", file=sys.stderr)
        print(f"Reports written to {report_dir}", file=sys.stderr)
        return 1

    print(f"Agent tooling analysis passed with {len(results)} checks.")
    print(f"Reports written to {report_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
