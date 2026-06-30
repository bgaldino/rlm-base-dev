# PDE Org Build — Runtime Flag Overrides + Self-Reverting Build

Use this skill when building a **Partner Development Environment (PDE)** org —
or any org type that needs **temporary, build-only feature-flag changes** — for
Revenue Cloud Foundations. The actual work lives in a script and a command; this
skill is the *when/why* and routes to them. It is consumable by any agent
(Cursor, Claude Code, Codex, Copilot, etc.).

**Source of truth (do not duplicate their logic here):**

- Script: `scripts/build_pde_dev_r1.sh`
- Command / Cloud-Agent prompt: `.cursor/commands/build-pde-dev-r1.md`

## Quick Rules

1. Build a PDE org with `scripts/build_pde_dev_r1.sh`. It provisions a fresh
   `pde<datetimestamp><pid>` scratch org from the `tfid-pde` shape (failing fast
   if that alias already exists), applies runtime-only flags `pde=true` +
   `billing_ui=false`, runs `prepare_rlm_org`, then reverts every file it
   touched on exit.
2. Feature-flag overrides are **runtime only** — they exist in `cumulusci.yml`
   for the duration of the build and are restored on exit (success, failure, or
   interrupt). Never commit `pde`/`billing_ui` flips to `main`.
3. Override behavior via env: `ORG=<alias>`, `SHAPE=<scratch shape>`,
   `FLOW=<flow>`, `CLEAN_BUILD_ARTIFACTS=false` (see the command doc for the
   full table).
4. Gate any follow-up (open a PR, notify, chain a schedule) on the script's
   **exit code** (`0` = success), **not** the visible log tail — the captured
   terminal log caps around ~1 MB and appears to freeze mid-build while the
   build keeps running. The authoritative signal is the exit code / footer.
5. The build regenerates files under `unpackaged/post_ux/` (UX assembly) and
   `datasets/sfdmu/` (`export.json` writeback). The script **requires those paths
   to be clean before it runs** (so it never clobbers a pre-existing local edit)
   and reverts all churn there — tracked and build-created — on exit. Verify with
   `git status` afterward. Use `CLEAN_BUILD_ARTIFACTS=false` to skip both.
6. The target scratch shape must be registered in `cumulusci.yml` under
   `orgs.scratch` **and committed on the branch** — otherwise a fresh/cloud
   checkout's `cci org scratch <shape> <alias>` will fail.
7. To schedule: convert `.cursor/commands/build-pde-dev-r1.md` into a Cursor
   Cloud Agent. Each run provisions a unique alias, so runs never collide.

## DO NOT

- **DO NOT** commit the runtime `cumulusci.yml` flag overrides, or the
  `post_ux`/`datasets` churn the build produces. (The EXIT trap handles this;
  confirm with `git status`.)
- **DO NOT** treat the streamed/visible log tail as "done" — use the exit code.
- **DO NOT** point a scheduled/cloud build at an unregistered or uncommitted
  scratch shape.
- **DO NOT** hand-edit `unpackaged/post_ux/` to "fix" build output — it is
  generated (see `repo-integration/ux-assembly-retrieve.md`).
- **DO NOT** change `pde`/`billing_ui` defaults in committed `cumulusci.yml`.

## Entry Conditions

| Task | Use this skill? | Notes |
|------|-----------------|-------|
| Build a PDE org (manual or scheduled) | Yes | Default path. |
| Build another org type with temporary build-only flags | Yes | Adapt `SHAPE`/flags via env, or fork the script. |
| General CCI tasks / flows / flag semantics | No | Use `cci-orchestration/SKILL.md`. |
| Profile `prepare_rlm_org` across scenarios | No | Use `build-harness/SKILL.md`. |
| Debug a failed build step | Pair | Use with `troubleshooting/SKILL.md`. |

## How It Works

The script (see source for exact logic):

1. Requires `unpackaged/post_ux/` and `datasets/sfdmu/` to be clean before
   starting (aborts otherwise; skip with `CLEAN_BUILD_ARTIFACTS=false`).
2. Backs up `cumulusci.yml`, then sets `pde: true` and `billing_ui: false`
   (aborting unless each flag matches exactly once at the `project.custom` level).
3. Registers a fresh, uniquely-aliased scratch org from the configured shape:
   `cci org scratch <SHAPE> pde<datetime><pid>` — **failing fast** if that alias
   already exists rather than reusing a stale org.
4. Runs `cci flow run prepare_rlm_org --org pde<datetime><pid>`.
5. On exit, an EXIT trap restores `cumulusci.yml` **and** reverts all build
   churn under `unpackaged/post_ux/` and `datasets/sfdmu/` (tracked edits via
   `git checkout`, build-created files via `git clean`) — safe because those
   paths were verified clean at the start.

### Shape choice: `tfid-pde` vs `dev-r1`

PDE has two baseline paths (see `orgs/tfid/README.md`):

- `tfid-pde` — a **Trialforce-snapshot** shape (`orgs/tfid/tfid-pde.json`). The
  current default.
- `dev-r1` — a **standard Developer-Edition scratch** config
  (`orgs/internal/dev-r1.json`). Use `SHAPE=dev-r1` to build from a vanilla DE
  scratch instead of a Trialforce snapshot.

## Examples

```bash
# Default PDE build (tfid-pde shape, auto pde<datetime><pid> alias)
scripts/build_pde_dev_r1.sh

# Pin a specific alias (must not already exist — the script fails fast if it does)
ORG=pde-demo scripts/build_pde_dev_r1.sh

# Build from the standard DE scratch shape instead of the TFID snapshot
SHAPE=dev-r1 scripts/build_pde_dev_r1.sh

# Keep build-generated post_ux/datasets churn for inspection (opt out of cleanup)
CLEAN_BUILD_ARTIFACTS=false scripts/build_pde_dev_r1.sh
```

## Validation Checks

```bash
# Script is syntactically valid
bash -n scripts/build_pde_dev_r1.sh

# Target shape is registered (and must also be committed for cloud runs)
grep -A2 '^    tfid-pde:' cumulusci.yml

# After a build, the working tree must be clean of build churn
git status --porcelain -- cumulusci.yml unpackaged/post_ux datasets/sfdmu
```

- Build success = script exit code `0` (and `exit_code: 0` in the terminal-log
  footer) — not the visible log tail.
- Before a scheduled/cloud run, confirm the shape registration is committed on
  the branch, not just present in the local working tree.
