# Claude Code Adapter

Claude Code should use the repository's shared instruction stack rather than a
separate Claude-only contract.

## Instruction mapping

- **Primary instructions:** `CLAUDE.md` is a symlink to `AGENTS.md`;
  `AGENTS.md` is the authoritative root contract — edit only `AGENTS.md`.
- **Task-specific skills:** read the applicable `.cursor/skills/**` Markdown
  files from the Skill Index in `AGENTS.md`. The skills are tool-neutral.
- **File-specific guidance:** `.cursor/rules/*.mdc` files are Cursor auto-rules,
  but Claude Code can reuse their guidance manually for matching file types.
- **Cross-repo discovery:** `.claude/skill-manifest.yml` is the manifest for
  resolving shared skills and artifacts across Foundations and related repos.

## Authoritative files

1. `AGENTS.md` (authoritative); `CLAUDE.md` is the symlink entry point for Claude Code
2. Relevant `.cursor/skills/**` files
3. Relevant `.cursor/rules/*.mdc` files
4. `.claude/skill-manifest.yml` for cross-repo skill resolution

This adapter is only a routing note; it does not override `AGENTS.md`.
