# Rule / Skill Coverage Matrix

> **Auto-generated** by `scripts/ai/analyze_agent_tooling.py coverage`.
> Do not edit manually — re-run the analyzer after changing `AGENTS.md`, `.cursor/rules/`, or `.cursor/skills/README.md`.

## Summary

- Cursor rule files found: **10**
- Rules not listed in `.cursor/skills/README.md`: **2**
- Recommended skill rules still missing: **6**
- High-risk AGENTS.md paths lacking both a rule and analyzer check: **4**

## Rule Matrix

| Rule file path | Glob pattern | Equivalent skill path | Has DO NOT section | Appears in AGENTS.md | Listed in skill README | Recommended owner/domain |
|---|---|---|---|---|---|---|
| `.cursor/rules/apex-classes.mdc` | `unpackaged/**/*.cls`<br>`force-app/**/*.cls` | (stand-alone) | Yes | Yes | No | Apex |
| `.cursor/rules/apex-scripts.mdc` | `scripts/apex/**/*.apex` | `troubleshooting/SKILL.md` | Yes | Yes | Yes | Apex |
| `.cursor/rules/cci-python-tasks.mdc` | `tasks/**/*.py` | `cci-orchestration/custom-task-authoring.md` | Yes | Yes | Yes | CCI Orchestration |
| `.cursor/rules/cci-task-definitions.mdc` | `cumulusci.yml` | `cci-orchestration/SKILL.md` | Yes | Yes | Yes | CCI Orchestration |
| `.cursor/rules/doc-review.mdc` | `cumulusci.yml`<br>`tasks/**/*.py`<br>`datasets/sfdmu/**/export.json`<br>`datasets/sfdmu/**/*.csv`<br>`robot/**/*.robot`<br>`.cursor/skills/**/*.md` | `doc-consistency/SKILL.md` | No | Yes | Yes | Doc Consistency |
| `.cursor/rules/lwc-components.mdc` | `unpackaged/**/lwc/**/*.html`<br>`unpackaged/**/lwc/**/*.js`<br>`force-app/**/lwc/**/*.html`<br>`force-app/**/lwc/**/*.js` | (stand-alone) | Yes | Yes | No | Lightning Web Components |
| `.cursor/rules/robot-tests.mdc` | `robot/**/*.robot`<br>`robot/**/*.py` | `robot-testing/SKILL.md` | Yes | Yes | Yes | Robot Testing |
| `.cursor/rules/sfdmu-csv-data.mdc` | `datasets/sfdmu/**/*.csv` | `sfdmu-data-plans/SKILL.md` | Yes | Yes | Yes | SFDMU Data Plans |
| `.cursor/rules/sfdmu-export-json.mdc` | `**/export.json` | `sfdmu-data-plans/SKILL.md` | Yes | Yes | Yes | SFDMU Data Plans |
| `.cursor/rules/ux-templates.mdc` | `templates/**` | `repo-integration/SKILL.md` | Yes | Yes | Yes | UX Assembly |

## Flags

### 1. Rules not listed in the skill README

- `.cursor/rules/apex-classes.mdc` — owner/domain: **Apex**; add it to `.cursor/skills/README.md` or document why it is intentionally omitted.
- `.cursor/rules/lwc-components.mdc` — owner/domain: **Lightning Web Components**; add it to `.cursor/skills/README.md` or document why it is intentionally omitted.

### 2. Skills with no corresponding rule where file-specific auto-injection would reduce risk

| Skill path | Suggested rule | Suggested glob(s) | Owner/domain | Reason |
|---|---|---|---|---|
| `schema-validation/SKILL.md` | `schema-validation.mdc` | `docs/erds/**`<br>`scripts/erd/**/*.py` | Schema Validation | ERD/schema files are safety-critical and the skill has no file-triggered rule today. |
| `release-enablement/SKILL.md` | `release-enablement.mdc` | `docs/enablement/**`<br>`docs/salesforce/**` | Release Enablement | Enablement docs have release-specific source/extract conventions that are easy to miss. |
| `rlm-business-apis/SKILL.md` | `rlm-business-apis.mdc` | `postman/**`<br>`scripts/soql/**` | Business APIs | API collections and SOQL files benefit from endpoint/auth/query guardrails at edit time. |
| `pmos-integration/SKILL.md` | `pmos-integration.mdc` | `.claude/skill-manifest.yml` | PMOS Integration | The cross-repo skill manifest is a single integration point with no auto-injected rule. |
| `revenue-cloud-docs/SKILL.md` | `revenue-cloud-docs.mdc` | `docs/salesforce/**`<br>`docs/enablement/**` | Revenue Cloud Docs | Grounding product claims against Salesforce Help is high-risk but not file-triggered. |
| `repo-integration/ux-assembly-retrieve.md` | `post-ux-generated-output.mdc` | `unpackaged/post_ux/**` | UX Assembly | `unpackaged/post_ux/` is generated output and should warn on any direct edit. |

### 3. High-risk paths from AGENTS.md that lack a rule or explicit analyzer check

| Path | Owner/domain | AGENTS.md source | Expected rule | Explicit analyzer check | Reason |
|---|---|---|---|---|---|
| `unpackaged/post_ux/**` | UX Assembly | AGENTS.md DO NOT #1 and Repository Layout | `post-ux-generated-output.mdc` | — | Generated UX output must not be edited directly. |
| `force-app/**/profiles/*.profile-meta.xml` | UX Assembly / Profiles | AGENTS.md DO NOT #2 | `force-app-profile-safety.mdc` | — | Force-app profiles should stay classAccesses-only; layout/application visibility belongs in templates. |
| `force-app/**/*.object-meta.xml` | UX Assembly / Objects | AGENTS.md DO NOT #3 | `force-app-object-safety.mdc` | — | Object actionOverrides/compact layout assignment belong in templates, not force-app objects. |
| `**/rlm.network-meta.xml` | PRM Network | AGENTS.md DO NOT #7 | `network-email-safety.mdc` | — | Network metadata must keep placeholder emails; deploy tasks patch/revert real values. |

## Notes

- `Appears in AGENTS.md` is true when the rule filename is present in the root `AGENTS.md` file-specific rule table.
- `Listed in skill README` is true when the rule filename is present in `.cursor/skills/README.md`.
- High-risk path coverage is satisfied by either a matching `.cursor/rules/*.mdc` glob or an explicit analyzer/validator script listed in this report.
