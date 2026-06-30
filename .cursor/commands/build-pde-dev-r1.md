---
description: Build a Partner Development Environment (PDE) org on scratch def dev-r1 with runtime-only flags pde=true, billing_ui=false (reverted after build)
---

# Build PDE org (dev-r1)

Build a **Partner Development Environment** using the `dev-r1` scratch
definition, with two **runtime-only** CumulusCI feature-flag overrides:

| Flag         | On `main` | This build | Effect |
|--------------|-----------|------------|--------|
| `pde`        | `false`   | **`true`** | Marks the org-type as PDE (declared flag; no `when:` gate today) |
| `billing_ui` | `true`    | **`false`**| Skips Billing UI LWC steps (`deploy_post_billing_ui` and 3 related `when:` steps) |

**Every other feature flag stays exactly as committed on the current branch.**
The edits to `cumulusci.yml` are temporary: the file is backed up before the
build and restored on exit (success, failure, or interrupt), so **nothing is
ever staged or committed** as a result of this build.

## How to run it

Run the dedicated, self-reverting build script from the repo root:

```bash
scripts/build_pde_dev_r1.sh
```

For a fresh scratch org each run (e.g. on a schedule), delete-and-recreate first:

```bash
RECREATE_ORG=true scripts/build_pde_dev_r1.sh
```

The script:

1. Backs up `cumulusci.yml`, then sets `pde: true` and `billing_ui: false`
   (aborting if either flag isn't matched exactly once).
2. Runs `cci flow run prepare_rlm_org --org dev-r1` (CCI auto-creates the
   `dev-r1` scratch org if it doesn't exist).
3. Restores the original `cumulusci.yml` via an `EXIT` trap in all cases.

## Agent responsibilities

When you (the agent) run this command:

1. From the repo root, execute `scripts/build_pde_dev_r1.sh` (add
   `RECREATE_ORG=true` only if a fresh org is wanted).
2. Stream/inspect the CCI output. If the build fails, surface the failing step
   and consult `.cursor/skills/troubleshooting/SKILL.md`. Do **not** re-commit
   or "fix" `cumulusci.yml` — the override is intentional and is auto-reverted.
3. After the run, confirm `git status` shows **no** modification to
   `cumulusci.yml` (the trap should have restored it). If it somehow remained
   modified, restore it with `git checkout -- cumulusci.yml` and report this.
4. Report the org alias, the flow result, and the SF CLI alias
   (`rlm-base__dev-r1`) for opening the org.

## Converting to a Cloud Agent (scheduled runs)

This file is self-contained on purpose. To run on a schedule, create a Cursor
Cloud Agent whose prompt is: *"Run the `build-pde-dev-r1` command in this repo"*
(or paste this file's body). For a clean org each run, instruct it to use
`RECREATE_ORG=true`. The build never mutates tracked files, so scheduled runs
leave the branch clean.

## Notes / guardrails

- Do not change `pde`/`billing_ui` defaults in `cumulusci.yml` on `main` —
  this build adjusts them only at runtime.
- `pde` is currently a declared flag with no `when:` gate in `cumulusci.yml`;
  setting it is correct for org-type intent but has no build-time effect on its
  own today. `billing_ui: false` is what materially changes this build.
- Per `AGENTS.md`, never push directly to `main`; this command does not commit
  anything.
