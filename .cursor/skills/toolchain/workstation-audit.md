# Workstation Audit — Read-Only

Run from the repo root of the **main checkout**, in a terminal opened outside the
repo and then `cd`'d into it. Nothing here installs, upgrades or edits. Report each
check as pass, fail, inconclusive or not applicable, with the evidence line, then propose fixes,
each linked to the guide section that covers it.

Never print whole rc files, `.env.local` or `env`: they can hold tokens. Proxy
URLs can hold a username and password too. The commands below print only key
names, versions, paths, whether a proxy is set, and URLs with any credentials
replaced by `<redacted>`. npm itself refuses to print a setting whose URL
contains a password (a proxy or registry), and the audit reports that as
`set (credentials hidden)`.

Pasting these into an interactive zsh? Run `setopt interactivecomments` first:
zsh treats `#` as a command otherwise. Agents running commands non-interactively
aren't affected.

Guide links: **DES** = [dev-environment-setup.md](../../../docs/guides/dev-environment-setup.md),
**LI** = [local-installation.md](../../../docs/guides/local-installation.md).
"Audit §N" means a section of this file.

## 1. Baseline

| Check | Command | Expect | Fix |
|-------|---------|--------|-----|
| Validator, no auto-fix | `cci task run validate_setup -o auto_fix false -o auto_fix_robot false` | A `Passed` count and no `Failed` line. Each `Warnings` entry is a finding to report (for example a missing gate interpreter), not a broken setup | The failing or warning line names the tool. A `selenium` fail right after a `pipx upgrade cumulusci` is CCI's own `selenium<4` pin: `pipx inject --force cumulusci -r robot/requirements.txt` |
| Gate interpreter | `python3 scripts/ai/gate_python.py; echo "exit $?"` | A `.venv/bin/python` path (or `$RLM_GATE_PYTHON`, if set), exit 0 | [DES: `MISSING-DEP`](../../../docs/guides/dev-environment-setup.md#pr_gatepy-reports-missing-dep-or-validate_setup-warns-gate-interpreter) |
| `.envrc` allowed | `direnv status \| grep 'Found RC allowed'` | `allowed 0` (0 means allowed, on direnv 2.33+) | `direnv allow` from the repo root |
| Signing | `git config --get commit.gpgsign; git config --get gpg.format; git config --get user.signingkey` | `true`; for `ssh`, a key file that exists (expand a leading `~` before `test -f`) or a literal `key::…`/`ssh-…` key; for GPG (`gpg.format` unset or `openpgp`), a key, or none if gpg's default key for your email signs; for S/MIME (`gpg.format` `x509`), a key `gpgsm` can use | [CONTRIBUTING.md → Sign your commits](../../../CONTRIBUTING.md#sign-your-commits) |

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
| Gate venv's Python | `.venv/bin/python -V; grep '^home' .venv/pyvenv.cfg` | The installed patch, and a `home` under `~/.pyenv/versions/<that patch>/`. A Homebrew `home` (`/opt/homebrew/…`) passes the patch check only while the two versions match | The gate-interpreter step of `update-toolchain.sh` rebuilds it on pyenv's Python. If `$RLM_GATE_PYTHON` is set, check that interpreter instead; the script probes it but doesn't manage it |
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
repo="$PWD"
(cd /tmp && env -i HOME="$HOME" TERM=xterm zsh -lic \
  'cd "${1:?repo path missing}" && eval "$(direnv export zsh 2>/dev/null)" && command -v python3 node' zsh "$repo")

# Terminal that STARTS in the repo (an IDE terminal, a restored tab)
env -i HOME="$HOME" TERM=xterm zsh -lic 'command -v python3 node'
```

Expect the first to print `~/.pyenv/shims/python3` and nvm's `node`. The second
printing `/usr/bin/python3` is the documented started-in-repo case, not a fault.
The fix is to open terminals outside the repo, never `direnv reload`
([DES §2, `~/.zprofile`](../../../docs/guides/dev-environment-setup.md#zprofile--runs-in-login-shells-only)).

## 6. Corporate CA (managed workstations)

```bash
# non-interactive
env -i HOME="$HOME" TERM=xterm zsh -c   'echo "[$NODE_EXTRA_CA_CERTS]"'
# a Terminal window
env -i HOME="$HOME" TERM=xterm zsh -lic 'echo "[$NODE_EXTRA_CA_CERTS]"'
env -i HOME="$HOME" TERM=xterm zsh -lic \
  'echo "[TLS_REJECT=$NODE_TLS_REJECT_UNAUTHORIZED][HTTPS_PROXY=${HTTPS_PROXY:+set}][https_proxy=${https_proxy:+set}][HTTP_PROXY=${HTTP_PROXY:+set}][http_proxy=${http_proxy:+set}]"'
# The real check, in a fresh Terminal-window shell opened outside the repo (as in
# audit §5): npm's own proxy settings, one attempt.
repo="$PWD"
(cd /tmp && env -i HOME="$HOME" TERM=xterm zsh -lic \
  'cd "${1:?repo path missing}" && eval "$(direnv export zsh 2>/dev/null)" && for k in ca cafile strict-ssl registry proxy https-proxy; do v=$(npm config get "$k" 2>&1); case "$v" in *"is protected"*) v="set (credentials hidden)";; esac; echo "$k=$v"; done | sed -E "s#(://)[^/@]+@#\\1<redacted>@#g" && npm ping --fetch-retries=0 --loglevel=notice 2>&1 | sed -E "s#(://)[^/@]+@#\\1<redacted>@#g"' zsh "$repo")

# Only when the ca/cafile row below sends you here: the guide's direct probe, in the
# same kind of fresh shell, passed as an argument (its quotes can't be spliced in).
probe='setTimeout(() => { console.log("timeout"); process.exit(2) }, 15000); require("https").get("https://registry.npmjs.org/", r => { console.log(r.statusCode); process.exit(0) }).on("error", e => { console.log(e.code || e.message); process.exit(1) })'
(cd /tmp && env -i HOME="$HOME" TERM=xterm zsh -lic \
  'cd "${1:?repo path missing}" && eval "$(direnv export zsh 2>/dev/null)" && node -e "$2"' zsh "$repo" "$probe")
```

If you run these as separate shell calls, set `repo=<path to the main checkout>` in each one first; without it they stop with "repo path missing".

| Result | Meaning |
|--------|---------|
| Both values are the same single existing file; `TLS_REJECT` empty or anything but `0`; `ca=null`, `cafile=null`, `strict-ssl=true`, an `https://` registry; `npm ping` prints `PONG` (or an HTTP code such as `E404`) with no warning; run on the managed network | Pass. Record the network ("on VPN", "office"). Off the managed network the inspecting proxy isn't in the path, so the corporate CA wasn't exercised: record **inconclusive (off network)** instead. A macOS system proxy or PAC file is invisible to npm and Node, so if inspection only happens through one, this check can't see it: note that |
| `registry=set (credentials hidden)` | Read the registry's scheme from `npm ping`'s `PING <url>` line (redacted): `https://` can satisfy the Pass row, `http://` is the next row |
| `strict-ssl=false`, or an `http://` registry | **Inconclusive**: npm doesn't check certificates, so `PONG` proves nothing about the CA |
| `TLS_REJECT=0` | **Fail**: npm still verifies, but `sf` and other Node processes don't. Remove the variable |
| A value contains `:` | Fail: a colon-joined list, so Node loads none of it |
| The two values differ | Fail: a later block overrides the export in one shell type |
| Empty in the non-interactive check only | Fail: the export lives in `~/.zprofile` or `~/.zshrc`, so non-interactive tools don't get it |
| `ca` or `cafile` is set | npm uses only that trust store, so `PONG` verifies npm's trust, not `NODE_EXTRA_CA_CERTS`. If the workstation has no explicit proxy (all four proxy variables above empty, npm's `proxy`/`https-proxy` null; npm also uses `HTTP_PROXY`/`http_proxy` for HTTPS), run the direct-probe command from the block above on the managed network (a fresh shell, not the agent's own, which can carry an older value). **Pass** if it prints an HTTP status and the other Pass conditions hold; **Fail** on a certificate code. Otherwise **Inconclusive (`cafile` set; `NODE_EXTRA_CA_CERTS` unverified)** |
| `Warning: Ignoring extra certs from …` | Fail: the path is wrong or not a single file (even if `PONG` follows) |
| `npm error code` with a certificate code (`UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, `UNABLE_TO_VERIFY_LEAF_SIGNATURE`, `SELF_SIGNED_CERT_IN_CHAIN`, `DEPTH_ZERO_SELF_SIGNED_CERT`, …) | On the managed network, **Fail**: npm and Node don't trust the corporate CA. The file lacks the right certificate, or the variable isn't set in that shell (or npm's `ca`/`cafile`, if set, lacks it). Off the managed network, a captive portal or other proxy can cause this too: **inconclusive (off network)** |
| `CERT_HAS_EXPIRED` / `CERT_NOT_YET_VALID`, or `ERR_TLS_CERT_ALTNAME_INVALID` | Fail, but not fixed by adding a CA: a stale bundle or the system clock, or a hostname mismatch |
| Any other code (`ECONNREFUSED`, `ECONNRESET`, `ENETUNREACH`, `ENOTFOUND`, `ETIMEDOUT`, …) | **Inconclusive**: a network or proxy problem, not a CA verdict. Record it with the code |

If several rows match, **Fail** wins over **Inconclusive**, and both win over Pass.

Empty in both is a **pass** (or n.a.) only on a workstation that needs no extra
CA, shown by every other Pass condition holding, the managed network included.
`npm ping --fetch-retries=0 --loglevel=notice` makes one attempt, but a silently dropped connection
can still take over a minute: let it finish and record the code. Fixes:
[DES: Node TLS errors behind a corporate CA](../../../docs/guides/dev-environment-setup.md#node-tls-errors-behind-a-corporate-ca-node_extra_ca_certs).

## Report format

One row per check: `check | pass/fail/inconclusive/n.a. | evidence`. Give an
inconclusive result its reason, for example "inconclusive (ETIMEDOUT); CA
unverified" or "inconclusive (strict-ssl=false)". End with the proposed
fixes, each linked to its guide section, and anything you could not check. For a
multi-workstation round, use the report in
[`verification-handoff.md`](verification-handoff.md).
