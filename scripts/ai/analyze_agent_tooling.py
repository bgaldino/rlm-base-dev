#!/usr/bin/env python3
"""Static analyzer for the repository's AI-agent tooling surface.

The checks intentionally use only Python's standard library so the analyzer can
run before CumulusCI, PyYAML, or Salesforce tooling is installed. When PyYAML is
available, the script uses it to enrich manifest checks; otherwise it falls back
to conservative line-oriented parsing.

Outputs:
  - docs/analysis/tooling-optimization-report.md
  - .agents/context/tooling-scorecard.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

REQUIRED_FILES = [
    Path("AGENTS.md"),
    Path(".github/copilot-instructions.md"),
    Path(".claude/skill-manifest.yml"),
    Path(".cursor/skills/README.md"),
]

GENERATED_CCI_REFERENCE_FILES = [
    Path(".cursor/skills/cci-orchestration/tasks-reference.md"),
    Path(".cursor/skills/cci-orchestration/flows-reference.md"),
    Path(".cursor/skills/cci-orchestration/feature-flags.md"),
]

REPORT_PATH = Path("docs/analysis/tooling-optimization-report.md")
SCORECARD_PATH = Path(".agents/context/tooling-scorecard.json")
MANIFEST_PATH = Path(".claude/skill-manifest.yml")
AGENTS_PATH = Path("AGENTS.md")
SKILLS_ROOT = Path(".cursor/skills")
RULES_ROOT = Path(".cursor/rules")

BACKTICK_PATH_RE = re.compile(r"`([^`]+\.md)`")


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str
    severity: str = "error"


@dataclass
class RuleMapping:
    rule: str
    status: str
    target: str
    source: str


@dataclass
class Analysis:
    repo_root: Path
    generated_at: str
    required_files: list[CheckResult] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    agents_skill_references: list[str] = field(default_factory=list)
    missing_agents_skill_references: list[str] = field(default_factory=list)
    rule_mappings: list[RuleMapping] = field(default_factory=list)
    cci_reference_files: list[CheckResult] = field(default_factory=list)
    manifest_summary: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def errors(self) -> list[str]:
        errors: list[str] = []
        errors.extend(result.details for result in self.required_files if not result.ok)
        errors.extend(result.details for result in self.cci_reference_files if not result.ok)
        errors.extend(
            f"AGENTS.md references missing skill file or unmatched glob: {path}"
            for path in self.missing_agents_skill_references
        )
        errors.extend(
            f"{mapping.rule} has no corresponding skill or stand-alone note"
            for mapping in self.rule_mappings
            if mapping.status == "missing"
        )
        return errors

    @property
    def passed(self) -> bool:
        return not self.errors


def find_repo_root(start: Path) -> Path:
    """Find the repo root by walking up to AGENTS.md and .git."""
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    return start


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def posix(path: Path) -> str:
    return path.as_posix()


def sorted_relative_files(root: Path, pattern: str, repo_root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(posix(path.relative_to(repo_root)) for path in root.glob(pattern) if path.is_file())


def first_level_skill_dirs(repo_root: Path) -> set[str]:
    skills_root = repo_root / SKILLS_ROOT
    if not skills_root.is_dir():
        return set()
    return {path.name for path in skills_root.iterdir() if path.is_dir()}


def extract_agents_skill_references(agents_text: str, repo_root: Path) -> list[str]:
    """Return advertised .cursor/skills/*.md references from AGENTS.md.

    AGENTS.md has a Skill Index with repo-relative .cursor paths and a
    progressive-disclosure table with paths relative to .cursor/skills/. The
    broader document also mentions non-skill Markdown files (for example
    AGENTS.md and CLAUDE.md), so this function only promotes bare references
    whose first path segment matches an actual first-level skill directory.
    """
    skill_dirs = first_level_skill_dirs(repo_root)
    references: set[str] = set()
    for match in BACKTICK_PATH_RE.finditer(agents_text):
        path = match.group(1).strip()
        if path.startswith(".cursor/skills/"):
            references.add(path)
            continue
        if path.startswith("docs/") or path.startswith(".github/") or "{" in path:
            continue
        first_segment = path.split("/", 1)[0]
        if "/" in path and first_segment in skill_dirs:
            references.add(f".cursor/skills/{path}")
    return sorted(references)


def path_reference_exists(repo_root: Path, reference: str) -> bool:
    if "*" in reference:
        return bool(list(repo_root.glob(reference)))
    return (repo_root / reference).is_file()


def normalize_equivalent_skill(cell: str) -> tuple[str, str]:
    """Classify the equivalent-skill table cell from AGENTS.md."""
    lowered = cell.lower()
    if "stand-alone" in lowered or "standalone" in lowered:
        return "standalone", cell.strip()

    match = re.search(r"`([^`]+)`", cell)
    if not match:
        return "missing", cell.strip()

    ref = match.group(1).strip()
    if ref.startswith(".cursor/skills/"):
        return "skill", ref
    if ref.endswith(".md"):
        return "skill", f".cursor/skills/{ref}"
    return "missing", ref


def extract_rule_mappings(agents_text: str, rules: Iterable[str], repo_root: Path) -> list[RuleMapping]:
    mappings_by_rule: dict[str, RuleMapping] = {}
    for line in agents_text.splitlines():
        if not line.startswith("|") or ".mdc`" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        rule_match = re.search(r"`([^`]+\.mdc)`", cells[0])
        if not rule_match:
            continue
        rule = Path(rule_match.group(1)).name
        cell = cells[-1]
        kind, target = normalize_equivalent_skill(cell)
        if kind == "standalone":
            status = "standalone"
        elif kind == "skill" and path_reference_exists(repo_root, target):
            status = "skill"
        else:
            status = "missing"
        mappings_by_rule[rule] = RuleMapping(rule=rule, status=status, target=target, source="AGENTS.md")

    results: list[RuleMapping] = []
    for rule_path in rules:
        rule_name = Path(rule_path).name
        mapping = mappings_by_rule.get(rule_name)
        if mapping is None:
            results.append(
                RuleMapping(
                    rule=rule_name,
                    status="missing",
                    target="No row in AGENTS.md File-Specific Rules table",
                    source="AGENTS.md",
                )
            )
        else:
            results.append(mapping)
    return sorted(results, key=lambda item: item.rule)


def load_yaml_optional(path: Path) -> tuple[dict[str, Any] | None, str]:
    """Load YAML with PyYAML when installed; otherwise return None.

    Importing is done through importlib so this script has no hard dependency on
    PyYAML and does not wrap imports in exception-handling blocks.
    """
    if importlib.util.find_spec("yaml") is None:
        return None, "line-oriented fallback"
    yaml = importlib.import_module("yaml")
    data = yaml.safe_load(read_text(path)) or {}
    if not isinstance(data, dict):
        return {}, "PyYAML"
    return data, "PyYAML"


def parse_manifest_fallback(text: str) -> dict[str, Any]:
    """Conservative line parser for Foundations manifest metadata.

    The fallback intentionally limits skill extraction to the top-level
    ``foundations:`` section so PMOS-side skill ids do not inflate this repo's
    local scorecard when PyYAML is unavailable.
    """
    summary: dict[str, Any] = {"skills": [], "auto_generated_subfiles": []}
    foundations_text = text
    foundations_match = re.search(r"(?ms)^foundations:\n(?P<body>.*?)(?=^pmos:|\Z)", text)
    if foundations_match:
        foundations_text = foundations_match.group("body")

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("manifest_version:"):
            summary["manifest_version"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("generated_at:"):
            summary["generated_at"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("last_verified:"):
            summary["last_verified"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("salesforce_release_active:"):
            summary["salesforce_release_active"] = stripped.split(":", 1)[1].strip().strip('"')

    for line in foundations_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            summary["skills"].append(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("path: .cursor/skills/"):
            summary.setdefault("skill_paths", []).append(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("- .cursor/skills/cci-orchestration/"):
            summary["auto_generated_subfiles"].append(stripped.removeprefix("- ").strip())
    return summary


def yaml_scalar(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def summarize_manifest(repo_root: Path) -> dict[str, Any]:
    manifest = repo_root / MANIFEST_PATH
    if not manifest.is_file():
        return {"present": False, "parser": "not run"}

    yaml_data, parser = load_yaml_optional(manifest)
    if yaml_data is not None:
        foundations = yaml_data.get("foundations", {}) if isinstance(yaml_data, dict) else {}
        skills = foundations.get("skills", []) if isinstance(foundations, dict) else []
        skill_ids = [skill.get("id") for skill in skills if isinstance(skill, dict) and skill.get("id")]
        skill_paths = [skill.get("path") for skill in skills if isinstance(skill, dict) and skill.get("path")]
        generated_subfiles: list[str] = []
        for skill in skills:
            if isinstance(skill, dict):
                generated_subfiles.extend(skill.get("auto_generated_subfiles", []) or [])
        return {
            "present": True,
            "parser": parser,
            "manifest_version": yaml_scalar(yaml_data.get("manifest_version")),
            "generated_at": yaml_scalar(yaml_data.get("generated_at")),
            "last_verified": yaml_scalar(yaml_data.get("last_verified")),
            "salesforce_release_active": yaml_scalar(yaml_data.get("salesforce_release_active")),
            "skill_count": len(skill_ids),
            "skill_ids": sorted(str(skill_id) for skill_id in skill_ids),
            "skill_paths": sorted(str(path) for path in skill_paths),
            "auto_generated_subfiles": sorted(str(path) for path in generated_subfiles),
        }

    fallback = parse_manifest_fallback(read_text(manifest))
    return {
        "present": True,
        "parser": parser,
        "manifest_version": fallback.get("manifest_version"),
        "generated_at": fallback.get("generated_at"),
        "last_verified": fallback.get("last_verified"),
        "salesforce_release_active": fallback.get("salesforce_release_active"),
        "skill_count": len(fallback.get("skills", [])),
        "skill_ids": sorted(fallback.get("skills", [])),
        "skill_paths": sorted(fallback.get("skill_paths", [])),
        "auto_generated_subfiles": sorted(fallback.get("auto_generated_subfiles", [])),
    }


def analyze(repo_root: Path) -> Analysis:
    generated_at = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    analysis = Analysis(repo_root=repo_root, generated_at=generated_at)

    for rel_path in REQUIRED_FILES:
        exists = (repo_root / rel_path).is_file()
        analysis.required_files.append(
            CheckResult(
                name=posix(rel_path),
                ok=exists,
                details=(f"Found {rel_path}" if exists else f"Missing required file: {rel_path}"),
            )
        )

    analysis.skills = sorted_relative_files(repo_root / SKILLS_ROOT, "**/*.md", repo_root)
    analysis.rules = sorted_relative_files(repo_root / RULES_ROOT, "*.mdc", repo_root)

    agents_file = repo_root / AGENTS_PATH
    agents_text = read_text(agents_file) if agents_file.is_file() else ""
    analysis.agents_skill_references = extract_agents_skill_references(agents_text, repo_root)
    analysis.missing_agents_skill_references = [
        reference for reference in analysis.agents_skill_references if not path_reference_exists(repo_root, reference)
    ]

    analysis.rule_mappings = extract_rule_mappings(agents_text, analysis.rules, repo_root)

    for rel_path in GENERATED_CCI_REFERENCE_FILES:
        exists = (repo_root / rel_path).is_file()
        analysis.cci_reference_files.append(
            CheckResult(
                name=posix(rel_path),
                ok=exists,
                details=(f"Found {rel_path}" if exists else f"Missing generated CCI reference file: {rel_path}"),
            )
        )

    analysis.manifest_summary = summarize_manifest(repo_root)

    manifest_skill_paths = analysis.manifest_summary.get("skill_paths", []) or []
    missing_manifest_paths = [path for path in manifest_skill_paths if not path_reference_exists(repo_root, path)]
    if missing_manifest_paths:
        analysis.warnings.append(
            "Manifest references missing skill paths: " + ", ".join(sorted(missing_manifest_paths))
        )

    return analysis


def status_icon(ok: bool) -> str:
    return "✅" if ok else "❌"


def render_markdown(analysis: Analysis) -> str:
    error_count = len(analysis.errors)
    warning_count = len(analysis.warnings)
    lines: list[str] = [
        "# Agent Tooling Optimization Report",
        "",
        f"Generated: `{analysis.generated_at}`",
        "",
        "## Summary",
        "",
        f"- Overall status: **{'PASS' if analysis.passed else 'FAIL'}**",
        f"- Required files: **{sum(1 for item in analysis.required_files if item.ok)}/{len(analysis.required_files)}** present",
        f"- Skills inventoried: **{len(analysis.skills)}** Markdown files under `.cursor/skills/`",
        f"- Cursor rules inventoried: **{len(analysis.rules)}** `.mdc` files under `.cursor/rules/`",
        f"- AGENTS.md skill references: **{len(analysis.agents_skill_references)}** checked, **{len(analysis.missing_agents_skill_references)}** missing",
        f"- Generated CCI references: **{sum(1 for item in analysis.cci_reference_files if item.ok)}/{len(analysis.cci_reference_files)}** present",
        f"- Errors: **{error_count}**",
        f"- Warnings: **{warning_count}**",
        "",
        "## Required Agent Entry Points",
        "",
    ]
    for item in analysis.required_files:
        lines.append(f"- {status_icon(item.ok)} `{item.name}` — {item.details}")

    lines.extend(["", "## Skill Inventory", ""])
    for skill in analysis.skills:
        lines.append(f"- `{skill}`")

    lines.extend(["", "## Cursor Rule Inventory", ""])
    for rule in analysis.rules:
        lines.append(f"- `{rule}`")

    lines.extend(["", "## AGENTS.md Skill Reference Check", ""])
    for reference in analysis.agents_skill_references:
        ok = reference not in analysis.missing_agents_skill_references
        lines.append(f"- {status_icon(ok)} `{reference}`")

    lines.extend(["", "## Cursor Rule Coverage", ""])
    for mapping in analysis.rule_mappings:
        if mapping.status == "skill":
            icon = "✅"
            description = f"mapped to `{mapping.target}`"
        elif mapping.status == "standalone":
            icon = "✅"
            description = f"has explicit stand-alone note ({mapping.target})"
        else:
            icon = "❌"
            description = mapping.target
        lines.append(f"- {icon} `{mapping.rule}` — {description}")

    lines.extend(["", "## Generated CCI Reference Files", ""])
    for item in analysis.cci_reference_files:
        lines.append(f"- {status_icon(item.ok)} `{item.name}` — {item.details}")

    manifest = analysis.manifest_summary
    lines.extend(
        [
            "",
            "## Skill Manifest Snapshot",
            "",
            f"- Present: **{manifest.get('present', False)}**",
            f"- Parser: `{manifest.get('parser', 'unknown')}`",
            f"- Manifest version: `{manifest.get('manifest_version')}`",
            f"- Last verified: `{manifest.get('last_verified')}`",
            f"- Active Salesforce release: `{manifest.get('salesforce_release_active')}`",
            f"- Manifest skill count: **{manifest.get('skill_count', 0)}**",
        ]
    )
    for skill_id in manifest.get("skill_ids", []) or []:
        lines.append(f"  - `{skill_id}`")

    lines.extend(["", "## Findings", ""])
    if analysis.errors:
        lines.append("### Errors")
        lines.append("")
        for error in analysis.errors:
            lines.append(f"- ❌ {error}")
    else:
        lines.append("- ✅ No blocking errors found.")

    if analysis.warnings:
        lines.extend(["", "### Warnings", ""])
        for warning in analysis.warnings:
            lines.append(f"- ⚠️ {warning}")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This report is generated by `scripts/ai/analyze_agent_tooling.py`.",
            "- The analyzer intentionally avoids mandatory third-party dependencies. If PyYAML is installed, manifest reporting is richer; otherwise the line-oriented fallback is used.",
            "",
        ]
    )
    return "\n".join(lines)


def to_scorecard(analysis: Analysis) -> dict[str, Any]:
    return {
        "generated_at": analysis.generated_at,
        "status": "pass" if analysis.passed else "fail",
        "counts": {
            "required_files_present": sum(1 for item in analysis.required_files if item.ok),
            "required_files_total": len(analysis.required_files),
            "skills_markdown_files": len(analysis.skills),
            "cursor_rules": len(analysis.rules),
            "agents_skill_references": len(analysis.agents_skill_references),
            "missing_agents_skill_references": len(analysis.missing_agents_skill_references),
            "generated_cci_reference_files_present": sum(1 for item in analysis.cci_reference_files if item.ok),
            "generated_cci_reference_files_total": len(analysis.cci_reference_files),
            "errors": len(analysis.errors),
            "warnings": len(analysis.warnings),
        },
        "required_files": {item.name: item.ok for item in analysis.required_files},
        "skills": analysis.skills,
        "rules": analysis.rules,
        "agents_skill_references": {
            "checked": analysis.agents_skill_references,
            "missing": analysis.missing_agents_skill_references,
        },
        "rule_mappings": [
            {
                "rule": mapping.rule,
                "status": mapping.status,
                "target": mapping.target,
                "source": mapping.source,
            }
            for mapping in analysis.rule_mappings
        ],
        "generated_cci_reference_files": {item.name: item.ok for item in analysis.cci_reference_files},
        "manifest": analysis.manifest_summary,
        "errors": analysis.errors,
        "warnings": analysis.warnings,
    }


def write_outputs(analysis: Analysis) -> None:
    report = analysis.repo_root / REPORT_PATH
    scorecard = analysis.repo_root / SCORECARD_PATH
    report.parent.mkdir(parents=True, exist_ok=True)
    scorecard.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_markdown(analysis), encoding="utf-8")
    scorecard.write_text(json.dumps(to_scorecard(analysis), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze AI-agent tooling static coverage.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root. Defaults to walking up from the current working directory.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if blocking errors are found after writing outputs.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the scorecard JSON to stdout after writing outputs.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = (args.repo_root or find_repo_root(Path.cwd())).resolve()
    analysis = analyze(repo_root)
    write_outputs(analysis)

    if args.json:
        print(json.dumps(to_scorecard(analysis), indent=2, sort_keys=True))
    else:
        print(f"Wrote {REPORT_PATH}")
        print(f"Wrote {SCORECARD_PATH}")
        print(f"Status: {'PASS' if analysis.passed else 'FAIL'} ({len(analysis.errors)} errors, {len(analysis.warnings)} warnings)")

    if args.check and not analysis.passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
