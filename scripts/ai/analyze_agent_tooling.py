#!/usr/bin/env python3
"""Baseline static checks for AI-agent tooling.

The baseline mode intentionally uses only the Python standard library. It is
meant to be safe in a fresh checkout before the CumulusCI/PyYAML environment is
installed or activated. Use ``--full-generated-reference-checks`` when you want
to exercise generators that require full YAML parsing.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent.parent
AI_DIR = ROOT / "scripts" / "ai"
MANIFEST = ROOT / ".claude" / "skill-manifest.yml"
CCI_REFERENCE_FILES = (
    ROOT / ".cursor" / "skills" / "cci-orchestration" / "tasks-reference.md",
    ROOT / ".cursor" / "skills" / "cci-orchestration" / "flows-reference.md",
    ROOT / ".cursor" / "skills" / "cci-orchestration" / "feature-flags.md",
)
BASELINE_FILES = (
    ROOT / "AGENTS.md",
    AI_DIR / "README.md",
    AI_DIR / "query_erd.py",
    AI_DIR / "generate_cci_reference.py",
    AI_DIR / "skill_manifest.py",
    MANIFEST,
    *CCI_REFERENCE_FILES,
)

FULL_CHECK_ENV_HELP = (
    "Full generated-reference checks require PyYAML/CumulusCI. Activate the "
    "project CCI environment, or install PyYAML with one of: "
    "`pipx inject cumulusci PyYAML`, `python -m pip install PyYAML`, or "
    "`python -m pip install cumulusci`."
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _stdlib_module_names() -> set[str]:
    names = set(getattr(sys, "stdlib_module_names", set()))
    names.update(sys.builtin_module_names)
    # Python packaging can expose platform-specific stdlib names; include the
    # modules this script uses so the check remains stable on supported Python.
    names.update({"argparse", "ast", "dataclasses", "pathlib", "subprocess", "typing"})
    return names


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    return imports


def check_required_files() -> CheckResult:
    missing = [_display_path(path) for path in BASELINE_FILES if not path.is_file()]
    if missing:
        return CheckResult("required files", False, "missing: " + ", ".join(missing))
    return CheckResult("required files", True, f"found {len(BASELINE_FILES)} baseline files")


def check_python_syntax() -> CheckResult:
    failures: list[str] = []
    for path in sorted(AI_DIR.glob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"{_display_path(path)}:{exc.lineno}: {exc.msg}")
    if failures:
        return CheckResult("python syntax", False, "; ".join(failures))
    return CheckResult("python syntax", True, "all scripts/ai/*.py files parse with ast")


def check_baseline_imports() -> CheckResult:
    path = AI_DIR / "analyze_agent_tooling.py"
    imports = _top_level_imports(path)
    external = sorted(imports - _stdlib_module_names())
    if external:
        return CheckResult(
            "baseline imports",
            False,
            f"{_display_path(path)} imports non-stdlib modules: {', '.join(external)}",
        )
    return CheckResult("baseline imports", True, "analyze_agent_tooling.py uses stdlib imports only")


def check_optional_dependency_messages() -> CheckResult:
    expected = {
        AI_DIR / "generate_cci_reference.py": ["PyYAML", "pipx inject cumulusci PyYAML"],
        AI_DIR / "skill_manifest.py": ["PyYAML", "minimal fallback"],
    }
    missing: list[str] = []
    for path, needles in expected.items():
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                missing.append(f"{_display_path(path)} missing {needle!r}")
    if missing:
        return CheckResult("dependency guidance", False, "; ".join(missing))
    return CheckResult("dependency guidance", True, "PyYAML/CCI activation guidance is present")


def check_manifest_high_level_keys() -> CheckResult:
    text = MANIFEST.read_text(encoding="utf-8")
    required = ("manifest_version:", "foundations:", "pmos:", "skills:", "grounding:")
    missing = [key for key in required if key not in text]
    if missing:
        return CheckResult("manifest baseline", False, "missing high-level keys: " + ", ".join(missing))
    return CheckResult("manifest baseline", True, "manifest has required high-level keys")


def check_generated_reference_presence() -> CheckResult:
    failures: list[str] = []
    for path in CCI_REFERENCE_FILES:
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if "Auto-generated" not in text or "scripts/ai/generate_cci_reference.py" not in text:
            failures.append(_display_path(path))
    if failures:
        return CheckResult("generated reference markers", False, "missing generator marker: " + ", ".join(failures))
    return CheckResult("generated reference markers", True, "CCI reference files identify their generator")


def check_readme_explains_check_modes() -> CheckResult:
    text = (AI_DIR / "README.md").read_text(encoding="utf-8")
    required = ("baseline static checks", "full generated-reference checks")
    missing = [phrase for phrase in required if phrase not in text.lower()]
    if missing:
        return CheckResult("README check modes", False, "missing phrases: " + ", ".join(missing))
    return CheckResult("README check modes", True, "README documents baseline vs full check modes")


def run_baseline_checks() -> list[CheckResult]:
    return [
        check_required_files(),
        check_python_syntax(),
        check_baseline_imports(),
        check_optional_dependency_messages(),
        check_manifest_high_level_keys(),
        check_generated_reference_presence(),
        check_readme_explains_check_modes(),
    ]


def run_full_generated_reference_check() -> CheckResult:
    if importlib.util.find_spec("yaml") is None:
        return CheckResult("full generated-reference dry run", False, FULL_CHECK_ENV_HELP)
    cmd = [sys.executable, str(AI_DIR / "generate_cci_reference.py"), "--dry-run"]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "generator returned non-zero exit").strip()
        return CheckResult("full generated-reference dry run", False, detail)
    return CheckResult("full generated-reference dry run", True, "generate_cci_reference.py --dry-run completed")


def print_results(results: Iterable[CheckResult]) -> int:
    overall_ok = True
    for result in results:
        marker = "PASS" if result.ok else "FAIL"
        print(f"[{marker}] {result.name}: {result.detail}")
        overall_ok = overall_ok and result.ok
    return 0 if overall_ok else 1


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run AI-agent tooling checks. Baseline mode uses only Python stdlib."
    )
    parser.add_argument(
        "--full-generated-reference-checks",
        action="store_true",
        help="also dry-run CCI reference generation (requires PyYAML/CumulusCI)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    results = run_baseline_checks()
    if args.full_generated_reference_checks:
        results.append(run_full_generated_reference_check())
    return print_results(results)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
