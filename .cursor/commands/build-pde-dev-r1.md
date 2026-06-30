---
description: Build a Partner Development Environment (PDE) org from the tfid-pde shape into a fresh pde<datetime> alias, with runtime-only flags pde=true, billing_ui=false (reverted after build)
---

# Build PDE org (tfid-pde shape → pde<datetime> alias)

Build a **Partner Development Environment** using the `tfid-pde` scratch
**shape**, provisioned into a **fresh, uniquely-aliased** scratch org
(`pde<datetimestamp><pid>`, e.g. `pde2026063018172578357`), with two **runtime-only**
CumulusCI feature-flag overrides:

| Flag         | On `main` | This build | Effect |
|--------------|-----------|------------|--------|
| `pde`        | `false`   | **`true`** | Marks the org-type as PDE (declared flag; no `when:` gate today) |
| `billing_ui` | `true`    | **`false`**| Skips Billing UI LWC steps (`deploy_post_billing_ui` and 3 related `when:` steps) |

**Every other feature flag stays exactly as committed on the current branch.**
The edits to `cumulusci.yml` are temporary: the file is backed up before the
build and restored on exit (success, failure, or interrupt), so **nothing is
ever staged or committed** as a result of this build.

The build always targets a **new** scratch org alias so scheduled runs never
collide or reuse a prior org. The alias is derived as `pde$(date +%Y%m%d%H%M%S)$$`
(timestamp + PID, so two builds in the same second still differ) and registered
from the `tfid-pde` shape via `cci org scratch tfid-pde <alias>`. If the resolved
alias already exists (e.g. a pinned `ORG=`), the script **fails fast** rather than
reusing a stale or partially-built org.

## How to run it

Run the dedicated, self-reverting build script from the repo root:

```bash
scripts/build_pde_dev_r1.sh
```

To pin a specific alias instead of the auto-generated one:

```bash
ORG=pde-demo scripts/build_pde_dev_r1.sh
```

The script:

1. Requires `unpackaged/post_ux/` and `datasets/sfdmu/` to be **clean** before
   starting (the build regenerates and then reverts them, so a pre-existing
   local edit there would be clobbered) — aborts with guidance if they're dirty.
   Skip this with `CLEAN_BUILD_ARTIFACTS=false`.
2. Backs up `cumulusci.yml`, then sets `pde: true` and `billing_ui: false`
   (aborting if either flag isn't matched exactly once).
3. Generates a unique alias `pde<datetime><pid>` (override with `ORG=`) and
   registers it from the `tfid-pde` shape: `cci org scratch tfid-pde <alias>`.
   **Fails fast** if that alias already exists (no silent reuse).
4. Runs `cci flow run prepare_rlm_org --org <alias>` (CCI creates the actual
   scratch org on first use).
5. Restores the original `cumulusci.yml` **and** reverts all churn the build
   regenerated under `unpackaged/post_ux/` and `datasets/sfdmu/` (UX assembly
   output, SFDMU `export.json` writeback — tracked edits via `git checkout`,
   build-created files via `git clean`) via an `EXIT` trap in all cases —
   leaving the working tree clean.

Overridable environment variables:

| Var    | Default                     | Purpose |
|--------|-----------------------------|---------|
| `ORG`  | `pde$(date +%Y%m%d%H%M%S)$$` | Scratch-org alias to create/build (must be unused — fails fast if it exists) |
| `SHAPE`| `tfid-pde`                  | Scratch shape (config under `orgs.scratch`) to base the alias on |
| `FLOW` | `prepare_rlm_org`           | CCI flow to run |
| `CLEAN_BUILD_ARTIFACTS` | `true`         | Require `unpackaged/post_ux/` and `datasets/sfdmu/` to be clean before the build, then revert all churn there afterward so the branch stays clean. Set `false` to skip both the pre-check and the cleanup and manage those paths yourself |

## Agent responsibilities

When you (the agent) run this command:

1. From the repo root, execute `scripts/build_pde_dev_r1.sh`.
2. Stream/inspect the CCI output. If the build fails, surface the failing step
   and consult `.cursor/skills/troubleshooting/SKILL.md`. Do **not** re-commit
   or "fix" `cumulusci.yml` — the override is intentional and is auto-reverted.
3. After the run, confirm `git status` shows **no** modification to
   `cumulusci.yml` (the trap should have restored it). If it somehow remained
   modified, restore it with `git checkout -- cumulusci.yml` and report this.
4. Report the generated alias, the flow result, and the SF CLI alias
   (`rlm-base__<alias>`) for opening the org.

## Converting to a Cloud Agent (scheduled runs)

This file is self-contained on purpose. To run on a schedule, create a Cursor
Cloud Agent whose prompt is: *"Run the `build-pde-dev-r1` command in this repo"*
(or paste this file's body). Each run provisions a fresh `pde<datetime>` org, so
scheduled builds never collide and the branch is never mutated.

When automating, **poll for completion** rather than assuming success: the build
takes tens of minutes, and any follow-up action (e.g. opening a PR, notifying)
must be gated on the flow's exit status (`0` = success).

## Notes / guardrails

- Do not change `pde`/`billing_ui` defaults in `cumulusci.yml` on `main` —
  this build adjusts them only at runtime.
- `pde` is currently a declared flag with no `when:` gate in `cumulusci.yml`;
  setting it is correct for org-type intent but has no build-time effect on its
  own today. `billing_ui: false` is what materially changes this build.
- Scheduled runs accumulate scratch-org config entries (one per `pde<datetime>`
  alias). The underlying scratch orgs expire on their own (30 days); prune stale
  aliases with `cci org scratch_delete <alias>` if needed.
- Per `AGENTS.md`, never push directly to `main`; this command does not commit
  anything.
