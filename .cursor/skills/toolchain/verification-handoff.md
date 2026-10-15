# Verifying the Toolchain Across Workstations

Use this when a toolchain or setup-guide change has to be proven on more than one
machine, for example a maintainer's other workstations or a contributor's laptop,
before the change counts as done. Every workstation runs the same read-only
procedure against the same commit and returns one report. The change is verified
when every listed workstation has reported a pass.

## Before you hand it out

1. **Pin the commit.** Normally that's the merge commit on `main`. To test a change
   that could break machines (for example `update-toolchain.sh`) *before* it lands,
   pin the PR's head SHA instead and say so in the brief.
2. **List the workstations and their kind:** **plain** (no IT management) or
   **managed** (see [`managed-workstations.md`](managed-workstations.md)). Cover both
   kinds when the change touches shell setup, certificates or PATH.
3. **Decide what each machine proves:** the full audit, or a named subset, and
   whether the owner agrees to run `update-toolchain.sh` (step 4 below).
4. **Choose where reports go.** A private place (a maintainer tracker, or a direct
   message) can take full reports. A public issue gets only the redacted form (see
   *Report*).

## Procedure (each workstation)

1. **Start clean.** In the main checkout, `git status --short` must be empty. If it
   isn't, ask the owner. Never commit their work (it could land on `main`) or
   discard it. With their OK, set it aside, untracked files included:
   ```bash
   git stash push -u -m toolchain-verify
   ```
2. **Fetch the canonical repository.** That's `upstream` on a fork (CONTRIBUTING.md),
   otherwise `origin`:
   ```bash
   remote=$(git remote | grep -x upstream || echo origin)
   git fetch "$remote"
   # A PR from a fork isn't in that fetch; for a pinned PR head, also:
   git fetch "$remote" "pull/<n>/head"
   ```
3. **Check out the pinned commit without moving any branch:**
   ```bash
   git switch --detach <sha>
   [ "$(git rev-parse HEAD)" = "$(git rev-parse '<sha>^{commit}')" ] && echo "at the pinned commit"
   direnv status | grep 'Found RC allowed'
   ```
   direnv approves `.envrc` by its content, so if the pinned commit changed it, it
   is now blocked (`allowed` isn't 0) and the audit's direnv, Python and PATH checks
   would fail for that reason alone. Show the owner `git diff @{-1} HEAD -- .envrc`
   and run `direnv allow` only with their OK.

   When you're done: `git switch -` returns to the previous branch (re-check
   `direnv status` the same way), and `git stash pop` restores anything set aside
   in step 1.
4. **Open a new terminal outside the repo, then `cd` in.** Run the read-only audit
   in [`workstation-audit.md`](workstation-audit.md), sections 1–6. Skip audit §6
   on a workstation that needs no corporate CA, and say so.
5. **Only if the owner explicitly agrees,** run `update-toolchain.sh` and repeat the
   audit. It upgrades the whole machine. Prove it left the shell files alone:
   ```bash
   shasum ~/.zshenv ~/.zprofile ~/.zshrc 2>/dev/null > /tmp/rc.before
   scripts/bash/update-toolchain.sh
   shasum ~/.zshenv ~/.zprofile ~/.zshrc 2>/dev/null | diff /tmp/rc.before - && echo "rc files unchanged"
   ```
6. **Change nothing else.** Anything that fails goes in the report with the guide
   section that covers it. The owner decides on fixes.

## Report (one per workstation)

```text
Workstation: <label>   Kind: plain | managed   Date: <YYYY-MM-DD>   Commit: <short SHA>
Result: PASS | FAIL

check                          | result | evidence
validate_setup (no auto-fix)   | pass   | Passed 14; no Failed; warnings: none
gate interpreter               | pass   | ~/<repo>/.venv/bin/python
python patch (pyenv/CCI/venv)  | pass   | 3.13.x / 3.13.x / 3.13.x (latest known 3.13.x)
openssl@3                      | pass   | Installed (on request); _ssl links openssl@3
node / sf / sfdmu              | pass   | v24.x (nvm) / 2.x / 5.x (≥ 5.6.4)
.envrc + .env.local            | pass   | allowed; keys: <names only>
PATH (cd in from outside)      | pass   | pyenv shim, nvm node
NODE_EXTRA_CA_CERTS            | n.a.   | not needed on this machine
update-toolchain.sh            | n.a.   | not run (owner declined)

Not checked: <anything skipped and why>
Proposed fixes: <check> → <guide section>
```

**Redact every report:**
- Write home paths as `~`.
- Never include tokens, rc-file contents or `.env.local` values. Key names are enough.

**For a public place, also:**
- Use a generic label ("maintainer workstation 2", "contributor laptop") rather
  than a hostname.
- Leave out the names of management tools, certificate paths and `/etc/paths.d`
  entries. Describe them generically ("a managed CA block in `~/.zshrc`").

## Briefing another agent or person

Keep the brief short and self-contained:

- What changed (a PR or commit), and the pinned SHA.
- Which workstation it is for, and its kind.
- "Follow `.cursor/skills/toolchain/verification-handoff.md` at that commit, return
  the report, and change nothing without asking me."
- What to skip (audit §6, the update-script run), and where to send the report.

Contributors without access to a maintainer's private tracker get the same brief:
the procedure uses only this repository.
