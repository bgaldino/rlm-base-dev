# Use the skills in your coding agent

Clone the **full repository**, preserve symbolic links, and open the repository
root in your agent. Skills use the scripts, data, documentation, and safety
rules shipped alongside them; copying an individual skill folder is not a
standalone installation.

## Shared content and discovery paths

| Path | Role |
|------|------|
| `.cursor/skills/<name>/` | Canonical skill content; edit here |
| `.agents/skills/<name>` | Relative directory link to the canonical skill for Codex and compatible clients |
| `.claude/skills/<name>` | Relative directory link to the same skill for Claude Code and compatible clients |

Each link targets `../../.cursor/skills/<name>`, so the entry point and its
supporting files stay together. There is one content copy. Read
[`AGENTS.md`](../../AGENTS.md) for repository-wide rules before using a skill.
The cross-repository manifest in `.claude/skill-manifest.yml` is separate from
these native discovery paths.

## Try discovery

Start a new session after cloning or updating the repository. Use the client's
skill picker to find `odt-authoring`, then try this read-only prompt:

```text
Use the odt-authoring skill to explain whether ODT field paths use dots or
colons, and which skill handles .docx templates. Do not change files or an org.
```

In Codex CLI, select the skill with `$odt-authoring` or `/skills`. In Claude
Code, invoke `/odt-authoring`. A successful answer identifies colon-separated
ODT paths and routes template work to `document-generation`.

### Verification coverage

The following checks were run on macOS for this adapter change:

| Client | Result |
|--------|--------|
| Codex CLI `0.154.0-alpha.6.2` | Native inventory found all 32 repository skills once each; explicit `$odt-authoring` invocation passed |
| Claude Code `2.1.69` | Native inventory found all 32 repository skills once each; explicit `/odt-authoring` invocation passed |
| Cursor Agent CLI `2026.05.01-eea359f` | Invocation could not run without authentication; discovery and duplicate handling remain unverified |
| GitHub Copilot | No local client test; native discovery and duplicate handling remain unverified |

These results cover discovery and one read-only invocation, not every workflow
or client version. Keep the catalog fallback below available.

Official references describe the respective discovery locations:
[Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills),
[Cursor](https://cursor.com/docs/skills), and
[Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills).
Some clients scan several compatible roots. If a client shows duplicate names,
they may point to the same canonical content; use the catalog path to select
the intended skill. Avoid installing another personal copy of this library
unless you deliberately want it available across repositories.

## Windows, downloads, and missing skills

Git must check out the adapters as symbolic links. Some Windows environments
and archive extraction tools instead produce small text files containing the
link target. Those files do not provide native discovery. Windows symlink
checkout requires OS support/permission as well as Git's `core.symlinks`
setting; changing the setting alone does not repair an existing checkout.
Use a fresh clone in a symlink-capable environment (such as WSL), or use the
fallback below. Windows and archive extraction have not been client-tested.

From the repository root, verify the shape of one link:

```sh
ls -ld .agents/skills/odt-authoring .claude/skills/odt-authoring
```

Both should be directory links to `../../.cursor/skills/odt-authoring`, and
`SKILL.md` should be readable through either path. If the client still omits
the skill, restart its session and check its project-skill settings. In
Claude Code, excluding `project` from `--setting-sources` also excludes these
project skills in the tested version.

### Catalog fallback — works without native discovery

Give any agent with repository-file access this prompt:

```text
Read AGENTS.md and .cursor/skills/README.md. Select and read the relevant
.cursor/skills/<name>/SKILL.md and its linked references before answering
my task. Follow the repository's validation and approval requirements.
```

The [skill catalog](../../.cursor/skills/README.md) and canonical files remain
usable when links are unavailable. Private maintainer artifacts are not
required to browse the public skills; workflows such as the private todo
tracker have their own access requirements.
