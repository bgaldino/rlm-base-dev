# AI Agent Tooling Scripts

Scripts that support AI agent workflows by providing queryable interfaces to
project data and auto-generating reference documentation for AI skills.

These scripts are consumed by AI agents and the progressive-disclosure skill
system (`.cursor/skills/`). They are **not** part of the CCI deployment
pipeline and work with any AI coding agent.

---

## Scripts

### `query_erd.py`

CLI tool for querying the Revenue Cloud data model stored in
`docs/erds/erd-data.json` — Release 262 (Summer '26, API v67.0): 263
objects, 4,190 platform fields, 674 verified relationship edges (custom
fields excluded). The same JSON also exposes 1,135 reference fields in
total — see the "Reference Fields" line in `query_erd.py stats` for the
distinction. Avoids loading the 30K-line JSON file directly into AI
context.

```bash
python scripts/ai/query_erd.py describe Product2         # fields, relationships, domain
python scripts/ai/query_erd.py relationships Product2     # all objects linked to/from Product2
python scripts/ai/query_erd.py domain Billing             # all objects in a domain
python scripts/ai/query_erd.py path Product2 Invoice      # relationship path between two objects
python scripts/ai/query_erd.py search "usage"             # fuzzy object/field search
python scripts/ai/query_erd.py stats                      # domain counts summary
```

**Data source:** `docs/erds/erd-data.json`
**Used by:** `.cursor/skills/revenue-cloud-data-model/SKILL.md`


### `analyze_agent_tooling.py`

Generates an AI-agent rule/skill coverage report that compares `.cursor/rules/`
with `AGENTS.md` and `.cursor/skills/README.md`, then flags rule README gaps,
recommended file-specific rule opportunities, and high-risk AGENTS.md paths
without rule or analyzer coverage.

```bash
python scripts/ai/analyze_agent_tooling.py              # write .agents/context/rule-skill-coverage.md
python scripts/ai/analyze_agent_tooling.py --dry-run    # preview without writing
```

**Data sources:** `AGENTS.md`, `.cursor/rules/`, `.cursor/skills/README.md`
**Output:** `.agents/context/rule-skill-coverage.md`

### `generate_cci_reference.py`

Parses `cumulusci.yml` and generates three auto-updating reference files for the
CCI orchestration skill. Run after editing `cumulusci.yml` to keep AI agent
knowledge current.

```bash
python scripts/ai/generate_cci_reference.py                # regenerate all 3 files
python scripts/ai/generate_cci_reference.py --tasks-only    # just tasks-reference.md
python scripts/ai/generate_cci_reference.py --flows-only    # just flows-reference.md
python scripts/ai/generate_cci_reference.py --flags-only    # just feature-flags.md
python scripts/ai/generate_cci_reference.py --dry-run       # preview without writing
```

**Data source:** `cumulusci.yml`
**Outputs:**
- `.cursor/skills/cci-orchestration/tasks-reference.md` — all tasks by group
- `.cursor/skills/cci-orchestration/flows-reference.md` — all flows with step trees
- `.cursor/skills/cci-orchestration/feature-flags.md` — feature flags with usage index

**Used by:** `.cursor/skills/cci-orchestration/SKILL.md`

---

## Dependencies

- **Python 3.10+** (the schema-diff and skill-manifest scripts use PEP 604
  union types like `list[Path] | None`; the repo's CI workflow pins Python
  3.13 and the README recommends 3.12 for CumulusCI itself, so 3.10 is a
  safe lower bound and is what we test against in practice). The previous
  "3.8+" claim predated the schema-diff tooling.
- **PyYAML** — used by `generate_cci_reference.py` and `skill_manifest.py`
  (available in the CCI venv)
- No other external dependencies

---

## Related

- `AGENTS.md` — Canonical AI agent instructions (repo root)
- `.cursor/skills/` — Per-topic skill guides (plain markdown, any agent)
- `.cursor/rules/` — File-specific auto-injection rules (Cursor only)
