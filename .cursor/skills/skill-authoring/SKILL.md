---
name: skill-authoring
description: >-
  Create, update, split, register, and validate AI-agent skills in Revenue Cloud
  Foundations. Use when editing skill entry points or sub-files, authoring discovery
  metadata, maintaining skill indexes, or checking tool-agnostic consumption and Cursor
  rule parity.
---

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
   Examples, and Validation Checks sections. Quick Rules is present in every
   skill today and DO NOT in most; existing skills are migrated to add Entry
   Conditions, Examples, and Validation Checks (and any missing DO NOT) incrementally.
4. **Use progressive disclosure** — split sub-files when a skill is approaching
   context bloat, has variant-specific detail, or contains references that only
   some tasks need.
5. **Register new skills everywhere agents discover them** — update
   `.cursor/skills/README.md`, `AGENTS.md`, and `.claude/skill-manifest.yml`;
   add matching directory links in `.agents/skills/` and `.claude/skills/`;
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
- **DO NOT** write a procedure around hardcoded instance names — a specific model,
  product, org, expression set or dataset. Teach the mechanism and how to **discover** the
  instances; use real names only as clearly-labelled examples. See below.

---

## Instances vs. mechanism

A skill that hardcodes the instances it happened to be written against becomes a runbook
for one scenario and quietly wrong for every other. It also ages badly: the moment a
vertical is added or a name changes, the skill is misleading rather than merely
incomplete.

**Write procedures against a placeholder, and give the reader a way to fill it in:**

| Do | Don't |
|----|-------|
| `-o version_full_names "<Version>"`, with a query that finds `<Version>` | `-o version_full_names "QuantumBitBundle_V1"` as the instruction |
| "the discriminator is `UsageType = 'Constraint'`" | "the constraint models are X, Y and Z" |
| A **Discovery** section near the top: what the org has, what the repo ships, what the flow uses | An inventory presented as the operative list |

**Real names are still valuable — in three specific places:**

1. **A clearly-labelled examples/worked-example section.** "Worked example — adding
   `QB-CMT-TKN-BND` to `QB-COMPLETE`; substitute your own."
2. **A "what this repo ships today" table**, marked as a snapshot that will age, with the
   discovery command that supersedes it.
3. **Recording a deliberate policy decision** that is genuinely repo-specific — e.g.
   "exactly one model per family may be active; Bundle is the chosen one, Complete and PCM
   are kept inactive for A/B". That is real, durable knowledge and belongs written down.

The distinction is whether the name is the **instruction** (wrong) or the **illustration
or recorded state** (right).

`.cursor/skills/expression-sets/SKILL.md` is the model to copy: it grounds its type table
in a live query, then lists instances in a column explicitly headed *"Shipped example(s)
in this repo"*.

**Scope the claim, too.** "Only one X may be active" is a different statement from "only
one X per family may be active"; the second is true here and the first is not. An
over-broad rule reads as authoritative and sends someone deactivating unrelated records.

---

## Entry Conditions

Read this skill before making skill-lifecycle changes, including:

| Task | Use this skill? | Notes |
|------|-----------------|-------|
| Create a new `.cursor/skills/<name>/SKILL.md` | Yes | Also update skill indexes and manifest. |
| Add a sub-file under an existing skill | Yes | Link it from the parent `SKILL.md`, which is the only place sub-files are registered. Do **not** add it to `AGENTS.md`. |
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

### Discovery metadata

Every top-level `SKILL.md` must start with YAML frontmatter containing `name`
and `description`, following the [Agent Skills specification](https://agentskills.io/specification):

```yaml
---
name: skill-name
description: >-
  Describe the capability and when an agent should select this skill.
---
```

- **`name`**: match the parent directory exactly; use 1–64 lowercase letters,
  digits, or hyphens, with no leading, trailing, or consecutive hyphens.
- **`description`**: a non-empty string of at most 1,024 characters. Describe
  both the capability and concrete task triggers. Distinguish adjacent skills
  where their scopes overlap; keep detailed procedures in the body.
- The stdlib-only repository gate accepts plain or quoted single-line strings
  and folded/literal blocks (`>`, `>-`, `|`, `|-`, with `+` also accepted).
  Use JSON-compatible double quotes or YAML single quotes; use a block for
  multiline text; folded blocks use one uniformly indented paragraph, and literal
  blocks support paragraph breaks. Required discovery fields must be unique top-level keys.
  Other YAML types, aliases and complex scalar syntax are outside this portable
  subset. This is a repository authoring constraint, not the full YAML specification.
- Preserve existing skill names and directories when adding metadata. Put
  frontmatter on the entry point; reference sub-files do not need it.
- Frontmatter enables metadata-based discovery in compatible tools. It does
  not replace the indexes and manifest below or configure native discovery
  paths for every agent.

### Native discovery links

Keep skill content under `.cursor/skills/<name>/`. For each top-level skill,
track a relative directory symlink in both `.agents/skills/` and
`.claude/skills/`, targeting `../../.cursor/skills/<name>`. Link the whole
directory so supporting files remain available; do not copy skill bodies.
When adding or retiring a skill, update both link sets in the same change.

For a new skill, run from the repository root, replacing `skill-name`:

```sh
ln -s ../../.cursor/skills/skill-name .agents/skills/skill-name
ln -s ../../.cursor/skills/skill-name .claude/skills/skill-name
```

Verify both paths resolve after a fresh Git checkout and are tracked as
symlinks (mode `120000` in `git ls-files -s`). Check the client's native
listing for missing or duplicate entries, then invoke one representative
skill. Record the tested client/version and any unavailable clients rather
than claiming universal support. See
[the discovery guide](../../../docs/guides/agent-skill-discovery.md) for
client verification and the catalog fallback.

### Instruction body

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
3. Describe it in the parent `SKILL.md`'s own sub-file list. That list is the
   only registry — `AGENTS.md` carries no second-level index, so a sub-file that
   is not described by its parent is effectively undiscoverable. **Write the
   filename as a code span (`` `sub-file.md` ``) or a Markdown link** — those are
   the two forms `analyze_agent_tooling.py check` recognizes as registration, so
   a name mentioned only in running prose fails the gate. A path relative to the
   skill directory, to `.cursor/skills/`, or to the repo root all work, as does a
   glob (`` `domains/*.md` ``) for a whole sub-directory.
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
- A new *directory* of helper scripts, as one row in **Script Reference** naming
  the owning skill — never the individual commands.
- New universal safety guards or project-wide conventions.

Do **not** update `AGENTS.md` for a new sub-file (the parent `SKILL.md` owns
that) or a new Cursor rule (`.cursor/skills/README.md` owns that).

Keep `AGENTS.md` concise. It routes agents and defines global rules; detailed
procedures belong in owning skills. This repository's working ceiling is
**25,000 bytes**, measured with `wc -c AGENTS.md`. This is a repository target,
not a universal model context limit. Codex's default `project_doc_max_bytes`
is **32 KiB (32,768 bytes)** for the combined project instruction chain;
nested instruction files also consume that budget. Other clients have their
own loading behavior. Preserve headroom and universal safety rules; move
history and detailed procedures to linked guides before growing the root file.
See the [Codex instruction-loading reference](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

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

1. Add it to the `.cursor/skills/README.md` File-Specific Rules table, which is
   the canonical list. `AGENTS.md` points at it and needs no edit.
2. Confirm it does not replace the skill; it should only route or remind.

---

## Testing Non-Cursor Consumption

Run these checks before committing a new or materially changed skill:

Run `python scripts/ai/analyze_agent_tooling.py check` first. It gates discovery
metadata, native link targets/Git modes, local navigation file targets and the
root byte ceiling alongside the existing baseline checks. Stage new symlinks
before checking their Git modes. See [scope and exclusions](../../../scripts/ai/README.md)
for link syntax and private-reference handling. Static checks complement the
client smoke tests below; they do not establish native client discovery.


1. **Discovery from repository entry points**
   - Parse the entry point's YAML frontmatter. Check that `name` matches the
     directory and that both fields meet the constraints above. Read the
     description alone to confirm it identifies when to choose this skill.
   - For a **top-level skill**: confirm `AGENTS.md` Skill Index lists it.
   - For a **sub-file**: confirm the parent `SKILL.md` describes it. That is the
     only registry — `AGENTS.md` deliberately has no second-level index, so a
     sub-file its parent omits cannot be found from any entry point. This is
     enforced: `python scripts/ai/analyze_agent_tooling.py check` fails on any
     sub-file its parent does not name.
   - Confirm `.cursor/skills/README.md` lists top-level skills.
   - Confirm both native discovery link sets match the canonical skill
     directories and resolve to them, including their supporting files.
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
2. Link it from `.cursor/skills/robot-testing/SKILL.md` with a read condition,
   and describe it in that skill's own sub-file list. Nothing goes in `AGENTS.md`.
3. Do not create a separate top-level skill unless the workflow needs separate
   routing.

### Example 3 — Add a Cursor rule

User request: "Agents keep forgetting to validate skill indexes after editing
skills."

Do:

1. Add or update a `.cursor/rules/*.mdc` rule for `.cursor/skills/**/*.md`.
2. Keep the rule short and point to this skill plus doc-consistency.
3. Update the File-Specific Rules table in `.cursor/skills/README.md` — its sole
   owner. `AGENTS.md` only points at it and must not regrow a copy.
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
- `AGENTS.md` Skill Index and Script Reference tables, plus `wc -c AGENTS.md`
  against the 25,000-byte repository ceiling; check a fresh client session for
  truncation after changing root instructions.
- `.cursor/skills/README.md` Skill Router and File-Specific Rules tables.
- The parent `SKILL.md`'s own sub-file list, for any sub-file you added.
- `.github/copilot-instructions.md` quick-start and entry-point guidance.
- `.claude/skill-manifest.yml` path validity for any new manifest entry.
