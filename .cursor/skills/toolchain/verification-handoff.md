# Verifying the Toolchain Across Workstations

Use this when a toolchain or setup-guide change has to be proven on more than one
machine, for example a maintainer's other workstations or a contributor's laptop,
before the change counts as done. Every workstation runs the same read-only
procedure against the same commit and returns one report. The change is verified
when every listed workstation has reported a pass.

## Before you hand it out

1. **Pin the commit.** Normally that's the merge commit on `main`. To test a change
   that could break machines (for example `update-toolchain.sh`) *before* it lands,
   pin the PR's head SHA instead and say so in the brief. Only do that when the
   code is trusted: the audit runs repository code (`validate_setup`,
   `gate_python.py`, `.envrc`, `update-toolchain.sh` if agreed, and the agent hooks
   and instructions an agent loads from the checkout, this file included), and
   that code can read anything the workstation's user can. A branch in the canonical
   repository that a maintainer wrote or has reviewed in full is trusted. **Never
   run another person's fork PR head on a workstation that holds credentials.** Verify it after
   merge, or in a disposable environment with no secrets.
2. **List the workstations and their kind:** **plain** (no IT management) or
   **managed** (see [`managed-workstations.md`](managed-workstations.md)). Cover both
   kinds when the change touches shell setup, certificates or PATH.
3. **Decide what each machine proves:** the full audit, or a named subset, and
   whether the owner agrees to run `update-toolchain.sh` (step 4 below).
4. **Choose where reports go.** A private place (a maintainer tracker, or a direct
   message) can take full reports. A public issue gets only the redacted form (see
   *Report*).

## Procedure (each workstation)

Pasting into an interactive zsh? Run `setopt interactivecomments` first: zsh
treats `#` as a command otherwise, which breaks lines with comments.

1. **Start clean.** In the main checkout, `git status --short` must be empty. If it
   isn't, ask the owner. Never commit their work (it could land on `main`) or
   discard it. With their OK, set it aside, untracked files included:
   ```bash
   git stash push -u -m toolchain-verify
   ```
2. **Fetch the canonical repository.** That's `upstream` on a fork (CONTRIBUTING.md),
   otherwise `origin`. Confirm the printed URL is the canonical repository
   (`bgaldino/rlm-base-dev`, or its current location per CONTRIBUTING.md) before
   going on. On a fork clone without an `upstream` remote, this prints the fork:
   stop and add `upstream` first, since everything below trusts this remote.
   ```bash
   remote=$(git remote | grep -x upstream || echo origin)
   # The URL is shown with any user:password@ or token@ redacted.
   echo "canonical remote: $remote -> $(git remote get-url "$remote" | sed -E 's#(://)[^/@]+@#\1<redacted>@#g')"
   git fetch "$remote"
   # A canonical-repo branch is in that fetch. Don't fetch and run a fork's PR head
   # here (step 1); step 3 refuses it anyway.
   ```
3. **Check out the pinned commit without moving any branch.** Continue to step 4
   only if this prints `OK`. Any `STOP` (exit status 1) ends the procedure: report
   it, and still run `git stash pop` if you set work aside in step 1. A STOP never
   moves HEAD.
   ```bash
   # Only a commit on a branch of the canonical repository is trusted. This asks the
   # remote for its real branch tips (refs/heads/*), so local tracking-ref names
   # can't fool it: fork PR heads fetched under any name (pr/<n>, pull/<n>/head, …)
   # don't count. It doesn't prove review, which is the brief's job.
   sha=<sha>
   # The remote confirmed in step 2:
   remote=$(git remote | grep -x upstream || echo origin)
   if ! git cat-file -e "$sha^{commit}" 2>/dev/null; then
     echo "STOP: commit $sha isn't here. Re-fetch (step 2) or check the SHA." >&2; false
   else
     ok=""
     for tip in $(git ls-remote --heads "$remote" | cut -f1); do
       git merge-base --is-ancestor "$sha" "$tip" 2>/dev/null && { ok=1; break; }
     done
     if [ -n "$ok" ] && git switch -q --detach "$sha" \
        && [ "$(git rev-parse HEAD)" = "$(git rev-parse "$sha^{commit}")" ]; then
       echo "OK: at the pinned commit, which is on a canonical branch"
       direnv status | grep 'Found RC allowed'; true
     else
       echo "STOP: $sha isn't on a canonical branch, the remote couldn't be reached, or the switch failed. Don't continue." >&2; false
     fi
   fi
   ```
   direnv approves `.envrc` by its content, so if the pinned commit changed it, it
   is now blocked (`allowed` isn't 0) and the audit's direnv, Python and PATH checks
   would fail for that reason alone. Show the owner `git diff @{-1} HEAD -- .envrc`
   and run `direnv allow` only with their OK.

   When you're done: `git switch -` returns to the previous branch (re-check
   `direnv status` the same way), and `git stash pop` restores anything set aside
   in step 1.
4. **Open a new terminal outside the repo, then `cd` in.** Run the read-only audit
   in [`workstation-audit.md`](workstation-audit.md), sections 1–6. On a **plain**
   workstation that needs no corporate CA you may skip audit §6, and say so. On a
   managed workstation always run it; it can be n.a. only when audit §6's own
   conditions for that hold.
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
Result: PASS | FAIL (<check>) | INCONCLUSIVE (<check>: <reason>)
        (FAIL takes precedence over INCONCLUSIVE; list every fail and inconclusive check;
         n.a. rows don't count against PASS; only PASS verifies)
Network: <managed network / VPN on | off network>

check                          | result | evidence
validate_setup (no auto-fix)   | pass   | Passed 14; no Failed; warnings: none
gate interpreter               | pass   | ~/<repo>/.venv/bin/python
python patch (pyenv/CCI/venv)  | pass   | 3.13.x / 3.13.x / 3.13.x (latest known 3.13.x)
openssl@3                      | pass   | Installed (on request); _ssl links openssl@3
node / sf / sfdmu              | pass   | v24.x (nvm) / 2.x / 5.x (≥ 5.6.4)
.envrc + .env.local            | pass   | allowed; keys: <names only>
PATH (cd in from outside)      | pass   | pyenv shim, nvm node
NODE_EXTRA_CA_CERTS            | n.a.   | plain workstation; no corporate CA needed
update-toolchain.sh            | n.a.   | not run (owner declined)

Not checked: <anything skipped and why>
Proposed fixes: <check> → <guide section>
```

**Redact every report:**
- Write home paths as `~`.
- Never include tokens, rc-file contents, `.env.local` values or proxy or registry
  credentials. Key names, "proxy set", and URLs with `user:pass@` redacted are enough.

**For a public place, also:**
- Use a generic label ("maintainer workstation 2", "contributor laptop") rather
  than a hostname.
- Leave out the names of management tools, certificate paths and `/etc/paths.d`
  entries. Describe them generically ("a managed CA block in `~/.zshrc`").

## Briefing another agent or person

Keep the brief short and self-contained:

- What changed (a PR or commit), the pinned SHA, and why it's trusted: merged to
  `main`, or a canonical-repo branch you wrote or reviewed in full.
- Which workstation it is for, and its kind.
- "Follow `.cursor/skills/toolchain/verification-handoff.md` at that commit, return
  the report, and change nothing without asking me."
- What to skip (audit §6, the update-script run), and where to send the report.

Contributors without access to a maintainer's private tracker get the same brief:
the procedure uses only this repository.
