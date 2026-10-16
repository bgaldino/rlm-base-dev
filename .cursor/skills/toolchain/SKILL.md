---
name: toolchain
description: >-
  Set up, audit, update and verify a local rlm-base-dev developer toolchain (Homebrew,
  pyenv Python 3.13, nvm Node LTS, pipx CumulusCI, sf CLI and SFDMU, direnv, the gate
  interpreter .venv, Chrome for Testing) without breaking the workstation. Use when
  setting up or replicating a workstation, running or debugging update-toolchain.sh,
  checking shell config or PATH order, handling a managed workstation's corporate CA
  or tool-managed shell blocks, or verifying a setup on several workstations. For a
  failing build step rather than the toolchain itself, use troubleshooting.
---

# Toolchain — Set Up, Audit, Update and Verify a Workstation

The setup guides describe the toolchain:
[local-installation.md](../../../docs/guides/local-installation.md) installs it step
by step, and [dev-environment-setup.md](../../../docs/guides/dev-environment-setup.md)
is the canonical layout, update routine and troubleshooting. This skill is how an
agent works on a real workstation: audit it read-only, change only what was asked,
and prove the result with checks that can't pass by accident. It is plain markdown
for any agent.

## Quick Rules

1. **Audit before you change anything.** Run the read-only audit with
   `python3 scripts/ai/toolchain_audit.py --section N` (or `--all`), read each
   result against its row in [`workstation-audit.md`](workstation-audit.md), and
   report what it found. The user decides what gets fixed.
2. **The guides are the source of truth.** Point to the guide section that covers a
   fix instead of improvising one; if the guide is wrong, fix the guide in the same
   change.
3. **Shell files are merged, never replaced or hand-edited by you.** Running the
   installation guide's documented steps at the user's request is fine. Anything
   else in an rc file is a proposal for the user to apply. Leave tool-managed blocks
   alone ([`managed-workstations.md`](managed-workstations.md)).
4. **Check what a fresh shell gets, not what you inherited.** Use
   `env -i HOME="$HOME" zsh -c …` (non-interactive) and `… zsh -lic …` (a Terminal
   window). A plain `zsh -c` inherits your current exports and can pass falsely.
5. **Open terminals outside the repo, then `cd` in.** A login shell that starts in
   the repo has the system PATH order.
6. **Machine-specific values go in `.env.local`**, which is gitignored and loaded by
   `.envrc` and `./tui-cci`. Never in the tracked `.envrc`.
7. **Audit runs of `validate_setup` turn off its auto-fixes:**
   `cci task run validate_setup -o auto_fix false -o auto_fix_robot false`. By
   default it can install or update the SFDMU plugin and the Robot packages.

## DO NOT

- **DO NOT** run anything copied out of `workstation-audit.md`'s tables. Their
  columns are the check's id, what to expect and where the fix is documented; every
  audit command is in `scripts/ai/toolchain_audit.py`
  (`--show <id>` prints one without running it).
- **DO NOT** print, `cat` or paste rc files (`~/.zshrc`, `~/.zshenv`, `~/.zprofile`),
  `.env.local`, or `env` output. They often hold tokens, and proxy or registry URLs
  can hold a username and password. Search for the specific
  names you need (`grep -n 'NODE_EXTRA_CA_CERTS' ~/.zshrc`) and redact values. If a
  secret is exposed anyway, say so and recommend rotating it.
- **DO NOT** run `scripts/bash/update-toolchain.sh`, `brew upgrade`, `pyenv install`,
  or `validate_setup` with its auto-fixes on, unless the user asked. They change the
  machine.
- **DO NOT** replace the user's rc files with the guide's templates
  ([dev-environment-setup.md §5](../../../docs/guides/dev-environment-setup.md#5-replicating-on-a-new-workstation)
  merges them).
- **DO NOT** suggest `direnv reload`, or `cd` out and back in, for a login shell that
  started in the repo. Both drop system and managed PATH entries
  ([why](../../../docs/guides/dev-environment-setup.md#zprofile--runs-in-login-shells-only)).
- **DO NOT** set `NODE_EXTRA_CA_CERTS` to a colon-separated list, or blame it for an
  `nvm install` TLS failure (nvm downloads with curl/wget). See
  [the CA entry](../../../docs/guides/dev-environment-setup.md#node-tls-errors-behind-a-corporate-ca-node_extra_ca_certs).
- **DO NOT** let `openssl@3` go: the pyenv 3.13 builds link it
  ([OpenSSL 4 migration](../../../docs/guides/dev-environment-setup.md#cci-breaks-after-brew-upgrade-homebrew-openssl-4-migration)).
- **DO NOT** read `cci version` succeeding as "on the current Python patch". The
  installed patch must equal `pyenv latest -k 3.13`, and CCI's and `.venv`'s Python
  must equal the installed patch.
- **DO NOT** add machine paths (Chrome for Testing, certificates) to `.envrc`.

## Entry Conditions

| Task | Read |
|------|------|
| Set up a new workstation, or replicate one | This skill, then [local-installation.md Steps 1–11](../../../docs/guides/local-installation.md#macos-environment-setup-homebrew--pyenv--nvm) and [dev-environment-setup.md §5](../../../docs/guides/dev-environment-setup.md#5-replicating-on-a-new-workstation) |
| "Is my setup OK?", or before changing anything | [`workstation-audit.md`](workstation-audit.md) |
| Update the toolchain, or something broke after an update | [dev-environment-setup.md §4](../../../docs/guides/dev-environment-setup.md#4-maintaining-the-toolchain) and [§6](../../../docs/guides/dev-environment-setup.md#6-troubleshooting); the audit to confirm |
| Corporate CA, proxy, IT-managed shell blocks, `/etc/paths.d` | [`managed-workstations.md`](managed-workstations.md) |
| Verify the setup on several workstations, or hand the check to someone | [`verification-handoff.md`](verification-handoff.md) |
| A CCI flow, deploy or data load fails | `troubleshooting` skill instead (it covers toolchain causes such as the CCI token issue) |
| Containerized toolchain instead of a local one | `docker/README.md` |
| Build harness or `./tui-cci` | `build-harness` skill |

## Sub-files

- [`workstation-audit.md`](workstation-audit.md) — read this before changing or
  vouching for a workstation: every check, the expected result and where the fix
  is documented. The commands run from `scripts/ai/toolchain_audit.py`, one section
  or check at a time.
- [`managed-workstations.md`](managed-workstations.md) — read this on a machine with
  IT-managed configuration: what to look for, what not to touch, and which guide
  section covers each case.
- [`verification-handoff.md`](verification-handoff.md) — read this to verify the
  setup across workstations: the procedure, the report format, and how to brief
  another person or agent.

## How the pieces fit

| Layer | Where | Notes |
|-------|-------|-------|
| Shell init | `~/.zshenv` (every shell), `~/.zprofile` (login), `~/.zshrc` (interactive) | Layout in [dev-environment-setup.md §2](../../../docs/guides/dev-environment-setup.md#2-system-layout) |
| Per-project activation | `.envrc` (tracked) + `.env.local` (gitignored, dotenv) | direnv; `./tui-cci` also loads `.env.local` |
| Python | pyenv, latest 3.13 patch; `openssl@3` kept | pipx CumulusCI venv, `.venv` and each `.harness/tui-venv` pin one patch; `pyenv global` follows the line only from an old patch with no packages of its own |
| Audit | `scripts/ai/toolchain_audit.py` | Read-only; runs each check of `workstation-audit.md` and prints the evidence, judging nothing |
| Gate interpreter | `<main checkout>/.venv` | Found by `scripts/ai/gate_python.py`; `pr_gate.py` re-runs under it when its own interpreter lacks a selected check's dependency |
| Node / sf / SFDMU | nvm, the major line pinned in `.nvmrc` (24); `sf` under it; `sfdmu` plugin ≥ 5.6.4 | Moving to a new major is a deliberate PR: `.nvmrc`, the Dockerfile's `NODE_MAJOR`, CI and `engines` together |
| Robot browser | stock Chrome, or Chrome for Testing via `.env.local` | Where stock Chrome fails on Setup pages |
| Updates | `scripts/bash/update-toolchain.sh` | Changes the whole machine; ask first |

## Examples

**"Check my setup."** Run `python3 scripts/ai/toolchain_audit.py --section 1`, then
sections 2–6, and read the output against [`workstation-audit.md`](workstation-audit.md).
Report a table of check, result and evidence, and list fixes as proposals with the
guide section for each. Change nothing.

**"`cci` dies with `Library not loaded: …openssl@3…` after brew upgrade."** That is
[*OpenSSL 4 migration*](../../../docs/guides/dev-environment-setup.md#cci-breaks-after-brew-upgrade-homebrew-openssl-4-migration). Propose
`brew install openssl@3 && brew tab --installed-on-request openssl@3`, then confirm
with `cci version`.

**"npm fails with `SELF_SIGNED_CERT_IN_CHAIN` on my work laptop."** Run
`python3 scripts/ai/toolchain_audit.py --section 6` and read it against
[audit §6](workstation-audit.md#6-corporate-ca-managed-workstations).
Look for a colon-joined value, an export only in `~/.zshrc`, or a later block
overriding it, and propose the fix from the guide's CA entry. Re-run audit §6 to
confirm.

**"Verify this on the other machines."** Use
[`verification-handoff.md`](verification-handoff.md): brief each workstation with
the procedure and collect one report per machine.

## Validation Checks

- `cci task run validate_setup -o auto_fix false -o auto_fix_robot false` reports no
  `Failed` line, and any `Warnings` are reported as findings (no org needed).
- `python3 scripts/ai/gate_python.py` prints the gate interpreter and exits 0.
- `python tests/test_toolchain_audit.py` passes after any change to the audit doc or
  `scripts/ai/toolchain_audit.py`: every row names a check the script has, no table
  cell holds a command, and the script runs nothing that changes the machine.
- For any change to this skill or the guides, all of these pass:
  - `python scripts/ai/analyze_agent_tooling.py check`;
  - `python scripts/ai/skill_manifest.py --check` (when the manifest changed);
  - `python scripts/ai/pr_gate.py --base origin/main`.

  The guide sections the skill links must still exist.
