# Todo Tracker — Durable Work Items Across Workstations and Agents

Open work for this repository lives as **context packs** in the private
`rlm-base-artifacts` repo, cloned to `.agents/artifacts/`. A pack holds everything
needed to start an item cold: what done looks like, facts already established (with
dates and evidence), approaches already tried and rejected, and how to verify.

Use this skill when picking up work, claiming an item, or closing one out — and
especially when starting a session in this repo with no idea what is in flight.

## Quick Rules

1. **Read the index before starting anything.** `/rlm-todos list`, or
   `python .agents/artifacts/todos/index.py list`.
2. **Claim before you work, and let the claim push.** The push *is* the claim — it is
   what makes a simultaneous start collide instead of silently duplicating a day.
3. **Never hand-edit frontmatter.** Use `index.py claim|release|close`; it stamps,
   validates, commits and pushes as one step.
4. **Release when you stop, not only when you finish.** A claim left on a paused item is
   the main way this tracker rots.
5. **Close on acceptance, not on merge.** If the criteria are met and verified, close it
   and say in the Outcome that it is unmerged.
6. **A session task list is never the record.** Claude Code's task tool, a scratch file,
   a TODO comment — none of these outlive the session. The pack does.

## DO NOT

- **DO NOT** put private detail in a GitHub issue. `bgaldino/rlm-base-dev` is **public**:
  no org aliases, no instance URLs, no unreleased-release detail, no retracted-conclusion
  investigations. The issue is a public-safe pointer; the pack is the payload.
- **DO NOT** claim as an agent. `claimed_by` names a **person** — an agent acts on
  someone's behalf, and a tracker full of `claude` cannot tell you whose machine holds
  the uncommitted work.
- **DO NOT** take over a claim silently. A claim older than 14 days with no commits
  referencing the item is presumed abandoned — clear it **and write in the pack's log
  that you did**.
- **DO NOT** widen a pack's scope to keep it open. Partially done is not done: split the
  remainder into a new pack and close the original against what it delivered.
- **DO NOT** write a bare `#NN` for a pack id in a commit message or PR body. GitHub
  autolinks it to an unrelated issue. Write "todo 71" unlinked, or use the pack's real
  `github_issue` number.
- **DO NOT** allocate a pack id from a stale `ls`. There is no allocator — you take the
  next number after the highest across `open/` **and** `done/`, so pull first. Two
  workstations both created a pack 119 three hours apart on 2026-08-14 doing exactly this.
  `--check` now fails on a duplicate and `claim`/`close` refuse an ambiguous id, but the
  collision itself is still yours to avoid.

## Entry Conditions

- Starting a session and needing to know what is in flight or already claimed.
- Picking up work described only as "the next thing" — the index is the answer.
- Finishing an item, which is not finished until it is closed out here.
- Finding work worth doing that is bigger than the current task — write a pack rather
  than leaving it in a session list that dies with the session.

## First run on a workstation

If `.agents/artifacts/` is empty, nothing above will work — clone it:

```bash
git clone https://github.com/bgaldino/rlm-base-artifacts.git .agents/artifacts
```

Access is limited. If the clone fails, say so plainly and continue without the tracker
rather than inventing what might be in it.

## Commands

`/rlm-todos <subcommand>` in this repo, or the tool directly:

| Command | Does |
|---|---|
| `index.py list [--status open]` | Every pack, with claim age, blockers and bundle |
| `index.py show <id>` | The full pack — read this before working, not just the title |
| `index.py claim <id>` | Pull, stamp, commit, **push**. Refuses an already-claimed pack |
| `index.py release <id>` | Clear the claim and reopen |
| `index.py close <id>` | Stamp, clear claim, `git mv` to `done/`, reindex, validate, push |
| `index.py --check` | Validate every pack; exit 1 on a closeout violation or stale index |

`claim` and `close` take `--no-push` for offline work. It prints a warning, because an
unpushed claim protects nobody.

## Sequencing — two different relationships

Both live in frontmatter; the **rationale goes in the body**, because a bare dependency
with no reason gets ignored the moment it is inconvenient.

- **`blocked_by` / `blocks`** — a hard ordering. B cannot start, or cannot be trusted,
  until A is done.
- **`bundle`** — no ordering, but doing them together is much cheaper: same files, same
  review round, or the same finding class where fixing one and not the others leaves a
  half-swept class an audit will re-raise.

Prefer an item from a bundle you are already inside over an unrelated one of nominally
higher value.

## Writing a pack

Four sections, in this order. The middle two are the whole point — they are what stops a
fresh agent on another machine re-deriving work already paid for.

1. **What and why** — the goal, and what "done" looks like.
2. **Already established** — facts with **evidence and a date**: measured how, in which
   org, when. A fact with no date cannot be judged for staleness.
3. **Do not redo** — approaches tried and rejected, with the reason. Wrong turns are as
   valuable as findings.
4. **How to verify** — the check that proves it is actually done.

At closeout, *What and why* becomes **Outcome**. `close` enforces that.

## Examples

**Starting a session cold**

```bash
python .agents/artifacts/todos/index.py list --status open
python .agents/artifacts/todos/index.py show 071      # read the whole pack
python .agents/artifacts/todos/index.py claim 071     # pushes immediately
```

**Someone else got there first.** `claim` exits non-zero with who holds it and since
when, or the push is rejected. Either way: pull, re-read, pick something else. Do not
work a claimed item in parallel.

**Finishing.** Rewrite the body into an Outcome first, then `close 071`. If it refuses,
it is telling you step 3 has not been done — that is the check working.

## Validation Checks

- `python .agents/artifacts/todos/index.py --check` reports **0 problems** and a current
  index. Run it before ending a session. Expect the "INDEX.md is stale" line roughly daily
  even when nothing changed — the index embeds computed claim ages, so time alone stales
  it. Read the message anyway; a real closeout violation arrives by the same channel.
- A pack you closed is in `done/`, has `status: done`, a `closed_at`, and no claim.
- A pack you claimed shows your name on the remote, not just locally.
- Nothing you intend to survive this session exists only in a session task list.

## Related

- `.agents/artifacts/todos/README.md` — the canonical protocol, including stale-claim
  handling and the public-vs-private split. This skill is the agent-facing entry point;
  that file is the specification.
- `.agents/README.md` — the instruction stack, and the clone pointer.
