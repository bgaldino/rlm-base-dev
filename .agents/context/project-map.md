# Project Map — Revenue Cloud Base Foundations

## Repository Snapshot

- **Repository:** `rlm-base-dev`
- **CCI project:** `rlm-base`
- **Salesforce target:** Release 262 / Summer '26
- **API version:** `67.0`
- **Source format:** SFDX
- **Default branch:** `main`
- **Active release branch in manifest:** `262`

## Agent Memory Files

- `.agents/context/project-memory.json` — deterministic machine-readable project memory.
- `.agents/schemas/project-memory.schema.json` — JSON Schema for validating future updates.
- `.agents/context/project-map.md` — human-readable orientation map for agents.

## Ownership Map

| Path | Ownership / Purpose | Agent Notes |
| --- | --- | --- |
| `cumulusci.yml` | CCI project, task, flow, org, and feature-flag configuration | After edits, run `python scripts/ai/generate_cci_reference.py` and commit regenerated references. |
| `config/` | Scratch org definition configuration | Review org shape and feature changes against Release 262 expectations. |
| `force-app/` | Core SFDX metadata | Keep profile and object safety constraints in mind. |
| `unpackaged/pre/` | Pre-deploy metadata | Deploys before core metadata/data. |
| `unpackaged/post_*/` | Feature-specific post-deploy metadata | Verify edition and feature guards when adding bundles. |
| `unpackaged/post_ux/` | Generated UX assembly output | Forbidden for manual edits; edit `templates/` instead. |
| `templates/` | Source of truth for generated UX | Run the UX assembler or drift flows to regenerate output. |
| `datasets/sfdmu/` | SFDMU v5 plans and CSVs | Validate with `python scripts/validate_sfdmu_v5_datasets.py`; keep v5 external ID rules. |
| `datasets/context_plans/` | Context definition plans | Keep context plan names aligned with CCI task options. |
| `datasets/constraints/` | Configurator constraint data | Coordinate data changes with validation/import tooling. |
| `datasets/tooling/` | Tooling API metadata exports | Treat as metadata snapshots. |
| `scripts/apex/` | Apex activation/deletion scripts | Keep scripts bulk-safe and avoid unsafe single-record loops. |
| `scripts/ai/` | Agent support utilities | Includes CCI reference generation and ERD/manifest helpers. |
| `scripts/cml/` | CML utilities | Export/import/validation helpers for constraint model work. |
| `scripts/erd/` | Schema and ERD tooling | Use for Release 260/262 schema comparisons and ERD generation. |
| `scripts/soql/` | Reusable SOQL queries | Prefer checked-in query files for repeatable analysis. |
| `tasks/` | Custom Python CCI tasks | Use `org_config.username` for `sf` CLI; reserve tokens for REST. |
| `tests/` | Shell-based integration tests | Run relevant test scripts for changed behavior. |
| `robot/rlm-base/` | Robot Framework tests | Setup and E2E automation. |
| `orgs/` | Scratch org definitions | Review for accidental churn before merge. |
| `postman/` | RLM API collections | Manual/API testing artifacts. |
| `docs/` | Documentation | Use lower-kebab-case filenames under `docs/`. |

## High-Risk Safety Constraints

1. Never hand edit `unpackaged/post_ux/`; edit `templates/` and regenerate.
2. Do not add `layoutAssignment` or `applicationVisibilities` to `force-app/` profiles; use `templates/profiles/`.
3. Do not add object metadata with `actionOverrides` to `force-app/`; use `templates/objects/`.
4. Do not switch SFDMU `Upsert` plans to `Insert` plus `deleteOldData: true` without explicit user approval after explaining the applicable v5 bug and confirming no safer external ID exists.
5. Do not pass `access_token` to `sf` CLI commands; use usernames or aliases with `--target-org`.
6. Do not add `EmailTemplatePage` flexipages to `templates/flexipages/`.
7. Do not commit real emails in `rlm.network-meta.xml`; keep placeholders.
8. Do not commit or push directly to `main`.

## Generated References

Generated CCI references are sourced from `cumulusci.yml` and regenerated with:

```bash
python scripts/ai/generate_cci_reference.py
```

Tracked generated references currently recorded in project memory:

- `.cursor/skills/cci-orchestration/tasks-reference.md`
- `.cursor/skills/cci-orchestration/flows-reference.md`
- `.cursor/skills/cci-orchestration/feature-flags.md`
- `docs/references/cci-task-reference.md`

## External Systems

- **CumulusCI (CCI):** task and flow orchestration. Use `cci ... --org <cci_alias>`.
- **SFDMU v5:** data import/export through `sf sfdmu run`; v5.0.0+ is required.
- **Salesforce CLI:** metadata/data/org commands. Use `sf ... --target-org <sf_alias_or_username>`.
- **Robot Framework:** setup and E2E test automation in `robot/rlm-base/`.
- **PMOS manifest:** cross-repo skill manifest at `.claude/skill-manifest.yml`; validate with `python scripts/ai/skill_manifest.py --check` when using PMOS integration.

## Recommended Agent Startup Checklist

1. Read `AGENTS.md` and any nested `AGENTS.md` files in paths you will edit.
2. Read `.agents/context/project-memory.json` for deterministic repo memory.
3. Use `.agents/schemas/project-memory.schema.json` to validate memory edits.
4. Inspect `git status --short` before and after changes.
5. Run the smallest relevant validation command for the files you touched.
6. Commit changes on the current branch and open a PR when code or documentation changes are made.
