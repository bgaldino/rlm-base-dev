# Cursor Adapter

Cursor has native support for both the historical skill directory and
file-pattern rule files in this repository.

## Instruction mapping

- **Primary instructions:** read and obey repo-root `AGENTS.md` as the canonical
  safety and project contract.
- **Task-specific skills:** use `.cursor/skills/**` as plain Markdown skill
  files. They are reusable by all tools even though Cursor can navigate them
  directly.
- **File-specific guidance:** `.cursor/rules/*.mdc` files are Cursor-specific
  auto-injection rules for matching file patterns.
- **Cross-repo discovery:** use `.claude/skill-manifest.yml` and
  `scripts/ai/skill_manifest.py` when resolving cross-repo skills or grounding
  artifacts.
- **Automated PR reviews:** drive review threads to **zero unresolved** using
  `python scripts/ai/pr_review.py` (`status` / `handle` / `verify`), per
  `AGENTS.md` §"Responding to Automated PR Reviews".

## Authoritative files

1. `AGENTS.md`
2. Relevant `.cursor/skills/**` files
3. Relevant `.cursor/rules/*.mdc` files
4. `.claude/skill-manifest.yml` for cross-repo skill resolution

Cursor rule auto-injection adds convenience, but it does not make `.cursor/rules/`
more authoritative than `AGENTS.md`.
