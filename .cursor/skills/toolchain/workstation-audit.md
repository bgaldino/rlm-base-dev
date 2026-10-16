# Workstation Audit — Read-Only

Run from the repo root of the **main checkout**, in a terminal opened outside the
repo and then `cd`'d into it. Nothing here installs, upgrades or edits. Report each
check as pass, fail, inconclusive or not applicable, with the evidence line, then propose fixes,
each linked to the guide section that covers it.

## How to run it

Every check's command lives in one read-only script. Run a section at a time:

```bash
python3 scripts/ai/toolchain_audit.py --section 1
```

`--section` takes 1–6 and can be repeated; `--all` runs sections 1–6; `--check <id>`
runs one check; `--list` names every check by section. Each check prints a
`== §N <id>: <title>` header, its output and `[exit N]`. The script runs each
command in its own zsh (bash if zsh is missing) from the repo root and judges
nothing: read each check's output against its row below. An exit status isn't a
verdict either (`git config --get` exits 1 for an unset key). Allow a few minutes
for `--all`: `validate_setup` and `npm ping` are slow. Run from a linked worktree, it
says so in its first lines and names the main checkout, the one to audit.

**Never run anything from the tables below.** Their columns are the check's id,
what to expect and where the fix is documented. A fix is a proposal for the owner,
and its guide section gives the commands with their warnings. To see a check's
command, `python3 scripts/ai/toolchain_audit.py --show <id>` prints it without
running it.

Never print whole rc files, `.env.local` or `env`: they can hold tokens. Proxy
URLs can hold a username and password too. The checks print only key
names, versions, paths, whether a proxy is set, and URLs with any credentials
replaced by `<redacted>`. npm itself refuses to print a setting whose URL
contains a password (a proxy or registry), and the audit reports that as
`set (credentials hidden)`.

Guide links: **DES** = [dev-environment-setup.md](../../../docs/guides/dev-environment-setup.md),
**LI** = [local-installation.md](../../../docs/guides/local-installation.md).
"Audit §N" means a section of this file.

## 1. Baseline

`python3 scripts/ai/toolchain_audit.py --section 1`

| Check | Expect | Fix |
|-------|--------|-----|
| `validate-setup`: validator, no auto-fix | A `Passed` count and no `Failed` line. Each `Warnings` entry is a finding to report (for example a missing gate interpreter), not a broken setup | The failing or warning line names the tool. A `selenium` fail right after CumulusCI was upgraded with pipx is CCI's own `selenium<4` pin: re-inject the repo's Robot pins ([DES §4, update routine step 6](../../../docs/guides/dev-environment-setup.md#update-routine)) |
| `gate-interpreter`: gate interpreter | A `.venv/bin/python` path (or `$RLM_GATE_PYTHON`, if set), `exit 0` | [DES: `MISSING-DEP`](../../../docs/guides/dev-environment-setup.md#pr_gatepy-reports-missing-dep-or-validate_setup-warns-gate-interpreter) |
| `envrc-allowed`: `.envrc` allowed | `allowed 0` (0 means allowed, on direnv 2.33+) | Approve `.envrc` with direnv from the repo root, with the owner's OK ([DES §3, first-time activation](../../../docs/guides/dev-environment-setup.md#first-time-activation)) |
| `signing`: commit signing | `true`; for `ssh`, a key file that exists (expand a leading `~` before checking it) or a literal `key::…`/`ssh-…` key; for GPG (`gpg.format` unset or `openpgp`), a key, or none if gpg's default key for your email signs; for S/MIME (`gpg.format` `x509`), a key `gpgsm` can use | [CONTRIBUTING.md → Sign your commits](../../../CONTRIBUTING.md#sign-your-commits) |

Plain `validate_setup` auto-fixes by default: it can install or update the SFDMU
plugin and re-inject the Robot packages into CCI's venv. The script turns both off.

## 2. Python and OpenSSL

`python3 scripts/ai/toolchain_audit.py --section 2`

The installed 3.13 patch must equal the latest known one, and every Python that
pins a patch (CumulusCI's pipx venv, `.venv`) must equal the installed one.

| Check | Expect | Fix |
|-------|--------|-----|
| `patch-current`: patch is current | The latest known 3.13 patch (the last line) is among the installed versions | [The update script](../../../docs/guides/dev-environment-setup.md#update-routine) (ask first) |
| `pyenv-global`: `pyenv global` | The installed patch, or a deliberate other choice (`system`, another line). An older 3.13 patch is a finding: the output after the global's name lists the packages pip-installed into it, which are why the update script left it (none listed means it hasn't been run since). Never uninstall the version the global names | Reinstall those packages under the current patch (or with pipx), then move the global to it: [DES: version not installed](../../../docs/guides/dev-environment-setup.md#pyenv-version-313x-is-not-installed-set-by-pyenvversion) |
| `envrc-python`: `.envrc` resolves it | That patch | If `envrc-allowed` fails, its fix. Otherwise a stale `PYENV_VERSION` in an old shell: open a new terminal outside the repo and `cd` in ([DES §3, verify](../../../docs/guides/dev-environment-setup.md#verify)) |
| `cci-python`: CCI's Python | The `Python version:` line names the installed patch | [DES: pipx venv broken after a patch bump](../../../docs/guides/dev-environment-setup.md#pipx-venv-broken-after-python-patch-bump) |
| `tui-venvs`: TUI venvs' Python | The installed patch for each checkout listed (none is fine: `./tui-cci` creates one on first run). The exit status is 1 whenever the last checkout listed has none: ignore it | The update script's TUI-venv step rebuilds them ([DES §4, update routine step 9](../../../docs/guides/dev-environment-setup.md#update-routine)) |
| `older-patch-users`: other users of an older patch | Nothing printed. Anything listed runs on a superseded 3.13 patch and breaks when that patch is uninstalled; check this before uninstalling any pyenv version. Apps kept on another line (3.12, 3.14) or a non-pyenv Python aren't listed: that's a choice, not drift | [DES: a pipx app or a script in `~/.local/bin` is on an older 3.13 patch](../../../docs/guides/dev-environment-setup.md#a-pipx-app-or-a-script-in-localbin-is-on-an-older-313-patch) |
| `pipx-shared-venv`: pipx shared venv | Nothing printed. `shared:` means the pip every pipx app uses runs on another Python: pipx keeps it on whichever Python first ran pipx, and no update moves it. `pth <app> (other lib):` means an app on 3.13 loads pip from another Python's `lib`. That works now, but the app loses pip once the shared venv is rebuilt. `pth <app> (missing):` means that app's pip is already gone, so pipx can't inject into or upgrade it. Apps kept on another line aren't checked for `other lib`: with one shared venv, that's expected. Check this before uninstalling any pyenv version, including the line the shared venv is on | [DES: pipx's shared venv is on another Python](../../../docs/guides/dev-environment-setup.md#pipxs-shared-venv-is-on-another-python), which picks the route by where the shared venv is (ask first) |
| `gate-venv-python`: gate venv's Python | The installed patch, and a `home` under `~/.pyenv/versions/<that patch>/`. A Homebrew `home` (`/opt/homebrew/…`) passes the patch check only while the two versions match | The update script's gate-interpreter step rebuilds it on pyenv's Python ([DES §4, update routine step 8](../../../docs/guides/dev-environment-setup.md#update-routine)). If `$RLM_GATE_PYTHON` is set, check that interpreter instead; the script probes it but doesn't manage it |
| `openssl-kept`: `openssl@3` kept | `Installed (on request)` | [DES: OpenSSL 4 migration](../../../docs/guides/dev-environment-setup.md#cci-breaks-after-brew-upgrade-homebrew-openssl-4-migration) |
| `ssl-linkage`: linkage | `…/openssl@3/lib/libssl.3.dylib` | Same entry |
| `cci-ssl`: CCI's ssl | OpenSSL 3.x | Same entry |

## 3. Node, sf, SFDMU

`python3 scripts/ai/toolchain_audit.py --section 3`

| Check | Expect | Fix |
|-------|--------|-----|
| `node`: Node from nvm | Under `~/.nvm/versions/node/`, a v24.x: the major in `.nvmrc` (24). `validate_setup` fails an older major and warns on a newer one (and on an nvm `default` alias that resolves to another major) | [LI Step 3](../../../docs/guides/local-installation.md#step-3--install-nodejs-via-nvm) installs the line; [the update script](../../../docs/guides/dev-environment-setup.md#update-routine) (ask first) moves it to the newest patch |
| `nvm-default`: nvm's default alias | `default -> 24 -> v24.x`: the alias names `.nvmrc`'s major (or one exact v24 version) and resolves to it. **Fail** if it resolves to another major, or names a floating alias (`node`, `stable`, `lts/*`) even while it still resolves to v24: that moves to the next major the day one is installed, taking every shell outside the repo and every startup file that prepends `default` with it. `nvm not found` is n.a. here (the `node` row covers it). `validate_setup` warns on a mismatch | [The update script](../../../docs/guides/dev-environment-setup.md#update-routine) (ask first) sets the alias from `.nvmrc` (step 3) |
| `node-nested-shell`: a shell started from a repo shell | `.envrc loaded`, then the nested shell's `node` is the repo shell's: the same v24.x (the major in `.nvmrc`) from the same path, and its list of nvm Node dirs is the repo shell's list, unchanged. **Fail** if the nested shell's `node` comes from another path, usually Homebrew's: `brew shellenv` in `~/.zshenv` puts Homebrew's bin first in every shell. **Fail** if the nested shell's list gains an entry, even the same version: a startup file (usually `~/.zshenv`) prepends a Node in every shell, and direnv doesn't re-apply `.envrc` in a shell that inherits it loaded, so once a newer Node is installed (or `default` changes) agents, IDE tasks and scripts run it. `NOT loaded` is inconclusive: fix `envrc-allowed` first | Merge the NVM block of [the `~/.zshenv` template](../../../docs/guides/dev-environment-setup.md#zshenv--runs-in-every-shell), which skips the prepend inside a direnv environment and prepends `default`, never the newest installed version (owner applies it). For a Homebrew `node`, [LI Step 3](../../../docs/guides/local-installation.md#step-3--install-nodejs-via-nvm) says how to remove it |
| `sf`: sf | An npm-installed sf (listed by the `npm ls -g` part) runs under that Node. An installer-based sf (not listed, usually `/usr/local/bin/sf`) runs its own bundled Node, which is fine; the update script updates it with sf's own updater | [The update script](../../../docs/guides/dev-environment-setup.md#update-routine) (ask first), step 4 |
| `sfdmu`: SFDMU | 5.6.4 or later | `validate_setup` with its auto-fix on updates the plugin (ask first) |

If `node` resolves elsewhere, another directory is ahead of nvm's on PATH; see
audit §5.

## 4. `.env.local`

`python3 scripts/ai/toolchain_audit.py --section 4`

| Check | Expect |
|-------|--------|
| `env-keys`: key names only | Only the keys this machine needs (prints names, never values). No output and exit 1 means there's no `.env.local` |
| `env-ignored`: ignored by git | `ignored` |
| `chrome-for-testing`: Chrome for Testing (if set) | The same version for both (`validate_setup` accepts `CHROME_BINARY` or `CHROME_BIN`; `CHROME_BINARY` wins). Neither set in `.env.local` is n.a.: the command isn't found (exit 127) |

`validate_setup` also reports `(from CHROME_BINARY)` / `(from CHROMEDRIVER_PATH)`
when the overrides are in effect.

## 5. PATH order in fresh shells

`python3 scripts/ai/toolchain_audit.py --section 5`

Both checks start from an empty environment (`env -i`) and read all of
`~/.zshenv`, `~/.zprofile` and `~/.zshrc` (`zsh -lic`), as a Terminal window does.

| Check | Expect |
|-------|--------|
| `path-outside-repo`: a terminal opened outside the repo, then `cd`'d in (the recommended way) | `~/.pyenv/shims/python3` and nvm's `node` |
| `path-started-in-repo`: a terminal that starts in the repo (an IDE terminal, a restored tab) | `/usr/bin/python3`, or a Homebrew or python.org `python3`, is the documented started-in-repo case, not a fault |

The fix is to open terminals outside the repo, never `direnv reload`
([DES §2, `~/.zprofile`](../../../docs/guides/dev-environment-setup.md#zprofile--runs-in-login-shells-only)).

## 6. Corporate CA (managed workstations)

`python3 scripts/ai/toolchain_audit.py --section 6`

| Check | What it prints |
|-------|----------------|
| `ca-non-interactive` | `[$NODE_EXTRA_CA_CERTS]` in a fresh non-interactive zsh |
| `ca-terminal` | The same in a fresh Terminal-window zsh |
| `ca-bundles` | `check_node_ca.py`: every bundle a shell file assigns to the variable must be in the file both shells export (two tool-managed blocks can each set their own; the later one wins). Paths and certificate counts only. Exit 0 pass, 1 fail, 3 n.a. |
| `tls-proxy-env` | `NODE_TLS_REJECT_UNAUTHORIZED`, and whether each of the four proxy variables is set |
| `npm-config-ping` | The real check, in a fresh Terminal-window shell opened outside the repo (as in audit §5): npm's own `ca`, `cafile`, `strict-ssl`, `registry`, `proxy` and `https-proxy`, then one `npm ping` |
| `ca-direct-probe` | On request only, when the `ca`/`cafile` row below sends you there: Node fetches the npm registry directly, in the same kind of fresh shell, and prints the HTTP status or the error code. `--section 6` skips it; run it with `--check ca-direct-probe` |

Read the output against these rows:

| Result | Meaning |
|--------|---------|
| `check_node_ca.py` prints `N.A.` (exit 3) | No zsh startup file assigns `NODE_EXTRA_CA_CERTS` and no shell exports it. On a plain workstation that needs no corporate CA, record n.a.; on a managed one it's a **Fail**: the CA isn't set up at all |
| `check_node_ca.py` prints any `FAIL:` line | **Fail**, even if `npm ping` passes (a registry with a public certificate doesn't need the corporate CA). Most often `<bundle>: N of its M certs aren't in the exported file`: two blocks set the variable and the later one wins. "can't fully parse" usually means two bundles were joined without a newline between them. "exports nothing", "colon-separated" and "different files" are the rows below; "didn't run" / "no zsh ran" means zsh is missing or a shell didn't finish within two minutes (for example a background job from a startup file holding its output open). For both the two-blocks and the joined-bundles case, the fix is [DES: Node TLS errors behind a corporate CA](../../../docs/guides/dev-environment-setup.md#node-tls-errors-behind-a-corporate-ca-node_extra_ca_certs) |
| `check_node_ca.py` prints `PASS`; both values are the same single existing file; `TLS_REJECT` empty or anything but `0`; `ca=null`, `cafile=null`, `strict-ssl=true`, an `https://` registry; `npm ping` prints `PONG` (or an HTTP code such as `E404`) with no warning; run on the managed network | Pass. Record the network ("on VPN", "office"). Off the managed network the inspecting proxy isn't in the path, so the corporate CA wasn't exercised: record **inconclusive (off network)** instead. A macOS system proxy or PAC file is invisible to npm and Node, so if inspection only happens through one, this check can't see it: note that |
| `registry=set (credentials hidden)` | Read the registry's scheme from `npm ping`'s `PING <url>` line (redacted): `https://` can satisfy the Pass row, `http://` is the next row |
| `strict-ssl=false`, or an `http://` registry | **Inconclusive**: npm doesn't check certificates, so `PONG` proves nothing about the CA |
| `TLS_REJECT=0` | **Fail**: npm still verifies, but `sf` and other Node processes don't. Remove the variable |
| A value contains `:` | Fail: a colon-joined list, so Node loads none of it |
| The two values differ | Fail: a later block overrides the export in one shell type |
| Empty in the non-interactive check only | Fail: the export lives in `~/.zprofile` or `~/.zshrc`, so non-interactive tools don't get it |
| `ca` or `cafile` is set | npm uses only that trust store, so `PONG` verifies npm's trust, not `NODE_EXTRA_CA_CERTS`. If the workstation has no explicit proxy (all four proxy variables above empty, npm's `proxy`/`https-proxy` null; npm also uses `HTTP_PROXY`/`http_proxy` for HTTPS), run the `ca-direct-probe` check on the managed network (it uses a fresh shell, not the agent's own, which can carry an older value). **Pass** if it prints an HTTP status and the other Pass conditions hold; **Fail** on a certificate code. Otherwise **Inconclusive (`cafile` set; `NODE_EXTRA_CA_CERTS` unverified)** |
| `Warning: Ignoring extra certs from …` | Fail: the path is wrong, it isn't a single file, or two bundles were joined without a newline (`bad end line`), even if `PONG` follows |
| `npm error code` with a certificate code (`UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, `UNABLE_TO_VERIFY_LEAF_SIGNATURE`, `SELF_SIGNED_CERT_IN_CHAIN`, `DEPTH_ZERO_SELF_SIGNED_CERT`, …) | On the managed network, **Fail**: npm and Node don't trust the corporate CA. The file lacks the right certificate, or the variable isn't set in that shell (or npm's `ca`/`cafile`, if set, lacks it). Off the managed network, a captive portal or other proxy can cause this too: **inconclusive (off network)** |
| `CERT_HAS_EXPIRED` / `CERT_NOT_YET_VALID`, or `ERR_TLS_CERT_ALTNAME_INVALID` | Fail, but not fixed by adding a CA: a stale bundle or the system clock, or a hostname mismatch |
| Any other code (`ECONNREFUSED`, `ECONNRESET`, `ENETUNREACH`, `ENOTFOUND`, `ETIMEDOUT`, …) | **Inconclusive**: a network or proxy problem, not a CA verdict. Record it with the code |

If several rows match, **Fail** wins over **Inconclusive**, and both win over Pass.

Empty in both is a **pass** (or n.a.) only on a workstation that needs no extra
CA, shown by every other Pass condition holding, the managed network included.
`npm ping` makes one attempt, but a silently dropped connection
can still take over a minute: let it finish and record the code. Fixes:
[DES: Node TLS errors behind a corporate CA](../../../docs/guides/dev-environment-setup.md#node-tls-errors-behind-a-corporate-ca-node_extra_ca_certs).

## Report format

One row per check: `check | pass/fail/inconclusive/n.a. | evidence`. Give an
inconclusive result its reason, for example "inconclusive (ETIMEDOUT); CA
unverified" or "inconclusive (strict-ssl=false)". End with the proposed
fixes, each linked to its guide section, and anything you could not check. For a
multi-workstation round, use the report in
[`verification-handoff.md`](verification-handoff.md).
