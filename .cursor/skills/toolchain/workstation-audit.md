# Workstation Audit — Read-Only

Run from the repo root of the **main checkout**, in a terminal opened outside the
repo and then `cd`'d into it. Nothing here installs, upgrades or edits. Report each
check as pass, fail or not applicable, with the evidence line, then propose fixes,
each linked to the guide section that covers it.

Never print whole rc files, `.env.local` or `env`: they can hold tokens. The
commands below print only key names, versions and paths.

Guide links: **DES** = [dev-environment-setup.md](../../../docs/guides/dev-environment-setup.md),
**LI** = [local-installation.md](../../../docs/guides/local-installation.md).
"Audit §N" means a section of this file.

## 1. Baseline

| Check | Command | Expect | Fix |
|-------|---------|--------|-----|
| Validator, no auto-fix | `cci task run validate_setup -o auto_fix false -o auto_fix_robot false` | A `Passed` count and no `Failed` line. Each `Warnings` entry is a finding to report (for example a missing gate interpreter), not a broken setup | The failing or warning line names the tool |
| Gate interpreter | `python3 scripts/ai/gate_python.py; echo "exit $?"` | A `.venv/bin/python` path, exit 0 | [DES: `MISSING-DEP`](../../../docs/guides/dev-environment-setup.md#pr_gatepy-reports-missing-dep-or-validate_setup-warns-gate-interpreter) |
| `.envrc` allowed | `direnv status \| grep 'Found RC allowed'` | `allowed 0` (0 means allowed, on direnv 2.33+) | `direnv allow` from the repo root |
| Signing | `git config --get commit.gpgsign; git config --get gpg.format; git config --get user.signingkey` | `true`; for `ssh`, a key file that exists (expand a leading `~` before `test -f`) or a literal `key::…`/`ssh-…` key; for GPG (`gpg.format` unset), a key, or none if gpg's default key for your email signs | [CONTRIBUTING.md → Sign your commits](../../../CONTRIBUTING.md#sign-your-commits) |

Plain `validate_setup` auto-fixes by default: it can install or update the SFDMU
plugin and `pipx inject` the Robot packages. Use the flags above whenever you are
only looking.

## 2. Python and OpenSSL

The installed 3.13 patch must equal the latest known one, and every Python that
pins a patch (CumulusCI's pipx venv, `.venv`) must equal the installed one.

| Check | Command | Expect | Fix |
|-------|---------|--------|-----|
| Patch is current | `pyenv versions --bare; pyenv latest -k 3.13` | The latest known 3.13 patch is installed | `update-toolchain.sh` (ask first) |
| `.envrc` resolves it | `direnv exec . python3 --version` | That patch | `direnv allow`; a stale `PYENV_VERSION` in an old shell |
| CCI's Python | `cci version` → `Python version:` line | The installed patch | [DES: pipx venv broken after a patch bump](../../../docs/guides/dev-environment-setup.md#pipx-venv-broken-after-python-patch-bump) |
| Gate venv's Python | `.venv/bin/python -V` | The installed patch | The gate-interpreter step of `update-toolchain.sh` rebuilds it |
| `openssl@3` kept | `brew info openssl@3 \| grep -i 'on request'` | `Installed (on request)` | [DES: OpenSSL 4 migration](../../../docs/guides/dev-environment-setup.md#cci-breaks-after-brew-upgrade-homebrew-openssl-4-migration) |
| Linkage | `otool -L "$(pyenv prefix "$(pyenv latest 3.13)")"/lib/python3.13/lib-dynload/_ssl*.so \| grep ssl` | `…/openssl@3/lib/libssl.3.dylib` | Same entry |
| CCI's ssl | `"$(pipx environment --value PIPX_LOCAL_VENVS)/cumulusci/bin/python" -c 'import ssl; print(ssl.OPENSSL_VERSION)'` | OpenSSL 3.x | Same entry |

## 3. Node, sf, SFDMU

| Check | Command | Expect |
|-------|---------|--------|
| Node from nvm | `command -v node; node -v` | Under `~/.nvm/versions/node/`, an LTS ≥ 22 |
| sf | `sf --version` | Runs under that Node |
| SFDMU | `sf plugins \| grep -i sfdmu` | 5.6.4 or later |

If `node` resolves elsewhere, another directory is ahead of nvm's on PATH; see
audit §5.

## 4. `.env.local`

| Check | Command | Expect |
|-------|---------|--------|
| Key names only | `[ -f .env.local ] && sed -nE 's/^[[:space:]]*(export[[:space:]]+)?([A-Za-z_][A-Za-z0-9_.]*)[[:space:]]*[=:].*/\2/p' .env.local` | Only the keys this machine needs (prints names, never values) |
| Ignored by git | `git check-ignore -q .env.local && echo ignored` | `ignored` |
| Chrome for Testing (if set) | `direnv exec . sh -c '"${CHROME_BINARY:-$CHROME_BIN}" --version; "$CHROMEDRIVER_PATH" --version'` | The same version for both (`validate_setup` accepts `CHROME_BINARY` or `CHROME_BIN`; `CHROME_BINARY` wins) |

`validate_setup` also reports `(from CHROME_BINARY)` / `(from CHROMEDRIVER_PATH)`
when the overrides are in effect.

## 5. PATH order in fresh shells

Run these from the repo root. `env -i` starts from an empty environment and `-lic`
reads all of `~/.zshenv`, `~/.zprofile` and `~/.zshrc`, as a Terminal window does.

```bash
# Terminal opened OUTSIDE the repo, then cd in (the recommended way).
# Capture the repo path first: $PWD inside the subshell is already /tmp.
# (Breaks only if the repo path contains a single quote.)
repo="$PWD"
(cd /tmp && env -i HOME="$HOME" TERM=xterm zsh -lic \
  "cd '$repo' && eval \"\$(direnv export zsh 2>/dev/null)\" && command -v python3 node")

# Terminal that STARTS in the repo (an IDE terminal, a restored tab)
env -i HOME="$HOME" TERM=xterm zsh -lic 'command -v python3 node'
```

Expect the first to print `~/.pyenv/shims/python3` and nvm's `node`. The second
printing `/usr/bin/python3` is the documented started-in-repo case, not a fault.
The fix is to open terminals outside the repo, never `direnv reload`
([DES §2, `~/.zprofile`](../../../docs/guides/dev-environment-setup.md#zprofile--runs-in-login-shells-only)).

## 6. Corporate CA (managed workstations)

```bash
env -i HOME="$HOME" TERM=xterm zsh -c   'echo "[$NODE_EXTRA_CA_CERTS]"'   # non-interactive
env -i HOME="$HOME" TERM=xterm zsh -lic 'echo "[$NODE_EXTRA_CA_CERTS]"'   # a Terminal window
# TLS probe in a fresh Terminal-window shell that opens outside the repo and cds
# in, so it tests nvm's Node (as in audit §5); it exits on its own within 15 s.
probe='const q = require("https").get("https://registry.npmjs.org/", r => { console.log(r.statusCode); process.exit(0) }); q.on("error", e => { console.log(e.code || e.message); process.exit(1) }); q.setTimeout(15000, () => { console.log("timeout"); process.exit(2) })'
repo="$PWD"
(cd /tmp && env -i HOME="$HOME" TERM=xterm zsh -lic \
  'cd "$2" && eval "$(direnv export zsh 2>/dev/null)" && node -e "$1"' zsh "$probe" "$repo")
```

| Result | Meaning |
|--------|---------|
| Both values are the same single existing file; the probe prints `200` with no warning | Pass |
| A value contains `:` | A colon-joined list: Node loads none of it |
| The two values differ | A later block overrides the export in one shell type |
| Empty in the non-interactive check only | The export lives in `~/.zprofile` or `~/.zshrc`; non-interactive tools don't get it |
| `Warning: Ignoring extra certs from …` | The path is wrong or not a single file |
| The probe prints `timeout` | Behind an explicit proxy this says nothing about the CA; judge by the warning |

Empty in both, with the probe passing, is fine on a workstation that needs no extra
CA. Fixes: [DES: Node TLS errors behind a corporate CA](../../../docs/guides/dev-environment-setup.md#node-tls-errors-behind-a-corporate-ca-node_extra_ca_certs).

## Report format

One row per check: `check | pass/fail/n.a. | evidence`. End with the proposed
fixes, each linked to its guide section, and anything you could not check. For a
multi-workstation round, use the report in
[`verification-handoff.md`](verification-handoff.md).
