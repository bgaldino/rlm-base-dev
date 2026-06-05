#!/usr/bin/env python3
"""Analyze AI-agent rule/skill coverage and generate context reports.

The primary output is ``.agents/context/rule-skill-coverage.md``. It compares
Cursor auto-injection rules with the canonical agent instructions and skill
README, then flags missing documentation or missing rule/check coverage for
high-risk repository surfaces.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RULES_DIR = ROOT / ".cursor" / "rules"
SKILLS_README = ROOT / ".cursor" / "skills" / "README.md"
AGENTS_MD = ROOT / "AGENTS.md"
OUTPUT_PATH = ROOT / ".agents" / "context" / "rule-skill-coverage.md"

HEADER_NOTE = (
    "> **Auto-generated** by `scripts/ai/analyze_agent_tooling.py`.\n"
    "> Do not edit manually — re-run the script after changing `AGENTS.md`, "
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
    RecommendedSkillRule(
        "schema-validation/SKILL.md",
        "schema-validation.mdc",
        ("docs/erds/**", "scripts/erd/**/*.py"),
        "Schema Validation",
        "ERD/schema files are safety-critical and the skill has no file-triggered rule today.",
    ),
    RecommendedSkillRule(
        "release-enablement/SKILL.md",
        "release-enablement.mdc",
        ("docs/enablement/**", "docs/salesforce/**"),
        "Release Enablement",
        "Enablement docs have release-specific source/extract conventions that are easy to miss.",
    ),
    RecommendedSkillRule(
        "rlm-business-apis/SKILL.md",
        "rlm-business-apis.mdc",
        ("postman/**", "scripts/soql/**"),
        "Business APIs",
        "API collections and SOQL files benefit from endpoint/auth/query guardrails at edit time.",
    ),
    RecommendedSkillRule(
        "pmos-integration/SKILL.md",
        "pmos-integration.mdc",
        (".claude/skill-manifest.yml",),
        "PMOS Integration",
        "The cross-repo skill manifest is a single integration point with no auto-injected rule.",
    ),
    RecommendedSkillRule(
        "revenue-cloud-docs/SKILL.md",
        "revenue-cloud-docs.mdc",
        ("docs/salesforce/**", "docs/enablement/**"),
        "Revenue Cloud Docs",
        "Grounding product claims against Salesforce Help is high-risk but not file-triggered.",
    ),
    RecommendedSkillRule(
        "repo-integration/ux-assembly-retrieve.md",
        "post-ux-generated-output.mdc",
        ("unpackaged/post_ux/**",),
        "UX Assembly",
        "`unpackaged/post_ux/` is generated output and should warn on any direct edit.",
    ),
)

HIGH_RISK_PATHS: tuple[HighRiskPath, ...] = (
    HighRiskPath(
        "unpackaged/post_ux/**",
        "UX Assembly",
        "AGENTS.md DO NOT #1 and Repository Layout",
        "post-ux-generated-output.mdc",
        "",
        "Generated UX output must not be edited directly.",
    ),
    HighRiskPath(
        "force-app/**/profiles/*.profile-meta.xml",
        "UX Assembly / Profiles",
        "AGENTS.md DO NOT #2",
        "force-app-profile-safety.mdc",
        "",
        "Force-app profiles should stay classAccesses-only; layout/application visibility belongs in templates.",
    ),
    HighRiskPath(
        "force-app/**/*.object-meta.xml",
        "UX Assembly / Objects",
        "AGENTS.md DO NOT #3",
        "force-app-object-safety.mdc",
        "",
        "Object actionOverrides/compact layout assignment belong in templates, not force-app objects.",
    ),
    HighRiskPath(
        "datasets/sfdmu/**/export.json",
        "SFDMU Data Plans",
        "AGENTS.md SFDMU v5 critical rules",
        "sfdmu-export-json.mdc",
        "scripts/validate_sfdmu_v5_datasets.py",
        "SFDMU v5 operation/externalId/deleteOldData choices can be destructive.",
    ),
    HighRiskPath(
        "datasets/sfdmu/**/*.csv",
        "SFDMU Data Plans",
        "AGENTS.md SFDMU v5 critical rules",
        "sfdmu-csv-data.mdc",
        "scripts/validate_sfdmu_v5_datasets.py",
        "CSV header/composite key drift can break idempotency or data loads.",
    ),
    HighRiskPath(
        "tasks/**/*.py",
        "CCI Orchestration",
        "AGENTS.md Org Identity: CCI vs SF CLI",
        "cci-python-tasks.mdc",
        "",
        "Python CCI tasks must not pass access tokens to sf CLI commands.",
    ),
    HighRiskPath(
        "templates/flexipages/**",
        "UX Assembly",
        "AGENTS.md DO NOT #6",
        "ux-templates.mdc",
        "",
        "EmailTemplatePage flexipages cannot deploy via Metadata API.",
    ),
    HighRiskPath(
        "**/rlm.network-meta.xml",
        "PRM Network",
        "AGENTS.md DO NOT #7",
        "network-email-safety.mdc",
        "",
        "Network metadata must keep placeholder emails; deploy tasks patch/revert real values.",
    ),
)

OWNER_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("sfdmu", "SFDMU Data Plans"),
    ("cci", "CCI Orchestration"),
    ("apex", "Apex"),
    ("lwc", "Lightning Web Components"),
    ("ux", "UX Assembly"),
    ("robot", "Robot Testing"),
    ("doc", "Doc Consistency"),
    ("schema", "Schema Validation"),
    ("release", "Release Enablement"),
    ("business", "Business APIs"),
    ("pmos", "PMOS Integration"),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def extract_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    return match.group(1) if match else ""


def parse_globs(frontmatter: str) -> tuple[str, ...]:
    lines = frontmatter.splitlines()
    globs: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("globs:"):
            inline = stripped.split(":", 1)[1].strip()
            if inline:
                return tuple(
                    part.strip().strip("'\"")
                    for part in inline.split(",")
                    if part.strip()
                )
            for child in lines[index + 1 :]:
                if not child.startswith((" ", "\t")):
                    break
                child_stripped = child.strip()
                if child_stripped.startswith("-"):
                    globs.append(child_stripped[1:].strip().strip("'\""))
            break
    return tuple(globs)


def has_do_not_section(text: str) -> bool:
    return bool(
        re.search(r"^##+\s+DO NOT\b", text, flags=re.MULTILINE | re.IGNORECASE)
    )


def parse_rule_table(markdown: str) -> dict[str, dict[str, str]]:
    """Parse rule tables with columns Rule, Triggers On, Equivalent Skill."""
    rows: dict[str, dict[str, str]] = {}
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "`" not in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() in {"rule", "------------"}:
            continue
        rule_match = re.search(r"`([^`]+\.mdc)`", cells[0])
        if not rule_match:
            continue
        skill_match = re.search(r"`([^`]+\.md)`", cells[2])
        rule_name = Path(rule_match.group(1)).name
        rows[rule_name] = {
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
    normalized = candidate.rstrip("/")
    samples = {
        normalized,
        normalized.replace("**", "sample").replace("*", "sample"),
        normalized.replace("**/", ""),
    }
    for rule in rules:
        for pattern in rule.globs:
            for sample in samples:
                if fnmatch.fnmatch(sample, pattern) or fnmatch.fnmatch(pattern, candidate):
                    return True
            if pattern == candidate:
                return True
    return False


def collect_rules() -> list[RuleInfo]:
    agents_text = read_text(AGENTS_MD)
    readme_text = read_text(SKILLS_README)
    agents_rules = parse_rule_table(agents_text)
    readme_rules = parse_rule_table(readme_text)

    rules: list[RuleInfo] = []
    for rule_path in sorted(RULES_DIR.glob("*.mdc")):
        text = read_text(rule_path)
        name = rule_path.name
        skill = (
            readme_rules.get(name, {}).get("skill")
            or agents_rules.get(name, {}).get("skill")
            or ""
        )
        rules.append(
            RuleInfo(
                path=str(rule_path.relative_to(ROOT)),
                name=name,
                globs=parse_globs(extract_frontmatter(text)),
                equivalent_skill=skill,
                has_do_not=has_do_not_section(text),
                appears_in_agents=name in agents_rules,
                listed_in_skill_readme=name in readme_rules,
                owner=infer_owner(name, skill),
            )
        )
    return rules


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def format_globs(globs: tuple[str, ...]) -> str:
    return "<br>".join(f"`{glob}`" for glob in globs) if globs else "—"


def generate_report() -> str:
    rules = collect_rules()
    rule_names = {rule.name for rule in rules}
    rules_not_in_readme = [rule for rule in rules if not rule.listed_in_skill_readme]
    recommended_gaps = [
        gap for gap in RECOMMENDED_SKILL_RULES if gap.suggested_rule not in rule_names
    ]
    high_risk_gaps = [
        risk
        for risk in HIGH_RISK_PATHS
        if not glob_covers(rules, risk.path) and not risk.explicit_analyzer_check
    ]

    lines: list[str] = [
        "# Rule / Skill Coverage Matrix",
        "",
        HEADER_NOTE,
        "",
        "## Summary",
        "",
        f"- Cursor rule files found: **{len(rules)}**",
        f"- Rules not listed in `.cursor/skills/README.md`: **{len(rules_not_in_readme)}**",
        f"- Recommended skill rules still missing: **{len(recommended_gaps)}**",
        f"- High-risk AGENTS.md paths lacking both a rule and analyzer check: **{len(high_risk_gaps)}**",
        "",
        "## Rule Matrix",
        "",
        "| Rule file path | Glob pattern | Equivalent skill path | Has DO NOT section "
        "| Appears in AGENTS.md | Listed in skill README | Recommended owner/domain |",
        "|---|---|---|---|---|---|---|",
    ]

    for rule in rules:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{rule.path}`",
                    format_globs(rule.globs),
                    f"`{rule.equivalent_skill}`" if rule.equivalent_skill else "—",
                    yes_no(rule.has_do_not),
                    yes_no(rule.appears_in_agents),
                    yes_no(rule.listed_in_skill_readme),
                    md_escape(rule.owner),
                ]
            )
            + " |"
        )

    lines.extend([
        "",
        "## Flags",
        "",
        "### 1. Rules not listed in the skill README",
        "",
    ])
    if rules_not_in_readme:
        for rule in rules_not_in_readme:
            lines.append(
                f"- `{rule.path}` — owner/domain: **{rule.owner}**; "
                "add it to `.cursor/skills/README.md` or document why it is "
                "intentionally omitted."
            )
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "### 2. Skills with no corresponding rule where file-specific "
        "auto-injection would reduce risk",
        "",
        "| Skill path | Suggested rule | Suggested glob(s) | Owner/domain | Reason |",
        "|---|---|---|---|---|",
    ])
    if recommended_gaps:
        for gap in recommended_gaps:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{gap.skill_path}`",
                        f"`{gap.suggested_rule}`",
                        format_globs(gap.suggested_globs),
                        md_escape(gap.owner),
                        md_escape(gap.reason),
                    ]
                )
                + " |"
            )
    else:
        lines.append("| — | — | — | — | None. |")

    lines.extend([
        "",
        "### 3. High-risk paths from AGENTS.md that lack a rule or "
        "explicit analyzer check",
        "",
        "| Path | Owner/domain | AGENTS.md source | Expected rule | Explicit analyzer check | Reason |",
        "|---|---|---|---|---|---|",
    ])
    if high_risk_gaps:
        for risk in high_risk_gaps:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{risk.path}`",
                        md_escape(risk.owner),
                        md_escape(risk.source),
                        f"`{risk.expected_rule}`",
                        f"`{risk.explicit_analyzer_check}`" if risk.explicit_analyzer_check else "—",
                        md_escape(risk.reason),
                    ]
                )
                + " |"
            )
    else:
        lines.append("| — | — | — | — | — | None. |")

    lines.extend([
        "",
        "## Notes",
        "",
        "- `Appears in AGENTS.md` is true when the rule filename is present "
        "in the root `AGENTS.md` file-specific rule table.",
        "- `Listed in skill README` is true when the rule filename is present "
        "in `.cursor/skills/README.md`.",
        "- High-risk path coverage is satisfied by either a matching "
        "`.cursor/rules/*.mdc` glob or an explicit analyzer/validator script "
        "listed in this report.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated rule/skill coverage report instead of writing it.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help=f"Report path (default: {OUTPUT_PATH.relative_to(ROOT)}).",
    )
    args = parser.parse_args()

    report = generate_report()
    if args.dry_run:
        print(report, end="")
        return 0

    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
