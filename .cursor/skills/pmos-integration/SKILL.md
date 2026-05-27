---
name: pmos-integration
description: >-
  Cross-repo skill manifest pattern connecting Foundations (rlm-base-dev) and
  PMOS (pmos-revenue-cloud). Use when a skill needs to read content from the
  other repo (PRDs, demo scripts, capability roadmap, schema, Help articles,
  scenario reference) without forking or duplicating it. Documents the temporal
  split (PMOS = future state, Foundations = current state), the resolver, and
  when each side is canonical.
---

# PMOS ↔ Foundations Integration

A cross-repo skill manifest that lets agents in either repo discover and consume content from the other read-only. Both repos work standalone today; the manifest upgrades what each can do when the other is present.

## Quick Rules

1. **Temporal split is the framing.** PMOS is canonical for *future state* (PRDs, roadmap, proposed schema changes). Foundations is canonical for *current state* (built schema, deployed flags, real records). Don't put proposed-but-not-built content in Foundations; don't put runtime-verified state in PMOS.
2. **Manifest is read-only on both sides.** Foundations consumes PMOS via local clone path; PMOS does the same in reverse. Each maintainer keeps full control of what they own.
3. **Filesystem-level, not API-level.** No servers, no auth, no CI dependency. The resolver looks for `$FOUNDATIONS_REPO_ROOT` / `$PMOS_REPO_ROOT` env vars or sibling-directory layout (`../pmos-revenue-cloud`, `../rlm-base-dev`).
4. **Degrades gracefully.** If a sibling clone isn't present, the consumer skill operates standalone. Nothing breaks; the upgrade just isn't available.
5. **Per-skill opt-in.** Each side decides which of their skills consume from the other. Not all-or-nothing.
6. **PMOS is document-centric — not a code project.** Don't propose Python or build automation in PMOS. PMOS's side of the manifest is purely declarative YAML.

## DO NOT

1. **DO NOT** copy or fork PMOS content into Foundations (or vice versa). The whole point is no duplication — the manifest is the wire.
2. **DO NOT** use git submodules or symlinks for cross-repo grounding. They're operationally fragile across OS layouts and break Claude Code skill discovery.
3. **DO NOT** ship Python/build tooling into PMOS. PMOS is doc-centric; the resolver lives in Foundations and reads PMOS content as static files.
4. **DO NOT** assume PMOS data is current-state truth. Per the temporal split, PMOS may carry proposed/future content that hasn't been built yet. For real-state queries (does this field exist? does this flag deploy?), use Foundations.
5. **DO NOT** assume Foundations covers future-state content. PMOS owns roadmap, PRDs, capability map. Foundations doesn't carry that authoritatively.

## What Each Repo Owns

| Concern | Canonical source | Why |
|---|---|---|
| Object/field schema (what exists today) | **Foundations** (`docs/erds/erd-data.json`) | Verified against live orgs and Core UDD source |
| 838 Salesforce Help articles per release | **Foundations** (`docs/salesforce/{release}/help/`) | Mirrored from help.salesforce.com, diffable across releases |
| QB scenario reference (real demo records) | **Foundations** (`docs/enablement/master/qb-scenario-reference.md`) | The records `prepare_rlm_org` actually loads |
| RLM business APIs reference | **Foundations** (`.cursor/skills/rlm-business-apis/`) | API endpoints + working examples |
| `prepare_rlm_org` flow + 36 feature flags | **Foundations** (`cumulusci.yml`) | The build itself |
| PRDs (proposed features) | **PMOS** (`docs/Releases/{release}/`) | Per-release authoring layer |
| Roadmap / capability map | **PMOS** (`context/CAPABILITIES.md`, 218 rows) | PM-owned status: Beta → GA → deprecated |
| PM authoring skills (prd, demo-script, sales-enablement, release-notes, presentation, documentation, spec, technical-review) | **PMOS** (`.claude/skills/`) | 61 skills total in PMOS |
| Multi-agent review personas (csm, eng-lead, ux-designer, etc.) | **PMOS** (`.claude/agents/`) | 16 reviewer agent definitions |
| Per-feature knowledge packages (~25k lines) | **PMOS** (`packages/available/revenue-cloud-*/`) | 11 RC packages: billing, pricing, configurator, pcm, transaction-mgmt, usage, ui-ux, performance, integrations, approvals, contracts |

## The Mechanism

### Manifest (this repo)

`/Users/bgaldino/Documents/GitHub/bgaldino/_bgaldino/rlm-base-dev/.claude/skill-manifest.yml`

Declares:
- Foundations skills available to PMOS consumers (id, path, brief)
- Foundations grounding artifacts (ERD, Help mirror, qb-scenario, API reference)
- Local-path hints for the consumer (env vars + fallback paths)

### Resolver

`scripts/ai/skill_manifest.py` — small Python helper:

```python
from scripts.ai.skill_manifest import load_manifest, resolve_grounding

m = load_manifest()
qb = resolve_grounding(m, repo='foundations', key='qb_scenario')
# qb is a Path object (or None if Foundations clone can't be found)

if qb:
    text = qb.read_text()
```

### CLI diagnostics

```bash
python scripts/ai/skill_manifest.py --check
python scripts/ai/skill_manifest.py --list-skills foundations
python scripts/ai/skill_manifest.py --list-skills pmos
```

## When to Use the Manifest

### From Foundations skills consuming PMOS content

| Scenario | Example |
|---|---|
| Generate a release-aware demo script | `qb-demo-script` skill reads PMOS `demo-script` for narrative voice; grounds records on Foundations qb-scenario-reference |
| Author per-release enablement | `release-enablement` reads PMOS PRDs to know what features are coming |
| Plan a data plan update | (planned) `apply_pmos_data_plan_update` reads PRD frontmatter `proposed_data_plan_changes:` and produces a draft SFDMU plan diff |
| Build trailhead module scripts | (planned) read PMOS `demo-script` patterns; ground records on Foundations |

### From PMOS skills consuming Foundations content

| Scenario | Example |
|---|---|
| Author a PRD that cites real schema | `prd` skill reads Foundations ERD via resolver instead of stale narrative summaries |
| Generate a demo script with real records | `demo-script` reads Foundations qb-scenario-reference instead of inventing records |
| Author release notes against actual ship state | `release-notes` reads Foundations Help mirror diff between releases |
| Cite real API endpoints | `technical-review` reads Foundations `rlm-business-apis` skill instead of stale v61.0 examples in PMOS `context/ARCHITECTURE.md` |

## The Working Example

Foundations' `qb-demo-script` skill (shipped on the 262 branch) auto-generates the QuantumBit demo canvas grounded entirely on canonical Foundations sources (ERD, Help mirror, qb-scenario-reference, feature-index). Output at `docs/enablement/262/qb-demo-script.md`.

- **Today (standalone):** Works whether or not PMOS is present
- **With manifest fully wired:** Optionally invokes PMOS `presentation` for narrative-voice polish; PMOS `sales-enablement` for battle-card companion. None of those are dependencies — they're upgrades.

## What's Shipped, What's Not

### Shipped (Foundations side)
- ✅ `.claude/skill-manifest.yml` — Foundations declarations
- ✅ `scripts/ai/skill_manifest.py` — resolver
- ✅ `qb-demo-script` skill — first proof-of-pattern consumer

### In progress
- 🟡 PMOS-side manifest YAML (drafted at `.agents/artifacts/pmos-side-manifest-draft.md`, pending Arun → Sandy review)
- 🟡 PMOS Tier 0 hygiene fixes (drafted at `.agents/artifacts/pmos-tier-0-hygiene-ask.md` — 4 critical-path: legacy CPQ schema in `context/ARCHITECTURE.md`, v61.0 REST examples, invented Apex REST paths, healthcare residue in `demo-data`)

### Not yet built
- Per-skill PMOS opt-in PRs (one PR per skill that PMOS chooses to upgrade)
- `apply_pmos_data_plan_update` Foundations skill (planned)
- `proposed_data_plan_changes:` PRD frontmatter convention (Brian + Sandy alignment needed)
- CI gate that checks both repos' manifests stay in sync (Phase 6.3.5)

## Related Artifacts

- `.agents/artifacts/arun-pmos-skills-brief.md` — full briefing to Arun on the integration plan
- `.agents/artifacts/rlm-base-dev-and-pmos-research.md` — owner/purpose comparison
- `.agents/artifacts/integration-claim-validation-pmos.md` — line-by-line validation of pmos-analysis claims
- `.agents/artifacts/pmos-side-manifest-draft.md` — proposed PMOS-side YAML (Sandy's review pending)
- `.agents/artifacts/pmos-tier-0-hygiene-ask.md` — prioritized PMOS-internal hygiene
- `.agents/artifacts/skills-pmos-distribution.md` — how PMOS's package system works (and doesn't ship skills today)
- `.agents/artifacts/skills-pmos-enablement.md` — enablement-cluster integration plan
- `.agents/artifacts/ssot-pmos-comprehensive-reaudit.md` — comprehensive single-source-of-truth audit
- `.claude/skill-manifest.yml` — the actual manifest

## Future Direction (Not Asks)

The brief to Arun also surfaces a longer-term direction: **CX authoring directly into PMOS, with PMOS-published content becoming the upstream that Foundations mirrors.** PMOS's `doc-downloader` skill already pulls from Google Docs / Confluence / Quip / Slack / generic webpages — the `consumption` half of upstream-authoring is built. The `publish-back` half (PMOS → Help portal directly, or PMOS → CX docs system → Help) is genuinely net-new and would require PMOS + CX team coordination — explicitly not in scope for this skill.

The manifest pattern is agnostic to where content is canonically authored; entries shift over time as ownership evolves. The wire stays the same.
