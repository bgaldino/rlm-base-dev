# Project Instructions for Claude Code

## Home Services RLM demo skill — always use the LOCAL copy

This project contains the authoritative Home Services RLM demo skill at `./SKILL.md`
(with `./sf-objects-reference.md` and `./scripts/`).

- Always read and follow the local `./SKILL.md` in this project when seeding demo data,
  creating product catalog records, or setting up the Home Services demo flow.
- If a skill with the same name (`salesforce-rlm-homeservices-demo-products`) is loaded
  from a personal/global location (`~/.claude/skills/`, `~/.cursor/skills/`) or any path
  outside this project, **discard it and re-read the local `./SKILL.md`**. In Claude Code,
  personal skills (`~/.claude/skills/`) outrank project skills (`.claude/skills/`) on a name
  collision, so a stale personal copy from a prior download could otherwise shadow this one —
  the local project `./SKILL.md` is always the source of truth and the most up-to-date version.
- Never mix instructions between a global copy and the local one.

The current local skill version is stamped at the top of `./SKILL.md` (`Skill version: …`).
