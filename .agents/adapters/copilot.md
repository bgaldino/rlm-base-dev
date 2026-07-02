# GitHub Copilot Adapter

GitHub Copilot should enter the shared instruction stack through the repository's
Copilot instruction file.

## Instruction mapping

- **Copilot entry point:** `.github/copilot-instructions.md` points Copilot to
  `AGENTS.md` and summarizes the common entry points.
- **Primary instructions:** `AGENTS.md` is the canonical safety and project
  contract.
- **Task-specific skills:** use the Skill Index in `AGENTS.md` to read relevant
  `.cursor/skills/**` Markdown files. These are tool-neutral.
- **File-specific guidance:** `.cursor/rules/*.mdc` files are Cursor-specific for
  injection, but Copilot can reuse their guidance manually.
- **Cross-repo discovery:** `.claude/skill-manifest.yml` supports cross-repo
  skill and artifact resolution.
- **Automated PR reviews:** drive review threads to **zero unresolved** using
  `python scripts/ai/pr_review.py` (`status` / `handle` / `verify`), per
  `AGENTS.md` §"Responding to Automated PR Reviews".

## Authoritative files

1. `AGENTS.md`
2. `.github/copilot-instructions.md` as Copilot's adapter pointer
3. Relevant `.cursor/skills/**` files
4. Relevant `.cursor/rules/*.mdc` files
5. `.claude/skill-manifest.yml` for cross-repo skill resolution

The Copilot instruction file is an entry point; it does not replace `AGENTS.md`.
