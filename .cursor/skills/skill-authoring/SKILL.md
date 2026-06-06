# Skill Authoring — Lifecycle and Registration

Use this skill when creating, changing, splitting, registering, or testing an
AI-agent skill in this repository. Skills are plain markdown guides that live
under `.cursor/skills/` for historical reasons, but they must remain consumable
by Cursor, Claude Code, GitHub Copilot, Codex, Windsurf, Aider, and any other
agent that can read repository files.

## Quick Rules

1. **Prefer a skill for detailed, repeatable procedure** — create or update a
   skill when the guidance is task-specific, multi-step, example-heavy, or only
   relevant after an agent has chosen that task.
2. **Keep `AGENTS.md` for universal routing and safety** — update `AGENTS.md`
   when every agent must see the rule before selecting a skill, or when adding a
   skill/sub-file to the repository-wide index.
3. **New top-level skills should include** Quick Rules, DO NOT, Entry Conditions,
   Examples, and Validation Checks sections. Quick Rules and DO NOT are required
   and present in every skill today; existing skills are migrated to add Entry
   Conditions, Examples, and Validation Checks incrementally.
4. **Use progressive disclosure** — split sub-files when a skill is approaching
   context bloat, has variant-specific detail, or contains references that only
   some tasks need.
5. **Register new skills everywhere agents discover them** — update
   `.cursor/skills/README.md`, `AGENTS.md`, and `.claude/skill-manifest.yml`;
   update `.github/copilot-instructions.md` only when Copilot's entry-point
   guidance changes.
6. **Add Cursor rules only for file-pattern reminders** — rules are for
   automatic injection on predictable globs; keep the canonical detailed
   workflow in the skill.
7. **Test as a non-Cursor reader** — verify an agent can discover the skill from
   `AGENTS.md` / `.cursor/skills/README.md`, resolve it through the manifest
   when applicable, and use it without Cursor-only assumptions.

## DO NOT

- **DO NOT** duplicate long procedural content across `AGENTS.md`,
  `.cursor/skills/README.md`, Cursor rules, and skill files. Keep the detailed
  workflow in one skill and point to it.
- **DO NOT** bury safety-critical repository-wide rules only inside a skill. Put
  those rules in `AGENTS.md` so every agent sees them before acting.
- **DO NOT** add sub-files that are not linked from the parent `SKILL.md`; hidden
  files are not discoverable enough for non-Cursor agents.
- **DO NOT** make a Cursor rule the only source of guidance. Cursor rules are
  supplemental; non-Cursor agents must be able to read equivalent instructions
  from `AGENTS.md` or a skill.
- **DO NOT** edit `CLAUDE.md`; it is an entry-point pointer/symlink to
  `AGENTS.md` in this repository pattern.
- **DO NOT** register PMOS-facing skills in `.claude/skill-manifest.yml` without
  a clear `purpose`, valid `path`, and explicit `consumed_by_pmos` value.

---

## Entry Conditions

Read this skill before making skill-lifecycle changes, including:

| Task | Use this skill? | Notes |
|------|-----------------|-------|
| Create a new `.cursor/skills/<name>/SKILL.md` | Yes | Also update skill indexes and manifest. |
| Add a sub-file under an existing skill | Yes | Link it from the parent skill and `AGENTS.md` Skill Sub-Files table when it is broadly useful. |
| Add or change `.cursor/rules/*.mdc` | Yes | Confirm the rule mirrors a skill or repository-wide source. |
| Add one universal safety guard | Usually no | Put universal rules directly in `AGENTS.md`; update a skill only if the detailed workflow changes. |
| Add examples/checklists for one task area | Yes | Prefer skill content over `AGENTS.md` detail. |
| Change cross-repo skill discoverability | Yes | Update `.claude/skill-manifest.yml` and test the resolver. |

---

## New Skill vs. `AGENTS.md`

### Create a new skill when guidance is specialized

Create a new skill when at least two of these are true:

- The workflow applies to a specific task family, not every repository action.
- The guidance needs examples, decision tables, validation commands, or
  troubleshooting branches.
- The content would make `AGENTS.md` longer without helping every agent.
- Agents should load it only after recognizing a task type.
- The workflow may grow sub-files, references, scripts, or templates.

Good skill candidates:

- Authoring release enablement exercises.
- Creating SFDMU data plans.
- Validating ERD/schema drift.
- Writing Robot Framework tests.
- Authoring and registering AI-agent skills.

### Update `AGENTS.md` when guidance is universal

Update `AGENTS.md` when the rule must be visible before an agent chooses a
skill, including:

- Safety-critical DO NOT rules.
- Repository-wide conventions.
- Skill router entries for new top-level skills.
- Skill sub-file discovery rows for broadly useful sub-files.
- File-specific rule inventory updates.
- Entry-point changes that affect all tools.

### Update an existing skill instead of creating a new one when it fits

Update an existing skill when the new guidance is an extension of an existing
workflow and does not require independent routing. If the new content is large
or optional, add a linked sub-file rather than a new top-level skill.

---

## Required Sections for Skills

Every top-level `SKILL.md` should include these sections near the top, in this
order where practical:

1. `# <Skill Name> — <Short Purpose>`
2. Intro paragraph: what the skill is for and who can consume it.
3. `## Quick Rules`
   - 5-8 numbered rules.
   - State the most important decisions and commands.
4. `## DO NOT`
   - Explicit safety constraints.
   - Include destructive actions, generated-output rules, source-of-truth rules,
     and tool-specific traps.
5. `## Entry Conditions`
   - Table or bullets describing when to read the skill.
   - Include adjacent cases that should use another skill or `AGENTS.md`.
6. Main workflow sections.
7. `## Examples`
   - Small, concrete examples that demonstrate routing and expected edits.
8. `## Validation Checks`
   - Commands and review checks agents should run before commit/PR.

Use imperative wording. Prefer concise tables and short examples over long
narrative. Keep detailed reference material in linked sub-files.

---

## Progressive Disclosure: When to Split Sub-Files

Split a sub-file when any of these are true:

- The top-level skill is becoming difficult to scan or is approaching a few
  hundred lines.
- Only some tasks need the content, such as one product domain, one framework,
  one release, or one advanced troubleshooting path.
- The content is reference-heavy: generated indexes, object maps, feature
  inventories, examples, or large decision tables.
- The content changes on a different cadence from the parent skill.
- A Cursor rule or another skill needs to point agents directly to that focused
  topic.

Sub-file rules:

1. Place the file under the parent skill directory unless it is a shared docs
   artifact that already belongs elsewhere.
2. Link the sub-file from the parent `SKILL.md` with a clear "read this when..."
   condition.
3. Add the sub-file to `AGENTS.md` Skill Sub-Files when it is broadly useful or
   likely to be selected directly by non-Cursor agents.
4. Keep sub-files one level deep when possible. Avoid nested reference chains.
5. If a sub-file is generated, mark it as generated and document the command
   that refreshes it.

---

## Registration Checklist

### `.cursor/skills/README.md`

Update the Skill Router when adding a top-level skill. Include:

- A user-intent phrase in the `I need to...` column.
- A short human-readable skill name.
- The relative entry point, usually `<skill-folder>/SKILL.md`.

Also update the "How Skills Are Structured" section if the required skill
structure changes, and update the Cursor rules table when adding or removing a
rule.

### `AGENTS.md`

Update `AGENTS.md` for:

- New top-level skill rows in **AI Agent Skill Index**.
- New broadly useful sub-file rows in **Skill Sub-Files**.
- New or changed Cursor rules in **File-Specific Rules**.
- New universal safety guards or project-wide conventions.

Keep `AGENTS.md` concise. It routes agents and defines global rules; it should
not duplicate the full skill body.

### `.claude/skill-manifest.yml`

Update the manifest when the skill should be discoverable through the cross-repo
skill resolver or consumed by PMOS workflows. Add a `foundations.skills`
entry with:

```yaml
- id: skill-authoring
  path: .cursor/skills/skill-authoring/SKILL.md
  purpose: "Skill lifecycle, registration, Cursor rule, and non-Cursor consumption guidance"
  consumed_by_pmos: []
```

Use additional fields only when they add real resolver value, such as
`sub_skills`, `tooling`, `grounding_inputs`, or `governs`.

### `.github/copilot-instructions.md`

This file should remain a concise pointer to `AGENTS.md` and the skill system.
Update it only when:

- The canonical entry points change.
- Copilot needs a new quick-start step to discover or consume skills.
- The rule/skill layout changes in a way that affects Copilot users.

Do not mirror every skill row here; Copilot should read `AGENTS.md` for the
canonical index.

---

## Cursor Rules for File-Pattern Injection

Add a Cursor rule when all of these are true:

1. The guidance is useful exactly when editing a predictable file pattern.
2. Forgetting the guidance commonly causes review churn or unsafe changes.
3. The rule can be short and point to a canonical skill or `AGENTS.md` section.
4. Non-Cursor agents have an equivalent readable source.

Create `.cursor/rules/<topic>.mdc` with frontmatter like:

```yaml
---
description: Short reminder for the rule picker
globs:
  - path/or/glob/**/*.ext
alwaysApply: false
---
```

Then include:

- A short heading.
- 3-6 quick checks.
- A link to the canonical skill or `AGENTS.md` section.

After adding a rule:

1. Add it to `.cursor/skills/README.md` File-Specific Rules table.
2. Add it to `AGENTS.md` File-Specific Rules table.
3. Confirm it does not replace the skill; it should only route or remind.

---

## Testing Non-Cursor Consumption

Run these checks before committing a new or materially changed skill:

1. **Discovery from repository entry points**
   - Confirm `AGENTS.md` lists the skill or sub-file.
   - Confirm `.cursor/skills/README.md` lists top-level skills.
   - Confirm `.github/copilot-instructions.md` still points agents to
     `AGENTS.md` and `.cursor/skills/*/SKILL.md`.
2. **Manifest resolution**
   - Run `python scripts/ai/skill_manifest.py --check` when the manifest changes.
   - Run `python scripts/ai/skill_manifest.py --list-skills foundations` and
     confirm the new skill appears when it is manifest-registered.
3. **Plain-file readability**
   - Open the skill with `sed -n '1,160p' .cursor/skills/<name>/SKILL.md` and
     confirm a non-Cursor agent can understand the entry conditions, DO NOT
     rules, examples, and validation checks without hidden Cursor context.
4. **Rule parity**
   - If a Cursor rule was added, confirm the rule points to the skill and the
     same guidance is available outside Cursor.
5. **Doc consistency**
   - Follow `.cursor/skills/doc-consistency/SKILL.md` before PR.

---

## Examples

### Example 1 — Add a new top-level skill

User request: "Create a skill for authoring pricing waterfall examples."

Do:

1. Create `.cursor/skills/pricing-waterfall-authoring/SKILL.md`.
2. Include Quick Rules, DO NOT, Entry Conditions, Examples, and Validation
   Checks.
3. Add a Skill Router row in `.cursor/skills/README.md`.
4. Add an AI Agent Skill Index row in `AGENTS.md`.
5. Add a manifest entry if PMOS or cross-repo consumers should discover it.
6. Run validation checks and commit all touched files together.

### Example 2 — Add a focused sub-file

User request: "Add more detailed Robot shadow DOM patterns."

Do:

1. Add or update `.cursor/skills/robot-testing/setup-ui-shadow-dom.md`.
2. Link it from `.cursor/skills/robot-testing/SKILL.md` with a read condition.
3. Add or update the `AGENTS.md` Skill Sub-Files row.
4. Do not create a separate top-level skill unless the workflow needs separate
   routing.

### Example 3 — Add a Cursor rule

User request: "Agents keep forgetting to validate skill indexes after editing
skills."

Do:

1. Add or update a `.cursor/rules/*.mdc` rule for `.cursor/skills/**/*.md`.
2. Keep the rule short and point to this skill plus doc-consistency.
3. Update `AGENTS.md` and `.cursor/skills/README.md` rule tables.
4. Verify non-Cursor agents can get the same instructions from this skill.

## Validation Checks

For skill-authoring changes, run the applicable checks:

```bash
python scripts/ai/skill_manifest.py --check
python scripts/ai/skill_manifest.py --list-skills foundations
python scripts/validate_sfdmu_v5_datasets.py
```

Also review:

- `git diff --stat` for unintended generated or runtime files.
- `AGENTS.md` Skill Index, Skill Sub-Files, and File-Specific Rules tables.
- `.cursor/skills/README.md` Skill Router and File-Specific Rules tables.
- `.github/copilot-instructions.md` quick-start and entry-point guidance.
- `.claude/skill-manifest.yml` path validity for any new manifest entry.
