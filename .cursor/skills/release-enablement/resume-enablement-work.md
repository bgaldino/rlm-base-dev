# Resume Enablement Work — On Any Workstation

How a fresh AI agent (Claude, Cursor, Codex, any) restarts enablement-catalog work mid-stream. Read this when starting a new conversation in this repo without prior thread context.

This skill is the **cross-workstation handoff mechanism**. The repo is the source of truth — conversation threads don't need to sync as long as a fresh agent can re-orient quickly from committed state.

## When to use this skill

You're starting a new conversation and any of these are true:

- You see "rlm-base-dev" enablement files but no prior context about them
- The user says something like "continuing enablement work" / "pick up where we left off" / "resume on this workstation"
- You're on a different machine than the one where prior work happened
- You see references to "master exercises", "Infinitech scenario", or "two-tier model" without context

## The 4-step re-orientation

### 1. Confirm branch state

```bash
cd <repo-path>
git branch --show-current
git log --oneline -5
git status --short | head -20
```

Expected branch: typically a `feat/enablement-*` or `feat/skills-and-enablement-*` feature branch (initial 260-cycle authoring happened on `feat/enablement-260-master-exercises`; subsequent cycles use a `feat/...-to-{version}` branch). If on `main` or a release branch (`262`, `260`, …), check whether the user wants to switch — enablement work happens on a feature branch.

If you see commits with messages starting `feat(enablement):` or `docs(enablement):`, you're in the right place.

### 2. Read the orientation set (in order)

Read these three files end-to-end before doing anything else:

1. **[`docs/enablement/README.md`](../../../docs/enablement/README.md)** — the colleague-review entry point. Explains the two-tier model, workshop scenario, directory map, current draft status, open questions.
2. **[`SKILL.md`](SKILL.md)** (this skill's parent) — the workflow, source inventory, frontmatter schema, two-tier model rules.
3. **[`docs/enablement/master/qb-scenario-reference.md`](../../../docs/enablement/master/qb-scenario-reference.md)** — the canonical reference for what's in QB orgs by default. Every walkthrough anchors here.

Optional (read when you encounter the relevant edge case):

- **[`authoring-patterns.md`](authoring-patterns.md)** — 11 patterns for handling edge cases (upgrade guidance, known issues, sub-features, cross-area features, scenario threading, version-aware section metadata, license-scope split, etc.)
- **[`docs/salesforce/{260,262}/feature-index.md`](../../../docs/salesforce/260/feature-index.md)** — per-release feature inventories

### 3. Check what's drafted vs pending

```bash
ls docs/enablement/master/
ls docs/enablement/260/*.md
```

Cross-reference against [`docs/enablement/coverage-matrix.md`](../../../docs/enablement/coverage-matrix.md) and the status tables in `docs/enablement/README.md`.

Master exercise file naming: `{NN}-{area-kebab}.md` where `NN` is workshop sequence (01–10).

### 4. Summarize state to the user

Before taking any action, summarize what you understand:

- What branch you're on and how many commits ahead of `main`
- Which master exercises are drafted (with version numbers)
- Which per-release 260 drafts exist
- The 2–3 most prominent open questions from the README's "Open questions" section
- What you understand the workshop scenario to be (Infinitech anchor, QB-COMPLETE / QB-QRack-750 bundles)

Then ask the user what they'd like to do next. **Do not start authoring or editing files until the user confirms direction.**

## Common follow-up tasks (and where to start)

| User intent | Where to start |
|---|---|
| "Continue with the next master exercise" | Read the master pilot files (PCM + Pricing). Apply the same structure to the next area. Use Pattern 9 (Scenario Threading) and Pattern 10 (Version-Aware Section Metadata). |
| "Refine the pilots based on feedback" | Read the user's feedback. Update master files in place; bump `file_version` in frontmatter (0.1 → 0.2). |
| "Fill in `[NEEDS REVIEW]` items" | Search across `docs/enablement/master/` and `docs/enablement/260/` for `NEEDS REVIEW`. Each one has a context note explaining what's missing. |
| "Add a customer-template data plan" | See `docs/enablement/master/qb-scenario-reference.md` § Gaps + Recommendations. Builds a new `qb-customer/` plan or extends `scratch_data`. |
| "Generate per-release extracts from master" | The auto-gen render task isn't built yet. Manual extract is acceptable — see SKILL.md § Workflow B. |
| "Update the QB scenario reference" | Edit `docs/enablement/master/qb-scenario-reference.md`. If the change affects what master exercises reference, update those too. |

## Tool grants needed on a new workstation

| Capability | Why |
|---|---|
| **File system** for the repo | Always required |
| **Chrome MCP** | If you need to capture content from `help.salesforce.com` (the Help portal is a SPA — `WebFetch` won't work; only Chrome with a recursive shadow-DOM walker) |
| **Bash / shell** | For `git`, `pdftotext` extraction from master Help PDFs, etc. |
| **Web tools** (WebSearch, WebFetch) | For finding URLs and lightly-trafficked pages; the SPA Help portal needs Chrome |

The user may need to re-grant these on the new workstation. If you don't have a tool you expect, ask the user before assuming the tool is unavailable.

## Critical do-nots when picking up

1. **DO NOT push to `main` directly.** Enablement work always uses a feature branch. Per `AGENTS.md`: never `git push origin main` or force-push main without explicit user approval.
2. **DO NOT amend or rewrite commits that have been pushed.** If the feature branch has been pushed (`git log @{upstream}` shows commits), amending changes the SHA and breaks anyone tracking the branch. New commits only.
3. **DO NOT assume the user uploaded source PDFs (Solution Overview decks, master Help PDF) on this workstation.** Those are CONFIDENTIAL or 130 MB — typically NOT in the repo. The captured markdown summaries in `docs/salesforce/{version}/feature-index.md` are usually sufficient for authoring; only ask for re-uploads if you genuinely need a section that wasn't captured.
4. **DO NOT invent customer or product names.** Customers come from `scratch_data` (Infinitech, Global Media). Partners from `qb-prm` (Robot Resellers). Bundles + products from `qb-pcm`. Constraint models from `qb-constraints` (QuantumBitComplete, Server2). See QB Scenario Reference for the canonical list.
5. **DO NOT skip reading `qb-scenario-reference.md`.** Even if the user is in a hurry. It's the foundation. Bad walkthroughs come from skipping this step.

## The orientation prompt template

For users who want to give a fresh Claude (or other agent) a single concise restart prompt:

> *I'm continuing enablement work on `rlm-base-dev`. Read these in order: (1) `docs/enablement/README.md` (colleague-review entry point), (2) `.cursor/skills/release-enablement/SKILL.md` (workflow + two-tier model), (3) `docs/enablement/master/qb-scenario-reference.md` (canonical QB reference). Then run `git log --oneline -5` and summarize: current branch, commits ahead of main, master files drafted with version numbers, per-release drafts present, top 2–3 open questions. Don't start editing files until I confirm the next step.*

This prompt + the four-step re-orientation above get a fresh agent to fully oriented in 5–10 minutes.

## Why repo-based handoff (not conversation sync)

The Claude desktop "Cowork mode" is a research preview; conversation sync semantics across workstations are not guaranteed and may change. **Don't rely on conversation thread continuity for project handoff.**

The repo is the synchronization mechanism that's reliable today:

- Any agent on any workstation that clones the repo gets the same starting context
- Skills + scenario reference + drafts all travel together
- Cross-workstation handoff matches the established personal vs Salesforce workstation model

This file ensures that pattern stays explicit. If you find yourself re-explaining state in every new conversation, update this skill (or `docs/enablement/README.md`) — make the next handoff faster.

## Change log

- **2026-05-06** — Initial sub-file created from cross-workstation handoff conversation. Captures the 4-step re-orientation, common follow-up task table, tool grants checklist, do-nots, and the standard restart prompt template.
