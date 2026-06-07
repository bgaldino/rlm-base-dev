# Agentforce Adapter

Agentforce should use this repository's shared files as its source of
instructions instead of introducing a parallel guidance stack.

## Instruction mapping

- **Primary instructions:** read repo-root `AGENTS.md` first and treat it as the
  canonical safety and project contract.
- **Task-specific skills:** use `AGENTS.md` to select relevant
  `.cursor/skills/**` Markdown files. The skills are tool-neutral and are not
  limited to Cursor.
- **File-specific guidance:** read applicable `.cursor/rules/*.mdc` files for
  reusable file-pattern guidance, while recognizing that Cursor-specific
  auto-injection does not apply to Agentforce.
- **Cross-repo discovery:** use `.claude/skill-manifest.yml` to understand which
  skills and grounding artifacts are shared across repos.
- **Copilot pointer:** `.github/copilot-instructions.md` is specific to GitHub
  Copilot and should be treated as an adapter, not as a separate authority.

## Authoritative files

1. `AGENTS.md`
2. Relevant `.cursor/skills/**` files
3. Relevant `.cursor/rules/*.mdc` files
4. `.claude/skill-manifest.yml` for cross-repo skill resolution

This adapter is only a routing note; it does not override `AGENTS.md`.
