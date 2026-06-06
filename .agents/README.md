# Agent Instruction Stack

This repository uses a layered instruction stack so every AI coding tool can
start from the same project contract and then opt into more specific guidance.
The path names reflect the tools that introduced each file, but most of the
content is intentionally reusable across agents.

## Canonical stack

1. **`AGENTS.md` — root safety and project contract**
   - Authoritative for repository-wide safety rules, project context, common
     workflows, pre-merge checks, and the skill index.
   - Every tool should read this file first and treat it as the top-level source
     of truth unless a direct human instruction overrides it.
   - Tool-specific entry points (`CLAUDE.md`, `.github/copilot-instructions.md`)
     are symlinks or pointers to this file — edit `AGENTS.md` only.

2. **`.cursor/skills/` — tool-neutral skill markdown**
   - Contains detailed task guides such as CCI orchestration, SFDMU data plans,
     Robot testing, UX assembly (under `repo-integration`), schema validation,
     and release enablement.
   - Despite the historical `.cursor` path, these are plain Markdown skills for
     any agent that can read repository files.
   - Use the Skill Index in `AGENTS.md` or `.cursor/skills/README.md` to choose
     the relevant entry point.

3. **`.cursor/rules/` — Cursor-specific rule files with reusable guidance**
   - Contains `.mdc` files that Cursor can auto-inject based on edited file
     patterns.
   - Non-Cursor tools can still read these files manually when working on the
     same file types; the guidance is reusable, but the auto-injection mechanism
     is Cursor-specific.

4. **`.claude/skill-manifest.yml` — cross-repo skill manifest**
   - Advertises Foundations skills, grounding artifacts, and cross-repo paths so
     agents can resolve shared guidance between this repo and related repos such
     as PMOS.
   - Use it with `scripts/ai/skill_manifest.py` when cross-repo discovery or
     validation is needed.

5. **`.github/copilot-instructions.md` — Copilot pointer**
   - Directs GitHub Copilot to `AGENTS.md` and summarizes the shared entry
     points.
   - It is an adapter for Copilot, not a replacement for the root contract.

## Authority order

1. Direct human/system instructions for the current task.
2. `AGENTS.md` for repository-wide policy and safety.
3. Relevant skill files under `.cursor/skills/` for task-specific workflows.
4. Relevant `.cursor/rules/` files for file-pattern-specific guidance.
5. Tool adapter files, including `.github/copilot-instructions.md` and the files
   in `.agents/adapters/`, for mapping a tool to the shared instruction stack.

If guidance appears to conflict, prefer the higher-authority source and document
any important assumption in your response or PR notes.

## Tool adapters

Short adapter notes live in `.agents/adapters/`:

- `codex.md`
- `claude-code.md`
- `cursor.md`
- `copilot.md`
- `agentforce.md`

Each adapter explains how that tool should map its native instruction mechanism
to the repository's existing files and which files are authoritative.

## Other `.agents/` files

The `.agents/` tree also holds supporting context for agents (added alongside
this README):

- `.agents/model-routing.md` — maps work types to model/execution modes and
  defines escalation criteria.
- `.agents/context/project-map.md` — human-readable map of the repository.
- `.agents/context/project-memory.json` — machine-readable project memory,
  validated against `.agents/schemas/project-memory.schema.json`.

None of these override `AGENTS.md`; they are routing and context aids.
