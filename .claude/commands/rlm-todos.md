---
description: List, claim, release or close a durable todo pack in the artifacts tracker
argument-hint: list | show <id> | claim <id> | release <id> | close <id>
---

Operate the durable todo tracker, following `.cursor/skills/todo-tracker/SKILL.md`.

Requested: **$ARGUMENTS**

The tool is `python .agents/artifacts/todos/index.py`. It does the stamping, git
`mv`, index regeneration, validation, commit and push — **do not hand-edit pack
frontmatter.** If `.agents/artifacts/` is missing, the tracker is not cloned on this
workstation; see the skill's *First run* section and stop rather than guessing at
what the tracker holds.

Map the argument to a subcommand:

- **`list`** (or no argument) — `index.py list`. Report open items with claim age,
  blockers and bundles. Flag anything showing **⚠ STALE**.
- **`show <id>`** — `index.py show <id>`. Read the **whole** pack, not just the
  title: *Already established* and *Do not redo* are what stop you re-deriving work
  already paid for.
- **`claim <id>`** — `index.py claim <id>`. It pulls, stamps and **pushes**; the push
  is what makes a simultaneous claim collide instead of duplicating a day of work.
  If it refuses or the push is rejected, someone else holds it — pull, re-read, pick
  something else. Never work a claimed item in parallel.
- **`release <id>`** — `index.py release <id>`. Do this whenever you stop, not only
  when you finish.
- **`close <id>`** — **rewrite the body first**: replace *What and why* with an
  **Outcome** (what was delivered and where), keep *Already established*, and add
  durable findings plus any follow-on work split out. Then `index.py close <id>`. It
  refuses a pack with no `## Outcome` section — that refusal means the rewrite has
  not been done, so do it rather than passing `--force`. Close on **acceptance, not
  merge**. If the pack names a `github_issue`, close that too, citing the PR or commit.

Two rules worth repeating because breaking them is silent:

- `claimed_by` is a **person**, never an agent.
- `bgaldino/rlm-base-dev` is **public**. Anything going into a GitHub issue must
  carry no org aliases, instance URLs, or unreleased-release detail — the issue is a
  public-safe pointer, the pack is the payload.

Finish by running `python .agents/artifacts/todos/index.py --check`; it must report
0 problems and a current index.
