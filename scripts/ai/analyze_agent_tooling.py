#!/usr/bin/env python3
"""Analyze the repository's AI-agent tooling surface.

This is the single, tool-agnostic analyzer for the repo's AI-agent layer. It
exposes positional subcommands (mirroring ``scripts/ai/query_erd.py``):

  check     stdlib-only pass/fail gate (default). Safe in a fresh checkout
            before CumulusCI/PyYAML are installed; exits non-zero on failure.
  report    rich Markdown report + JSON scorecard of the tooling surface.
  coverage  Cursor rule / skill coverage matrix and gap analysis.
  all       run check, then report, then coverage.

Design contract:
  * The module imports ONLY the Python standard library at import time, so the
    ``check`` gate runs with no third-party dependencies. The ``check`` gate
    self-verifies this invariant.
  * PyYAML, when installed, is loaded lazily (via importlib, guarded against
    import failure) to enrich ``report``/``coverage``. Without it, a
    conservative line-oriented fallback is used.
  * Written artifacts are deterministic (no embedded wall-clock timestamps) so
    scheduled regeneration only produces a diff on a real change.

Outputs:
  report   -> docs/analysis/tooling-optimization-report.md
              .agents/context/tooling-scorecard.json
  coverage -> .agents/context/rule-skill-coverage.md
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Repo-relative path constants (resolved against a repo root computed at runtime)
# ---------------------------------------------------------------------------

REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".claude/skill-manifest.yml",
    ".cursor/skills/README.md",
    "scripts/ai/README.md",
]

GENERATED_CCI_REFERENCE_FILES = [
    ".cursor/skills/cci-orchestration/tasks-reference.md",
    ".cursor/skills/cci-orchestration/flows-reference.md",
    ".cursor/skills/cci-orchestration/feature-flags.md",
]

# Files whose presence the baseline gate asserts, beyond REQUIRED_FILES.
BASELINE_EXTRA_FILES = [
    "scripts/ai/query_erd.py",
    "scripts/ai/generate_cci_reference.py",
    "scripts/ai/skill_manifest.py",
]

MANIFEST_PATH = ".claude/skill-manifest.yml"
AGENTS_PATH = "AGENTS.md"
SKILLS_ROOT = ".cursor/skills"
RULES_ROOT = ".cursor/rules"
SKILLS_README = ".cursor/skills/README.md"
AI_README = "scripts/ai/README.md"

REPORT_PATH = "docs/analysis/tooling-optimization-report.md"
SCORECARD_PATH = ".agents/context/tooling-scorecard.json"
COVERAGE_PATH = ".agents/context/rule-skill-coverage.md"

# A backtick-wrapped token that points at a Markdown file, e.g. `foo/bar.md`.
BACKTICK_MD_RE = re.compile(r"`([^`]+\.md)`")
FENCE_RE = re.compile(r"^\s*```")

FULL_CHECK_ENV_HELP = (
    "Full generated-reference checks require PyYAML/CumulusCI. Activate the "
    "project CCI environment, or install PyYAML with one of: "
    "`pipx inject cumulusci PyYAML`, `python -m pip install PyYAML`, or "
    "`python -m pip install cumulusci`."
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def find_repo_root(start: Path | None = None) -> Path:
    """Return the repo root.

    Prefer walking up to a directory that has both AGENTS.md and .git; fall
    back to the script's grandparent (scripts/ai/<file> -> repo root).
    """
    if start is None:
        start = Path(__file__).resolve().parent
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    # Fallback: this file lives at <root>/scripts/ai/analyze_agent_tooling.py.
    here = Path(__file__).resolve()
    if len(here.parents) >= 3:
        return here.parents[2]
    return start


def read_text(path: Path, default: str = "") -> str:
    """Read UTF-8 text, returning ``default`` for missing/unreadable files."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return default


def posix(path: Path) -> str:
    return path.as_posix()


def rel(path: Path, root: Path) -> str:
    """Repo-relative POSIX path when possible, else the absolute POSIX path."""
    try:
        return posix(path.relative_to(root))
    except ValueError:
        return posix(path)


def repo_relative(root: Path, reference: str) -> Path:
    """Resolve a repo-relative reference, neutralizing a stray leading slash.

    ``root / "/abs"`` would discard ``root`` under pathlib semantics, so a
    leading slash is treated as repo-relative rather than filesystem-absolute.
    """
    return root / reference.lstrip("/")


def path_reference_exists(root: Path, reference: str) -> bool:
    if any(ch in reference for ch in "*{}"):
        # Glob/template tokens are matched against the filesystem, not stat'd.
        return bool(list(root.glob(reference.lstrip("/"))))
    return repo_relative(root, reference).is_file()


def strip_fenced_code(text: str) -> str:
    """Remove fenced code blocks so their contents are not parsed as prose."""
    kept: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return "\n".join(kept)


def looks_like_concrete_path(token: str) -> bool:
    """True for a token that is a plausible concrete file path.

    Excludes glob/template tokens (``*``, ``**``, ``{version}``) and any token
    containing whitespace.
    """
    if any(ch in token for ch in "*{}"):
        return False
    if any(ch.isspace() for ch in token):
        return False
    return True


def load_yaml_optional(path: Path) -> tuple[dict[str, Any] | None, str]:
    """Load YAML with PyYAML when importable; otherwise return ``(None, label)``.

    ``find_spec`` can report a module that still fails to import (broken or
    partial install), so the actual import is guarded.
    """
    if importlib.util.find_spec("yaml") is None:
        return None, "line-oriented fallback"
    try:
        yaml = importlib.import_module("yaml")
    except ImportError:
        return None, "line-oriented fallback"
    data = yaml.safe_load(read_text(path)) or {}
    if not isinstance(data, dict):
        return {}, "PyYAML"
    return data, "PyYAML"


def stdlib_module_names() -> set[str]:
    """Best-effort set of standard-library top-level module names (3.10+)."""
    names = set(getattr(sys, "stdlib_module_names", set()))
    names.update(sys.builtin_module_names)
    # __future__ is stdlib but is sometimes excluded from stdlib_module_names.
    names.add("__future__")
    return names


def top_level_imports(path: Path) -> set[str]:
    """Module-level (import-time) imports only.

    Does NOT descend into function or class bodies, so a lazy in-function
    third-party import (e.g. an ``import yaml`` inside a report/coverage helper)
    is not counted against the stdlib-only-at-import-time contract. Imports in
    module-level ``if``/``try``/``with`` blocks still execute at import time and
    are included.
    """
    tree = ast.parse(read_text(path), filename=str(path))
    imports: set[str] = set()
    scopes = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

    def visit(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Import):
                for alias in child.names:
                    imports.add(alias.name.split(".", 1)[0])
            elif isinstance(child, ast.ImportFrom) and child.module and child.level == 0:
                imports.add(child.module.split(".", 1)[0])
            elif not isinstance(child, scopes):
                visit(child)

    visit(tree)
    return imports


def sorted_relative_files(root: Path, sub: str, pattern: str) -> list[str]:
    base = root / sub
    if not base.exists():
        return []
    return sorted(
        rel(p, root) for p in base.glob(pattern) if p.is_file()
    )


def first_level_skill_dirs(root: Path) -> set[str]:
    base = root / SKILLS_ROOT
    if not base.is_dir():
        return set()
    return {p.name for p in base.iterdir() if p.is_dir()}


# ---------------------------------------------------------------------------
# Manifest summary (shared by report)
# ---------------------------------------------------------------------------


def parse_manifest_fallback(text: str) -> dict[str, Any]:
    """Conservative line parser for Foundations manifest metadata.

    Top-level scalar metadata is read only from unindented lines, so identical
    keys nested under ``pmos:`` cannot overwrite the Foundations values. Skill
    ids are limited to the ``foundations:`` section so PMOS skill ids do not
    inflate this repo's local count.
    """
    summary: dict[str, Any] = {"skills": [], "skill_paths": [], "auto_generated_subfiles": []}

    foundations_text = text
    foundations_match = re.search(r"(?ms)^foundations:\n(?P<body>.*?)(?=^\S|\Z)", text)
    if foundations_match:
        foundations_text = foundations_match.group("body")

    for line in text.splitlines():
        # Top-level scalars only (no leading whitespace).
        if line[:1].isspace():
            continue
        for key in ("manifest_version", "generated_at", "last_verified", "salesforce_release_active"):
            prefix = key + ":"
            if line.startswith(prefix):
                summary[key] = line[len(prefix):].strip().strip('"').strip("'")

    for line in foundations_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            summary["skills"].append(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("path: .cursor/skills/"):
            summary["skill_paths"].append(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("- .cursor/skills/cci-orchestration/"):
            summary["auto_generated_subfiles"].append(stripped[2:].strip())
    return summary


def summarize_manifest(root: Path) -> dict[str, Any]:
    manifest = root / MANIFEST_PATH
    if not manifest.is_file():
        return {"present": False, "parser": "not run"}

    data, parser = load_yaml_optional(manifest)
    if data is not None:
        foundations = data.get("foundations") or {}
        if not isinstance(foundations, dict):
            foundations = {}
        skills = foundations.get("skills") or []
        if not isinstance(skills, list):
            skills = []
        skill_ids = [s.get("id") for s in skills if isinstance(s, dict) and s.get("id")]
        skill_paths = [s.get("path") for s in skills if isinstance(s, dict) and s.get("path")]
        generated_subfiles: list[str] = []
        for s in skills:
            if isinstance(s, dict):
                generated_subfiles.extend(s.get("auto_generated_subfiles") or [])
        return {
            "present": True,
            "parser": parser,
            "manifest_version": _scalar(data.get("manifest_version")),
            "generated_at": _scalar(data.get("generated_at")),
            "last_verified": _scalar(data.get("last_verified")),
            "salesforce_release_active": _scalar(data.get("salesforce_release_active")),
            "skill_count": len(skill_ids),
            "skill_ids": sorted(str(s) for s in skill_ids),
            "skill_paths": sorted(str(p) for p in skill_paths),
            "auto_generated_subfiles": sorted(str(p) for p in generated_subfiles),
        }

    fb = parse_manifest_fallback(read_text(manifest))
    return {
        "present": True,
        "parser": parser,
        "manifest_version": fb.get("manifest_version"),
        "generated_at": fb.get("generated_at"),
        "last_verified": fb.get("last_verified"),
        "salesforce_release_active": fb.get("salesforce_release_active"),
        "skill_count": len(fb.get("skills", [])),
        "skill_ids": sorted(fb.get("skills", [])),
        "skill_paths": sorted(fb.get("skill_paths", [])),
        "auto_generated_subfiles": sorted(fb.get("auto_generated_subfiles", [])),
    }


def _scalar(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


# ===========================================================================
# Subcommand: check  (stdlib-only pass/fail gate)
# ===========================================================================


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    skipped: bool = False


def check_required_files(root: Path) -> CheckResult:
    targets = REQUIRED_FILES + BASELINE_EXTRA_FILES + GENERATED_CCI_REFERENCE_FILES
    missing = [t for t in targets if not (root / t).is_file()]
    if missing:
        return CheckResult("required files", False, "missing: " + ", ".join(sorted(missing)))
    return CheckResult("required files", True, f"found {len(targets)} baseline files")


def check_python_syntax(root: Path) -> CheckResult:
    ai_dir = root / "scripts" / "ai"
    failures: list[str] = []
    for path in sorted(ai_dir.glob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"{rel(path, root)}:{exc.lineno}: {exc.msg}")
        except (OSError, UnicodeDecodeError) as exc:
            failures.append(f"{rel(path, root)}: unreadable ({exc.__class__.__name__})")
    if failures:
        return CheckResult("python syntax", False, "; ".join(failures))
    return CheckResult("python syntax", True, "all scripts/ai/*.py parse with ast")


def check_baseline_imports(root: Path) -> CheckResult:
    path = root / "scripts" / "ai" / "analyze_agent_tooling.py"
    if not path.is_file():
        return CheckResult("baseline imports", False, f"missing {rel(path, root)}")
    try:
        imports = top_level_imports(path)
    except (SyntaxError, OSError, UnicodeDecodeError) as exc:
        return CheckResult("baseline imports", False, f"could not parse imports: {exc}")
    external = sorted(imports - stdlib_module_names())
    if external:
        return CheckResult(
            "baseline imports", False,
            f"analyze_agent_tooling.py imports non-stdlib modules: {', '.join(external)}",
        )
    return CheckResult("baseline imports", True, "analyze_agent_tooling.py uses stdlib imports only")


def check_optional_dependency_messages(root: Path) -> CheckResult:
    expected = {
        "scripts/ai/generate_cci_reference.py": ["PyYAML"],
        "scripts/ai/skill_manifest.py": ["PyYAML", "minimal fallback"],
    }
    missing: list[str] = []
    for rel_path, needles in expected.items():
        path = root / rel_path
        if not path.is_file():
            missing.append(f"{rel_path} missing")
            continue
        text = read_text(path)
        for needle in needles:
            if needle not in text:
                missing.append(f"{rel_path} missing {needle!r}")
    if missing:
        return CheckResult("dependency guidance", False, "; ".join(missing))
    return CheckResult("dependency guidance", True, "PyYAML/CCI activation guidance is present")


def check_manifest_high_level_keys(root: Path) -> CheckResult:
    manifest = root / MANIFEST_PATH
    if not manifest.is_file():
        return CheckResult("manifest baseline", False, f"missing {MANIFEST_PATH}")
    text = read_text(manifest)
    required = ("manifest_version:", "foundations:", "pmos:", "skills:", "grounding:")
    missing = [k for k in required if k not in text]
    if missing:
        return CheckResult("manifest baseline", False, "missing high-level keys: " + ", ".join(missing))
    return CheckResult("manifest baseline", True, "manifest has required high-level keys")


def check_generated_reference_presence(root: Path) -> CheckResult:
    absent: list[str] = []
    unmarked: list[str] = []
    for rel_path in GENERATED_CCI_REFERENCE_FILES:
        path = root / rel_path
        if not path.is_file():
            absent.append(rel_path)
            continue
        text = read_text(path)
        if "Auto-generated" not in text or "scripts/ai/generate_cci_reference.py" not in text:
            unmarked.append(rel_path)
    if absent or unmarked:
        parts = []
        if absent:
            parts.append("absent: " + ", ".join(absent))
        if unmarked:
            parts.append("missing generator marker: " + ", ".join(unmarked))
        return CheckResult("generated reference markers", False, "; ".join(parts))
    return CheckResult("generated reference markers", True, "CCI reference files identify their generator")


def check_readme_explains_check_modes(root: Path) -> CheckResult:
    path = root / AI_README
    if not path.is_file():
        return CheckResult("README check modes", False, f"missing {AI_README}")
    text = read_text(path).lower()
    # Accept singular or plural ("check" / "checks") to avoid brittle matching.
    patterns = {
        "baseline static check": r"baseline static checks?",
        "full generated-reference check": r"full generated-reference checks?",
    }
    missing = [label for label, pat in patterns.items() if not re.search(pat, text)]
    if missing:
        return CheckResult("README check modes", False, "missing phrases: " + ", ".join(missing))
    return CheckResult("README check modes", True, "README documents baseline vs full check modes")


def run_baseline_checks(root: Path) -> list[CheckResult]:
    return [
        check_required_files(root),
        check_python_syntax(root),
        check_baseline_imports(root),
        check_optional_dependency_messages(root),
        check_manifest_high_level_keys(root),
        check_generated_reference_presence(root),
        check_readme_explains_check_modes(root),
    ]


def run_full_generated_reference_check(root: Path) -> CheckResult:
    if importlib.util.find_spec("yaml") is None:
        # Skip (do not fail) when PyYAML is absent — this opt-in deeper check
        # requires it, and the README documents it as skipped with guidance.
        return CheckResult("full generated-reference dry run", True, FULL_CHECK_ENV_HELP, skipped=True)
    script = root / "scripts" / "ai" / "generate_cci_reference.py"
    cmd = [sys.executable, str(script), "--dry-run"]
    try:
        proc = subprocess.run(
            cmd, cwd=str(root), text=True, capture_output=True, check=False, timeout=300
        )
    except subprocess.TimeoutExpired:
        return CheckResult("full generated-reference dry run", False, "generator timed out after 300s")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "generator returned non-zero exit").strip()
        return CheckResult("full generated-reference dry run", False, detail)
    return CheckResult("full generated-reference dry run", True, "generate_cci_reference.py --dry-run completed")


def cmd_check(root: Path, full_generated_reference_checks: bool) -> int:
    results = run_baseline_checks(root)
    if full_generated_reference_checks:
        results.append(run_full_generated_reference_check(root))
    overall_ok = True
    skipped = 0
    for result in results:
        if result.skipped:
            marker = "SKIP"
            skipped += 1
        else:
            marker = "PASS" if result.ok else "FAIL"
        print(f"[{marker}] {result.name}: {result.detail}")
        overall_ok = overall_ok and result.ok
    failing = sum(1 for r in results if not r.ok)
    suffix = f", {skipped} skipped" if skipped else ""
    print(f"Status: {'PASS' if overall_ok else 'FAIL'} "
          f"({failing} failing of {len(results)} checks{suffix})")
    return 0 if overall_ok else 1


# ===========================================================================
# Subcommand: report  (rich Markdown report + JSON scorecard)
# ===========================================================================


@dataclass
class FileCheck:
    name: str
    ok: bool
    detail: str


@dataclass
class RuleMapping:
    rule: str
    status: str  # skill | standalone | missing
    target: str


@dataclass
class Analysis:
    root: Path
    required_files: list[FileCheck] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    agents_skill_references: list[str] = field(default_factory=list)
    missing_agents_skill_references: list[str] = field(default_factory=list)
    rule_mappings: list[RuleMapping] = field(default_factory=list)
    cci_reference_files: list[FileCheck] = field(default_factory=list)
    manifest_summary: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def errors(self) -> list[str]:
        out: list[str] = []
        out.extend(c.detail for c in self.required_files if not c.ok)
        out.extend(c.detail for c in self.cci_reference_files if not c.ok)
        out.extend(
            f"AGENTS.md references missing skill file or unmatched glob: {p}"
            for p in self.missing_agents_skill_references
        )
        out.extend(
            f"{m.rule} has no corresponding skill or stand-alone note"
            for m in self.rule_mappings if m.status == "missing"
        )
        return out

    @property
    def passed(self) -> bool:
        return not self.errors


def extract_agents_skill_references(agents_text: str, root: Path) -> list[str]:
    """Advertised ``.cursor/skills/*.md`` references from AGENTS.md prose.

    Fenced code blocks are stripped first, and glob/template tokens are
    ignored, so only concrete skill-file references are checked.
    """
    skill_dirs = first_level_skill_dirs(root)
    prose = strip_fenced_code(agents_text)
    refs: set[str] = set()
    for match in BACKTICK_MD_RE.finditer(prose):
        token = match.group(1).strip()
        if not looks_like_concrete_path(token):
            continue
        if token.startswith(".cursor/skills/"):
            refs.add(token)
            continue
        if token.startswith(("docs/", ".github/", ".claude/", "scripts/", "templates/")):
            continue
        first = token.split("/", 1)[0]
        if "/" in token and first in skill_dirs:
            refs.add(f".cursor/skills/{token}")
    return sorted(refs)


def normalize_equivalent_skill(cell: str) -> tuple[str, str]:
    lowered = cell.lower()
    if "stand-alone" in lowered or "standalone" in lowered:
        return "standalone", cell.strip()
    # Prefer a backtick token that names a Markdown skill file; fall back to the
    # first backtick token only if no `.md` reference is present. This avoids
    # mis-reading an incidental non-skill token earlier in the cell.
    md_match = re.search(r"`([^`]+\.md)`", cell)
    match = md_match or re.search(r"`([^`]+)`", cell)
    if not match:
        return "missing", cell.strip()
    ref = match.group(1).strip()
    if ref.startswith(".cursor/skills/"):
        return "skill", ref
    if ref.endswith(".md"):
        return "skill", f".cursor/skills/{ref}"
    return "missing", ref


def split_table_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return all(set(c) <= set("-: ") and c for c in cells) if cells else False


def extract_rule_mappings(agents_text: str, rules: Iterable[str]) -> list[RuleMapping]:
    by_rule: dict[str, tuple[str, str]] = {}
    for line in agents_text.splitlines():
        if not line.lstrip().startswith("|") or ".mdc" not in line:
            continue
        cells = split_table_row(line)
        if len(cells) < 3 or is_separator_row(cells):
            continue
        rule_match = re.search(r"`?([^`\s|]+\.mdc)`?", cells[0])
        if not rule_match:
            continue
        rule = Path(rule_match.group(1)).name
        kind, target = normalize_equivalent_skill(cells[-1])
        by_rule[rule] = (kind, target)

    results: list[RuleMapping] = []
    for rule_path in rules:
        name = Path(rule_path).name
        if name not in by_rule:
            results.append(RuleMapping(name, "missing", "No row in AGENTS.md File-Specific Rules table"))
            continue
        kind, target = by_rule[name]
        results.append(RuleMapping(name, kind, target))
    return sorted(results, key=lambda m: m.rule)


def analyze(root: Path) -> Analysis:
    analysis = Analysis(root=root)

    for rel_path in REQUIRED_FILES:
        exists = (root / rel_path).is_file()
        analysis.required_files.append(
            FileCheck(rel_path, exists, f"Found {rel_path}" if exists else f"Missing required file: {rel_path}")
        )

    analysis.skills = sorted_relative_files(root, SKILLS_ROOT, "**/*.md")
    analysis.rules = sorted_relative_files(root, RULES_ROOT, "*.mdc")

    agents_text = read_text(root / AGENTS_PATH)
    analysis.agents_skill_references = extract_agents_skill_references(agents_text, root)
    analysis.missing_agents_skill_references = [
        r for r in analysis.agents_skill_references if not path_reference_exists(root, r)
    ]
    analysis.rule_mappings = extract_rule_mappings(agents_text, analysis.rules)

    for rel_path in GENERATED_CCI_REFERENCE_FILES:
        exists = (root / rel_path).is_file()
        analysis.cci_reference_files.append(
            FileCheck(rel_path, exists, f"Found {rel_path}" if exists else f"Missing generated CCI reference file: {rel_path}")
        )

    analysis.manifest_summary = summarize_manifest(root)
    manifest_skill_paths = analysis.manifest_summary.get("skill_paths", []) or []
    missing_paths = [p for p in manifest_skill_paths if not path_reference_exists(root, p)]
    if missing_paths:
        analysis.warnings.append("Manifest references missing skill paths: " + ", ".join(sorted(missing_paths)))

    return analysis


def _icon(ok: bool) -> str:
    return "✅" if ok else "❌"


def render_report_markdown(a: Analysis) -> str:
    lines: list[str] = [
        "# Agent Tooling Optimization Report",
        "",
        "> **Auto-generated** by `scripts/ai/analyze_agent_tooling.py report`.",
        "> Do not edit manually — re-run the analyzer after changing agent docs,",
        "> skills, rules, or the skill manifest.",
        "",
        "## Summary",
        "",
        f"- Overall status: **{'PASS' if a.passed else 'FAIL'}**",
        f"- Required files: **{sum(1 for c in a.required_files if c.ok)}/{len(a.required_files)}** present",
        f"- Skills inventoried: **{len(a.skills)}** Markdown files under `.cursor/skills/`",
        f"- Cursor rules inventoried: **{len(a.rules)}** `.mdc` files under `.cursor/rules/`",
        f"- AGENTS.md skill references: **{len(a.agents_skill_references)}** checked, "
        f"**{len(a.missing_agents_skill_references)}** missing",
        f"- Generated CCI references: **{sum(1 for c in a.cci_reference_files if c.ok)}/"
        f"{len(a.cci_reference_files)}** present",
        f"- Errors: **{len(a.errors)}**",
        f"- Warnings: **{len(a.warnings)}**",
        "",
        "## Required Agent Entry Points",
        "",
    ]
    for c in a.required_files:
        lines.append(f"- {_icon(c.ok)} `{c.name}` — {c.detail}")

    lines += ["", "## Skill Inventory", ""]
    lines += [f"- `{s}`" for s in a.skills] or ["- (none found)"]

    lines += ["", "## Cursor Rule Inventory", ""]
    lines += [f"- `{r}`" for r in a.rules] or ["- (none found)"]

    lines += ["", "## AGENTS.md Skill Reference Check", ""]
    for ref in a.agents_skill_references:
        ok = ref not in a.missing_agents_skill_references
        lines.append(f"- {_icon(ok)} `{ref}`")
    if not a.agents_skill_references:
        lines.append("- (no concrete skill references found)")

    lines += [
        "", "## Cursor Rule Coverage", "",
        "Each `.cursor/rules/*.mdc` is checked against the AGENTS.md File-Specific "
        "Rules table for an equivalent skill or an explicit stand-alone note. See "
        "`.agents/context/rule-skill-coverage.md` for the full coverage matrix and "
        "recommendations.", "",
    ]
    for m in a.rule_mappings:
        if m.status == "skill":
            lines.append(f"- ✅ `{m.rule}` — mapped to `{m.target}`")
        elif m.status == "standalone":
            lines.append(f"- ✅ `{m.rule}` — explicit stand-alone note")
        else:
            lines.append(f"- ❌ `{m.rule}` — {m.target}")

    lines += ["", "## Generated CCI Reference Files", ""]
    for c in a.cci_reference_files:
        lines.append(f"- {_icon(c.ok)} `{c.name}` — {c.detail}")

    m = a.manifest_summary
    lines += [
        "", "## Skill Manifest Snapshot", "",
        f"- Present: **{m.get('present', False)}**",
        f"- Parser: `{m.get('parser', 'unknown')}`",
        f"- Manifest version: `{m.get('manifest_version')}`",
        f"- Last verified: `{m.get('last_verified')}`",
        f"- Active Salesforce release: `{m.get('salesforce_release_active')}`",
        f"- Manifest skill count: **{m.get('skill_count', 0)}**",
    ]
    for sid in m.get("skill_ids", []) or []:
        lines.append(f"  - `{sid}`")

    lines += ["", "## Findings", ""]
    if a.errors:
        lines += ["### Errors", ""]
        lines += [f"- ❌ {e}" for e in a.errors]
    else:
        lines.append("- ✅ No blocking errors found.")
    if a.warnings:
        lines += ["", "### Warnings", ""]
        lines += [f"- ⚠️ {w}" for w in a.warnings]

    lines += [
        "", "## Notes", "",
        "- Generated by `scripts/ai/analyze_agent_tooling.py report`.",
        "- The analyzer needs no third-party dependencies. With PyYAML installed, "
        "manifest reporting is richer; otherwise a line-oriented fallback is used.",
        "",
    ]
    return "\n".join(lines)


def to_scorecard(a: Analysis) -> dict[str, Any]:
    return {
        "status": "pass" if a.passed else "fail",
        "counts": {
            "required_files_present": sum(1 for c in a.required_files if c.ok),
            "required_files_total": len(a.required_files),
            "skills_markdown_files": len(a.skills),
            "cursor_rules": len(a.rules),
            "agents_skill_references": len(a.agents_skill_references),
            "missing_agents_skill_references": len(a.missing_agents_skill_references),
            "generated_cci_reference_files_present": sum(1 for c in a.cci_reference_files if c.ok),
            "generated_cci_reference_files_total": len(a.cci_reference_files),
            "errors": len(a.errors),
            "warnings": len(a.warnings),
        },
        "required_files": {c.name: c.ok for c in a.required_files},
        "skills": a.skills,
        "rules": a.rules,
        "agents_skill_references": {
            "checked": a.agents_skill_references,
            "missing": a.missing_agents_skill_references,
        },
        "rule_mappings": [
            {"rule": m.rule, "status": m.status, "target": m.target} for m in a.rule_mappings
        ],
        "generated_cci_reference_files": {c.name: c.ok for c in a.cci_reference_files},
        "manifest": a.manifest_summary,
        "errors": a.errors,
        "warnings": a.warnings,
    }


def cmd_report(root: Path, do_check: bool, do_json: bool) -> int:
    a = analyze(root)
    report = root / REPORT_PATH
    scorecard = root / SCORECARD_PATH
    report.parent.mkdir(parents=True, exist_ok=True)
    scorecard.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_report_markdown(a), encoding="utf-8")
    scorecard.write_text(json.dumps(to_scorecard(a), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if do_json:
        print(json.dumps(to_scorecard(a), indent=2, sort_keys=True))
    else:
        print(f"Wrote {REPORT_PATH}")
        print(f"Wrote {SCORECARD_PATH}")
        print(f"Status: {'PASS' if a.passed else 'FAIL'} ({len(a.errors)} errors, {len(a.warnings)} warnings)")

    if do_check and not a.passed:
        return 1
    return 0


# ===========================================================================
# Subcommand: coverage  (rule / skill coverage matrix)
# ===========================================================================

COVERAGE_HEADER = (
    "> **Auto-generated** by `scripts/ai/analyze_agent_tooling.py coverage`.\n"
    "> Do not edit manually — re-run the analyzer after changing `AGENTS.md`, "
    "`.cursor/rules/`, or `.cursor/skills/README.md`."
)


@dataclass(frozen=True)
class RuleInfo:
    path: str
    name: str
    globs: tuple[str, ...]
    equivalent_skill: str
    has_do_not: bool
    appears_in_agents: bool
    listed_in_skill_readme: bool
    owner: str


@dataclass(frozen=True)
class RecommendedSkillRule:
    skill_path: str
    suggested_rule: str
    suggested_globs: tuple[str, ...]
    owner: str
    reason: str


@dataclass(frozen=True)
class HighRiskPath:
    path: str
    owner: str
    source: str
    expected_rule: str
    explicit_analyzer_check: str
    reason: str


RECOMMENDED_SKILL_RULES: tuple[RecommendedSkillRule, ...] = (
    RecommendedSkillRule("schema-validation/SKILL.md", "schema-validation.mdc",
        ("docs/erds/**", "scripts/erd/**/*.py"), "Schema Validation",
        "ERD/schema files are safety-critical and the skill has no file-triggered rule today."),
    RecommendedSkillRule("release-enablement/SKILL.md", "release-enablement.mdc",
        ("docs/enablement/**", "docs/salesforce/**"), "Release Enablement",
        "Enablement docs have release-specific source/extract conventions that are easy to miss."),
    RecommendedSkillRule("rlm-business-apis/SKILL.md", "rlm-business-apis.mdc",
        ("postman/**", "scripts/soql/**"), "Business APIs",
        "API collections and SOQL files benefit from endpoint/auth/query guardrails at edit time."),
    RecommendedSkillRule("pmos-integration/SKILL.md", "pmos-integration.mdc",
        (".claude/skill-manifest.yml",), "PMOS Integration",
        "The cross-repo skill manifest is a single integration point with no auto-injected rule."),
    RecommendedSkillRule("revenue-cloud-docs/SKILL.md", "revenue-cloud-docs.mdc",
        ("docs/salesforce/**", "docs/enablement/**"), "Revenue Cloud Docs",
        "Grounding product claims against Salesforce Help is high-risk but not file-triggered."),
    RecommendedSkillRule("repo-integration/ux-assembly-retrieve.md", "post-ux-generated-output.mdc",
        ("unpackaged/post_ux/**",), "UX Assembly",
        "`unpackaged/post_ux/` is generated output and should warn on any direct edit."),
)

HIGH_RISK_PATHS: tuple[HighRiskPath, ...] = (
    HighRiskPath("unpackaged/post_ux/**", "UX Assembly", "AGENTS.md DO NOT #1 and Repository Layout",
        "post-ux-generated-output.mdc", "", "Generated UX output must not be edited directly."),
    HighRiskPath("force-app/**/profiles/*.profile-meta.xml", "UX Assembly / Profiles", "AGENTS.md DO NOT #2",
        "force-app-profile-safety.mdc", "", "Force-app profiles should stay classAccesses-only; layout/application visibility belongs in templates."),
    HighRiskPath("force-app/**/*.object-meta.xml", "UX Assembly / Objects", "AGENTS.md DO NOT #3",
        "force-app-object-safety.mdc", "", "Object actionOverrides/compact layout assignment belong in templates, not force-app objects."),
    HighRiskPath("datasets/sfdmu/**/export.json", "SFDMU Data Plans", "AGENTS.md SFDMU v5 critical rules",
        "sfdmu-export-json.mdc", "scripts/validate_sfdmu_v5_datasets.py", "SFDMU v5 operation/externalId/deleteOldData choices can be destructive."),
    HighRiskPath("datasets/sfdmu/**/*.csv", "SFDMU Data Plans", "AGENTS.md SFDMU v5 critical rules",
        "sfdmu-csv-data.mdc", "scripts/validate_sfdmu_v5_datasets.py", "CSV header/composite key drift can break idempotency or data loads."),
    HighRiskPath("tasks/**/*.py", "CCI Orchestration", "AGENTS.md Org Identity: CCI vs SF CLI",
        "cci-python-tasks.mdc", "", "Python CCI tasks must not pass access tokens to sf CLI commands."),
    HighRiskPath("templates/flexipages/**", "UX Assembly", "AGENTS.md DO NOT #6",
        "ux-templates.mdc", "", "EmailTemplatePage flexipages cannot deploy via Metadata API."),
    HighRiskPath("**/rlm.network-meta.xml", "PRM Network", "AGENTS.md DO NOT #7",
        "network-email-safety.mdc", "", "Network metadata must keep placeholder emails; deploy tasks patch/revert real values."),
)

OWNER_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("sfdmu", "SFDMU Data Plans"), ("cci", "CCI Orchestration"), ("apex", "Apex"),
    ("lwc", "Lightning Web Components"), ("ux", "UX Assembly"), ("robot", "Robot Testing"),
    ("doc", "Doc Consistency"), ("schema", "Schema Validation"), ("release", "Release Enablement"),
    ("business", "Business APIs"), ("pmos", "PMOS Integration"),
)


def extract_frontmatter(text: str) -> str:
    if not text.lstrip("﻿").startswith("---"):
        return ""
    # Tolerate CRLF line endings and an optional trailing newline after the
    # closing fence so a rule file's globs are not silently dropped.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    match = re.match(r"^---\n(.*?)\n---\s*(?:\n|$)", text, flags=re.DOTALL)
    return match.group(1) if match else ""


def _split_flow_list(inline: str) -> list[str]:
    """Split a YAML inline flow-list body on commas at brace/quote depth 0.

    Keeps brace expansions (``*.{html,js}``) and quoted items intact instead of
    splitting on every comma.
    """
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    quote = ""
    for ch in inline:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in "'\"":
            quote = ch
            buf.append(ch)
        elif ch in "{[(":
            depth += 1
            buf.append(ch)
        elif ch in "}])":
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return [p.strip().strip("'\"") for p in parts if p.strip()]


def parse_globs(frontmatter: str) -> tuple[str, ...]:
    lines = frontmatter.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("globs:"):
            continue
        inline = stripped.split(":", 1)[1].strip()
        if inline:
            # Strip surrounding flow-list brackets: globs: [a/**, b/**]
            if inline.startswith("[") and inline.endswith("]"):
                inline = inline[1:-1]
            return tuple(_split_flow_list(inline))
        globs: list[str] = []
        for child in lines[index + 1:]:
            if not child.startswith((" ", "\t")):
                break
            child_stripped = child.strip()
            if child_stripped.startswith("-"):
                globs.append(child_stripped[1:].strip().strip("'\""))
        return tuple(globs)
    return ()


def has_do_not_section(text: str) -> bool:
    return bool(re.search(r"^##+\s+DO NOT\b", text, flags=re.MULTILINE | re.IGNORECASE))


def parse_rule_table(markdown: str) -> dict[str, dict[str, str]]:
    """Parse Markdown rule tables (columns: Rule, Triggers On, Equivalent Skill)."""
    rows: dict[str, dict[str, str]] = {}
    for line in markdown.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = split_table_row(line)
        if len(cells) < 3 or is_separator_row(cells):
            continue
        if cells[0].lower() in {"rule", "rule file", "i need to..."}:
            continue
        rule_match = re.search(r"`?([^`\s|]+\.mdc)`?", cells[0])
        if not rule_match:
            continue
        name = Path(rule_match.group(1)).name
        skill_match = re.search(r"`?([^`\s|]+\.md)`?", cells[2])
        rows[name] = {
            "triggers": cells[1],
            "skill": skill_match.group(1) if skill_match else cells[2],
        }
    return rows


def infer_owner(rule_name: str, skill_path: str) -> str:
    haystack = f"{rule_name} {skill_path}".lower()
    for keyword, owner in OWNER_KEYWORDS:
        if keyword in haystack:
            return owner
    return "Repository Integration"


def glob_covers(rules: list[RuleInfo], candidate: str) -> bool:
    """True if any rule glob matches the candidate high-risk path.

    This is an intentional approximation: ``fnmatch`` has no path-segment
    awareness (``*`` spans ``/``), so coverage matching errs toward broad. It is
    a planning aid for the coverage report, not an access-control decision.
    """
    normalized = candidate.rstrip("/")
    samples = {
        normalized,
        normalized.replace("**", "x").replace("*", "x"),
        normalized.replace("**/", ""),
    }
    for rule in rules:
        for pattern in rule.globs:
            if pattern == candidate:
                return True
            for sample in samples:
                # fnmatch(name, pattern): the candidate is the name to match.
                if fnmatch.fnmatch(sample, pattern):
                    return True
    return False


def collect_rules(root: Path) -> list[RuleInfo]:
    agents_rules = parse_rule_table(read_text(root / AGENTS_PATH))
    readme_rules = parse_rule_table(read_text(root / SKILLS_README))
    rules_dir = root / RULES_ROOT

    rules: list[RuleInfo] = []
    for rule_path in sorted(rules_dir.glob("*.mdc")):
        text = read_text(rule_path)
        name = rule_path.name
        skill = readme_rules.get(name, {}).get("skill") or agents_rules.get(name, {}).get("skill") or ""
        rules.append(RuleInfo(
            path=rel(rule_path, root),
            name=name,
            globs=parse_globs(extract_frontmatter(text)),
            equivalent_skill=skill,
            has_do_not=has_do_not_section(text),
            appears_in_agents=name in agents_rules,
            listed_in_skill_readme=name in readme_rules,
            owner=infer_owner(name, skill),
        ))
    return rules


def _md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def _format_globs(globs: tuple[str, ...]) -> str:
    return "<br>".join(f"`{g}`" for g in globs) if globs else "—"


def render_coverage_markdown(root: Path) -> str:
    rules = collect_rules(root)
    rule_names = {r.name for r in rules}
    rules_not_in_readme = [r for r in rules if not r.listed_in_skill_readme]
    recommended_gaps = [g for g in RECOMMENDED_SKILL_RULES if g.suggested_rule not in rule_names]
    high_risk_gaps = [
        risk for risk in HIGH_RISK_PATHS
        if not glob_covers(rules, risk.path) and not risk.explicit_analyzer_check
    ]

    lines: list[str] = [
        "# Rule / Skill Coverage Matrix", "", COVERAGE_HEADER, "",
        "## Summary", "",
        f"- Cursor rule files found: **{len(rules)}**",
        f"- Rules not listed in `.cursor/skills/README.md`: **{len(rules_not_in_readme)}**",
        f"- Recommended skill rules still missing: **{len(recommended_gaps)}**",
        f"- High-risk AGENTS.md paths lacking both a rule and analyzer check: **{len(high_risk_gaps)}**",
        "",
        "## Rule Matrix", "",
        "| Rule file path | Glob pattern | Equivalent skill path | Has DO NOT section "
        "| Appears in AGENTS.md | Listed in skill README | Recommended owner/domain |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rules:
        lines.append("| " + " | ".join([
            f"`{r.path}`", _format_globs(r.globs),
            f"`{r.equivalent_skill}`" if r.equivalent_skill else "—",
            _yes_no(r.has_do_not), _yes_no(r.appears_in_agents),
            _yes_no(r.listed_in_skill_readme), _md_escape(r.owner),
        ]) + " |")

    lines += ["", "## Flags", "", "### 1. Rules not listed in the skill README", ""]
    if rules_not_in_readme:
        for r in rules_not_in_readme:
            lines.append(f"- `{r.path}` — owner/domain: **{r.owner}**; add it to "
                         "`.cursor/skills/README.md` or document why it is intentionally omitted.")
    else:
        lines.append("- None.")

    lines += [
        "", "### 2. Skills with no corresponding rule where file-specific "
        "auto-injection would reduce risk", "",
        "| Skill path | Suggested rule | Suggested glob(s) | Owner/domain | Reason |",
        "|---|---|---|---|---|",
    ]
    if recommended_gaps:
        for g in recommended_gaps:
            lines.append("| " + " | ".join([
                f"`{g.skill_path}`", f"`{g.suggested_rule}`", _format_globs(g.suggested_globs),
                _md_escape(g.owner), _md_escape(g.reason),
            ]) + " |")
    else:
        lines.append("| — | — | — | — | None. |")

    lines += [
        "", "### 3. High-risk paths from AGENTS.md that lack a rule or explicit analyzer check", "",
        "| Path | Owner/domain | AGENTS.md source | Expected rule | Explicit analyzer check | Reason |",
        "|---|---|---|---|---|---|",
    ]
    if high_risk_gaps:
        for risk in high_risk_gaps:
            lines.append("| " + " | ".join([
                f"`{risk.path}`", _md_escape(risk.owner), _md_escape(risk.source),
                f"`{risk.expected_rule}`",
                f"`{risk.explicit_analyzer_check}`" if risk.explicit_analyzer_check else "—",
                _md_escape(risk.reason),
            ]) + " |")
    else:
        lines.append("| — | — | — | — | — | None. |")

    lines += [
        "", "## Notes", "",
        "- `Appears in AGENTS.md` is true when the rule filename is present in the root "
        "`AGENTS.md` file-specific rule table.",
        "- `Listed in skill README` is true when the rule filename is present in "
        "`.cursor/skills/README.md`.",
        "- High-risk path coverage is satisfied by either a matching `.cursor/rules/*.mdc` "
        "glob or an explicit analyzer/validator script listed in this report.",
        "",
    ]
    return "\n".join(lines)


def cmd_coverage(root: Path, dry_run: bool, output: Path | None) -> int:
    report = render_coverage_markdown(root)
    if dry_run:
        print(report, end="" if report.endswith("\n") else "\n")
        return 0
    out_path = Path(os.path.abspath(output)) if output is not None else (root / COVERAGE_PATH)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {rel(out_path, root)}")
    return 0


# ===========================================================================
# CLI
# ===========================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze the repository's AI-agent tooling surface. "
                    "Defaults to the stdlib-only 'check' gate when no subcommand is given.",
    )
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="Repository root (default: auto-detect from this script).")
    sub = parser.add_subparsers(dest="command")

    p_check = sub.add_parser("check", help="stdlib-only pass/fail gate (default)")
    p_check.add_argument("--full-generated-reference-checks", action="store_true",
                         help="also dry-run generate_cci_reference.py (requires PyYAML/CumulusCI)")

    p_report = sub.add_parser("report", help="write Markdown report + JSON scorecard")
    p_report.add_argument("--check", action="store_true", dest="report_check",
                          help="exit non-zero if blocking errors are found")
    p_report.add_argument("--json", action="store_true", dest="report_json",
                          help="print the scorecard JSON to stdout")

    p_cov = sub.add_parser("coverage", help="write the rule/skill coverage matrix")
    p_cov.add_argument("--dry-run", action="store_true", help="print the matrix instead of writing it")
    p_cov.add_argument("--output", type=Path, default=None, help="override the output path")

    sub.add_parser("all", help="run check, then report, then coverage")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    root = (args.repo_root or find_repo_root()).resolve()
    command = args.command or "check"

    if command == "check":
        return cmd_check(root, getattr(args, "full_generated_reference_checks", False))
    if command == "report":
        return cmd_report(root, getattr(args, "report_check", False), getattr(args, "report_json", False))
    if command == "coverage":
        return cmd_coverage(root, getattr(args, "dry_run", False), getattr(args, "output", None))
    if command == "all":
        gate = cmd_check(root, False)
        print()
        cmd_report(root, False, False)
        print()
        cmd_coverage(root, False, None)
        return gate
    parser.error(f"unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
