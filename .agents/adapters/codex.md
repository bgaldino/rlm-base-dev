# Codex Adapter

Codex should treat the repo-root `AGENTS.md` file as the canonical safety and
project contract for every task in this repository.

## Instruction mapping

- **Primary instructions:** read and obey `AGENTS.md` first.
- **Task-specific skills:** use the Skill Index in `AGENTS.md` to select and read
  the relevant `.cursor/skills/**` Markdown files. These files are tool-neutral
  despite the historical Cursor path.
- **File-specific guidance:** when editing file types covered by
  `.cursor/rules/*.mdc`, read the matching rule file as reusable guidance.
- **Cross-repo discovery:** use `.claude/skill-manifest.yml` and
  `scripts/ai/skill_manifest.py` when a task needs PMOS/Foundation skill or
  artifact resolution.

## Authoritative files

1. `AGENTS.md`
2. Relevant `.cursor/skills/**` files
3. Relevant `.cursor/rules/*.mdc` files
4. `.claude/skill-manifest.yml` for cross-repo skill resolution

This adapter is only a routing note; it does not override `AGENTS.md`.
