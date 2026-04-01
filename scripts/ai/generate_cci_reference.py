#!/usr/bin/env python3
"""Generate CCI reference markdown files from cumulusci.yml.

Parses the project's cumulusci.yml and writes three auto-generated skill
reference files into .cursor/skills/cci-orchestration/:

  - tasks-reference.md   — all tasks organised by group
  - flows-reference.md   — all flows with step trees and when: conditions
  - feature-flags.md     — all feature flags with defaults and usage index

Usage:
    python scripts/ai/generate_cci_reference.py                # regenerate all
    python scripts/ai/generate_cci_reference.py --tasks-only    # just tasks
    python scripts/ai/generate_cci_reference.py --flows-only    # just flows
    python scripts/ai/generate_cci_reference.py --flags-only    # just flags
    python scripts/ai/generate_cci_reference.py --dry-run       # preview, no write

No external dependencies beyond PyYAML.
"""
import argparse
import os
import re
import sys
import textwrap
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
CCI_YML = ROOT / "cumulusci.yml"
OUTPUT_DIR = ROOT / ".cursor" / "skills" / "cci-orchestration"

def _header_note() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"> **Auto-generated** by `scripts/ai/generate_cci_reference.py` from "
        f"`cumulusci.yml` on {ts}.  \n"
        "> Do not edit manually — re-run the script after changing `cumulusci.yml`."
    )


HEADER_NOTE = _header_note()


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def load_cci() -> dict:
    with open(CCI_YML, "r") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Tasks reference
# ---------------------------------------------------------------------------

def generate_tasks_reference(data: dict) -> str:
    tasks: dict = data.get("tasks", {})
    by_group: dict[str, list] = defaultdict(list)

    for name, cfg in sorted(tasks.items()):
        if cfg is None:
            cfg = {}
        group = cfg.get("group", "Uncategorized")
        by_group[group].append((name, cfg))

    lines = [
        "# CCI Tasks Reference",
        "",
        HEADER_NOTE,
        "",
        f"**{len(tasks)} tasks** across **{len(by_group)} groups**.",
        "",
        "---",
        "",
    ]

    for group in sorted(by_group):
        task_list = by_group[group]
        lines.append(f"## {group}")
        lines.append("")
        lines.append(f"*{len(task_list)} task(s)*")
        lines.append("")

        for name, cfg in sorted(task_list, key=lambda t: t[0]):
            lines.append(f"### `{name}`")
            lines.append("")

            desc = cfg.get("description", "")
            if desc:
                desc = " ".join(str(desc).split())
                lines.append(f"**Description:** {desc}")
                lines.append("")

            class_path = cfg.get("class_path", "")
            if class_path:
                lines.append(f"**Class:** `{class_path}`")
                lines.append("")

            options = cfg.get("options", {})
            if options:
                lines.append("**Options:**")
                lines.append("")
                for opt_name, opt_val in options.items():
                    if isinstance(opt_val, dict):
                        desc_text = opt_val.get("description", "")
                        req = opt_val.get("required", False)
                        lines.append(f"- `{opt_name}`: {desc_text} {'*(required)*' if req else ''}")
                    else:
                        val_str = str(opt_val)
                        if len(val_str) > 120:
                            val_str = val_str[:117] + "..."
                        lines.append(f"- `{opt_name}`: `{val_str}`")
                lines.append("")

            lines.append("---")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Flows reference
# ---------------------------------------------------------------------------

def _format_step(step_num, step_cfg, indent=0) -> list[str]:
    """Recursively format a flow step into markdown lines."""
    lines = []
    prefix = "  " * indent

    if isinstance(step_cfg, dict):
        task_name = step_cfg.get("task")
        flow_name = step_cfg.get("flow")
        when = step_cfg.get("when", "")
        options = step_cfg.get("options", {})

        ref_type = "task" if task_name else "flow"
        ref_name = task_name or flow_name or "???"

        when_str = f"  `when: {when}`" if when else ""

        lines.append(f"{prefix}{step_num}. **{ref_type}** `{ref_name}`{when_str}")

        if options and ref_type == "task":
            for k, v in options.items():
                v_str = str(v)
                if len(v_str) > 100:
                    v_str = v_str[:97] + "..."
                lines.append(f"{prefix}   - `{k}`: `{v_str}`")
    else:
        lines.append(f"{prefix}{step_num}. {step_cfg}")

    return lines


def generate_flows_reference(data: dict) -> str:
    flows: dict = data.get("flows", {})
    by_group: dict[str, list] = defaultdict(list)

    for name, cfg in flows.items():
        if cfg is None:
            cfg = {}
        group = cfg.get("group", "Uncategorized")
        by_group[group].append((name, cfg))

    lines = [
        "# CCI Flows Reference",
        "",
        HEADER_NOTE,
        "",
        f"**{len(flows)} flows** across **{len(by_group)} groups**.",
        "",
        "---",
        "",
    ]

    for group in sorted(by_group):
        flow_list = by_group[group]
        lines.append(f"## {group}")
        lines.append("")

        for name, cfg in sorted(flow_list, key=lambda f: f[0]):
            desc = cfg.get("description", "")
            if desc:
                desc = " ".join(str(desc).split())

            lines.append(f"### `{name}`")
            lines.append("")
            if desc:
                lines.append(f"{desc}")
                lines.append("")

            steps = cfg.get("steps", {})
            if steps:
                lines.append("**Steps:**")
                lines.append("")
                for step_num in sorted(steps, key=lambda s: int(s) if str(s).isdigit() else 0):
                    step_cfg = steps[step_num]
                    for line in _format_step(step_num, step_cfg):
                        lines.append(line)
                lines.append("")

            lines.append("---")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Feature flags reference
# ---------------------------------------------------------------------------

def _scan_when_clauses(data: dict) -> dict[str, list[str]]:
    """Scan all when: clauses in flows and build a flag → [usage context] map."""
    usage: dict[str, list[str]] = defaultdict(list)
    flows = data.get("flows", {})
    custom_keys = set(data.get("project", {}).get("custom", {}).keys())

    for flow_name, flow_cfg in flows.items():
        if not flow_cfg or "steps" not in flow_cfg:
            continue
        for step_num, step_cfg in flow_cfg.get("steps", {}).items():
            if not isinstance(step_cfg, dict):
                continue
            when = step_cfg.get("when", "")
            if not when:
                continue

            ref = step_cfg.get("task") or step_cfg.get("flow") or "???"
            when_str = str(when)

            for flag in custom_keys:
                pattern = rf'project_config\.project__custom__{re.escape(flag)}'
                if re.search(pattern, when_str):
                    usage[flag].append(f"`{flow_name}` step {step_num} → `{ref}`")

            if "org_config.scratch" in when_str:
                usage["(org_config.scratch)"].append(
                    f"`{flow_name}` step {step_num} → `{ref}`"
                )

    return dict(usage)


def generate_feature_flags(data: dict) -> str:
    custom: dict = data.get("project", {}).get("custom", {})
    usage_map = _scan_when_clauses(data)

    boolean_flags = []
    config_values = []
    anchor_entries = []

    for key, value in custom.items():
        if isinstance(value, (list, dict)):
            anchor_entries.append((key, value))
        elif isinstance(value, bool) or key in usage_map:
            boolean_flags.append((key, value))
        else:
            config_values.append((key, value))

    lines = [
        "# CCI Feature Flags Reference",
        "",
        HEADER_NOTE,
        "",
        f"**{len(boolean_flags)} feature flags**, **{len(config_values)} configuration values**, "
        f"**{len(anchor_entries)} YAML anchors** under `project.custom`.",
        "",
        "---",
        "",
        "## Feature Flags",
        "",
        "Boolean flags that gate task/flow execution via `when:` clauses.",
        "",
        "| Flag | Default | Used in `when:` clauses |",
        "|------|---------|------------------------|",
    ]

    for key, value in sorted(boolean_flags, key=lambda x: x[0]):
        uses = usage_map.get(key, [])
        use_count = f"{len(uses)} flow step(s)" if uses else "—"
        lines.append(f"| `{key}` | `{value}` | {use_count} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Flag Usage Detail")
    lines.append("")

    for key, value in sorted(boolean_flags, key=lambda x: x[0]):
        uses = usage_map.get(key, [])
        if not uses:
            continue
        lines.append(f"### `{key}` (default: `{value}`)")
        lines.append("")
        for u in uses:
            lines.append(f"- {u}")
        lines.append("")

    if "(org_config.scratch)" in usage_map:
        lines.append("### `org_config.scratch` (runtime)")
        lines.append("")
        for u in usage_map["(org_config.scratch)"]:
            lines.append(f"- {u}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Configuration Values")
    lines.append("")
    lines.append("Non-boolean scalar values under `project.custom` used as YAML anchors "
                 "for context definitions, dataset paths, sleep durations, etc.")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("|-----|-------|")

    for key, value in sorted(config_values, key=lambda x: x[0]):
        val_str = str(value)
        if len(val_str) > 80:
            val_str = val_str[:77] + "..."
        lines.append(f"| `{key}` | `{val_str}` |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## YAML Anchors (lists/maps)")
    lines.append("")
    lines.append("These `project.custom` entries are YAML anchors (lists or maps) reused "
                 "throughout the file for permission sets, decision tables, dataset paths, etc.")
    lines.append("")

    for key, value in sorted(anchor_entries, key=lambda x: x[0]):
        lines.append(f"### `{key}`")
        lines.append("")
        if isinstance(value, list):
            lines.append(f"*{len(value)} items:*")
            lines.append("")
            for item in value:
                lines.append(f"- `{item}`")
        elif isinstance(value, dict):
            lines.append(f"*{len(value)} keys:*")
            lines.append("")
            for k, v in value.items():
                lines.append(f"- `{k}`: `{v}`")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_file(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN — would write {path} ({len(content)} chars)")
        print(f"{'='*60}")
        preview = content[:2000]
        print(preview)
        if len(content) > 2000:
            print(f"\n... ({len(content) - 2000} more characters)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  Wrote {path.relative_to(ROOT)} ({len(content):,} chars)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate CCI reference docs from cumulusci.yml"
    )
    parser.add_argument("--tasks-only", action="store_true")
    parser.add_argument("--flows-only", action="store_true")
    parser.add_argument("--flags-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not CCI_YML.exists():
        print(f"ERROR: {CCI_YML} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {CCI_YML.relative_to(ROOT)} ...")
    data = load_cci()

    generate_all = not (args.tasks_only or args.flows_only or args.flags_only)

    if generate_all or args.tasks_only:
        content = generate_tasks_reference(data)
        write_file(OUTPUT_DIR / "tasks-reference.md", content, args.dry_run)

    if generate_all or args.flows_only:
        content = generate_flows_reference(data)
        write_file(OUTPUT_DIR / "flows-reference.md", content, args.dry_run)

    if generate_all or args.flags_only:
        content = generate_feature_flags(data)
        write_file(OUTPUT_DIR / "feature-flags.md", content, args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
