# Developer Environment Setup

Canonical reference for setting up a local dev environment to work on
**rlm-base-dev** (and similar Salesforce / CumulusCI projects) on macOS.

This document captures **two layers**:

1. **System layer** — versioned toolchain shared across all projects on the
   workstation (Homebrew, nvm, pyenv, pipx, direnv).
2. **Project layer** — per-project pins via `.envrc`, activated automatically
   when you `cd` into the project directory.

The goal is one inventory you can share with teammates so every workstation
ends up with the same layered structure — not the same exact patch versions.

> **Audience:** new contributors bootstrapping a workstation, or existing
> contributors replicating the setup on a second machine. For the very first
> install steps (Homebrew, git, nvm, pyenv), follow the
> [local installation guide](local-installation.md#macos-environment-setup-homebrew--pyenv--nvm)
> (Steps 1–11). This doc describes the **target
> architecture** and **ongoing maintenance** once those are in place.
>
> **AI agents:** read the [toolchain skill](../../.cursor/skills/toolchain/SKILL.md)
> before auditing or changing a workstation. It covers the read-only audit, the
> safety rules, and cross-workstation verification.

---

## 1. Toolchain inventory

| Tool | Installer | Purpose | Pin strategy |
|------|-----------|---------|--------------|
| **Homebrew** | macOS pkg installer (one-time) | Package manager for everything below | latest |
| **direnv** | `brew install direnv` | Per-project env activation on `cd` | latest |
| **nvm** | `brew install nvm` | Node version manager | latest |
| **Node.js** | `nvm install --lts` | JavaScript runtime for `sf` CLI | major LTS line (`lts/*`) |
| **pyenv** | `brew install pyenv` | Python version manager | latest |
| **OpenSSL 3** | `brew install openssl@3` | TLS library the pyenv Python 3.13 builds link against | `openssl@3`; keep installed — see [OpenSSL 4 migration](#cci-breaks-after-brew-upgrade-homebrew-openssl-4-migration) |
| **Python** | `pyenv install $(pyenv latest -k 3.13)` | Runtime for CumulusCI + scripts | major.minor line (`3.13`) |
| **pipx** | `$(pyenv prefix)/bin/python3 -m pip install --user pipx` | Isolated CLI installs (CCI) | latest |
| **CumulusCI** | `pipx install cumulusci --python "$(pyenv prefix)/bin/python3"` | Orchestration engine | latest; ensure `setuptools>=75.4` (snowfakery 4.x requirement) |
| **Salesforce CLI (`sf`)** | `npm install -g @salesforce/cli` | Salesforce metadata + data | latest (built-in auto-updater) |
| **SFDMU plugin** | `sf plugins install sfdmu` | Bulk data import/export | v5.6.4+ required (enforced by `cci task run validate_setup`) |
| **Gate interpreter (`.venv`)** | `"$(pyenv prefix "$(pyenv latest 3.13)")/bin/python3" -m venv .venv` + `.venv/bin/python -m pip install $(.venv/bin/python scripts/ai/pr_gate.py --requirements --all)` (main checkout root) | Runs `scripts/ai/pr_gate.py` locally, in the loop Stop hook, and for the `validate_setup` "Gate interpreter" check | Python `3.13` (matches CI); packages from `pr_gate.py`'s `DEPS` (CumulusCI pinned to CI's version) |
| **Chrome for Testing** *(managed workstations only)* | `npx -y @puppeteer/browsers install chrome@<v>` + `chromedriver@<v>` (same version, `--path ~/.cache/cft`) | Browser for the Robot setup tasks where stock Chrome crashes on Setup pages | any CfT version, browser and driver identical; paths go in `.env.local` ([local-installation.md](local-installation.md#chrome-for-testing-managed-workstations)) |
| **gh, git, GCM** | `brew install gh git git-credential-manager` | Source control + PR workflow | latest |
| **Doc snapshot tooling** *(optional)* | `pip install -r scripts/doc_snapshot/requirements.txt && python -m playwright install chromium` (in any venv) | Refresh the Salesforce Help / Dev Guide corpus under `docs/salesforce/` (`python -m scripts.doc_snapshot`; see its [README](../../scripts/doc_snapshot/README.md)) | versions in `requirements.txt`; only needed to re-snapshot docs |

**Pin philosophy:**
- **Major line, not minor.** Patch versions move forward automatically. Bumping
  a major line (Python 3.13 → 3.14, Node 24 → 26) is a deliberate, tested
  change tracked in `scripts/bash/update-toolchain.sh`.
- **pyenv and nvm are version managers, not version pickers.** Let them
  resolve the latest installed patch via `pyenv latest 3.13` and `nvm use 'lts/*'` (quote the glob so zsh doesn't expand it).

---

## 2. System layout

```
~/.zshenv                            All zsh shells (login, interactive, scripts, Claude Code Bash)
~/.zprofile                          Login shells only
~/.zshrc                             Interactive shells only

/opt/homebrew/                       Homebrew prefix (Apple Silicon)
~/.nvm/                              nvm dir; node versions under versions/node/
~/.pyenv/                            pyenv dir; python versions under versions/
~/.local/bin/                        pipx-installed CLIs (cci, etc.)

<project>/.envrc                     direnv config — per-project pyenv + nvm pins
<project>/.venv/                     gate interpreter — Python 3.13 venv with pr_gate.py's requirements
```

`<project>/.venv` lives in the **main checkout** only. A git worktree (including
Claude Code's `.claude/worktrees/*` and the loop's `.loop/wt-*`) resolves to the
main checkout's `.venv`, so one venv serves every worktree. `scripts/ai/pr_gate.py`,
the loop Stop hook (`.claude/hooks/stop_gate.py`) and the `validate_setup` "Gate
interpreter" check all find it through `scripts/ai/gate_python.py`; set
`$RLM_GATE_PYTHON` to point them at a venv kept elsewhere. It is separate from the
pipx venv that runs `cci`: pipx's copy of CumulusCI doesn't count, because the gate
imports `cumulusci` itself. `.envrc` doesn't activate it either. It doesn't need to:
started under any `python`, `pr_gate.py` re-runs itself under the gate interpreter when
that interpreter lacks a selected check's dependency.

### Shell config responsibilities

Each file does one job. No duplication, except a line that re-asserts a setting
something later overrides: Homebrew's `brew shellenv` in `~/.zprofile` (after
macOS `path_helper`), and an export repeated after a tool-managed block that
resets it (see [the `NODE_EXTRA_CA_CERTS` entry](#node-tls-errors-behind-a-corporate-ca-node_extra_ca_certs) in §6).

The templates below show only this toolchain's lines. Your rc files may also hold
**tool-managed blocks**: sections that another tool writes and keeps up to date,
usually between marker comments such as `# >>> tool >>>` … `# <<< tool <<<` or
`# tool-managed-start` … `# tool-managed-end`. Managed workstations commonly add
them for corporate certificates, proxies, PATH entries or telemetry. Leave them
where the tool put them and don't edit inside them: the tool rewrites them on its
next update, and moving one to another file can break what it configures. Add
this toolchain's lines around them instead.

#### `~/.zshenv` — runs in **every** shell
Must be **fast** (~70ms target). No interactive features.

```sh
# Homebrew — detect prefix on Apple Silicon (/opt/homebrew) and Intel (/usr/local).
# Using `brew shellenv` here (rather than just adding bin to PATH) sets MANPATH,
# INFOPATH, and HOMEBREW_* env vars too, so later `brew --prefix nvm` works
# in non-login shells.
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

# pipx-installed CLIs
export PATH="$HOME/.local/bin:$PATH"

# NVM — function definitions + default node bin on PATH (no slow `nvm use`).
# `brew --prefix nvm` resolves to /opt/homebrew/opt/nvm (Apple Silicon)
# or /usr/local/opt/nvm (Intel) — works on both architectures.
#
# We skip the full `nvm use default` activation cycle (slow) and just resolve
# `default` to a concrete vX.Y.Z via nvm's public API, then prepend that bin
# dir. `nvm version default` handles any alias chain — including glob aliases
# like `lts/*` (which `update-toolchain.sh` and `nvm install --lts` set) —
# without depending on nvm's internal alias-cache file layout.
export NVM_DIR="$HOME/.nvm"
_NVM_PREFIX="$(brew --prefix nvm 2>/dev/null || true)"
if [ -n "$_NVM_PREFIX" ] && [ -s "$_NVM_PREFIX/nvm.sh" ]; then
  . "$_NVM_PREFIX/nvm.sh" --no-use
  _NVM_VER="$(nvm version default 2>/dev/null)"
  if [ -n "$_NVM_VER" ] && [ "$_NVM_VER" != "N/A" ] && \
     [ -d "$NVM_DIR/versions/node/$_NVM_VER/bin" ]; then
    export PATH="$NVM_DIR/versions/node/$_NVM_VER/bin:$PATH"
  fi
  unset _NVM_VER
fi
unset _NVM_PREFIX

# pyenv binary on PATH — but NO global init. Per-project init via direnv.
export PYENV_ROOT="$HOME/.pyenv"
[ -d "$PYENV_ROOT/bin" ] && export PATH="$PYENV_ROOT/bin:$PATH"

# direnv export — activates project .envrc in non-interactive shells too
command -v direnv >/dev/null 2>&1 && eval "$(direnv export zsh 2>/dev/null)"
```

#### `~/.zprofile` — runs in **login** shells only

`.zshenv` already runs for every shell (including login), so it handles
Homebrew, nvm and pyenv setup. `.zprofile` is for login-only extras, plus a
`brew shellenv` block that puts Homebrew first again: on macOS, `/etc/zprofile` runs
`path_helper` after `~/.zshenv`, and in login shells (a new Terminal window)
that moves `/usr/bin` and the other system paths ahead of everything
`~/.zshenv` prepended. On Apple silicon the Homebrew installer suggests this same
line (on Intel, `/usr/local/bin` is already in `/etc/paths`; the block is harmless
there). It puts
Homebrew first, ahead of nvm's Node and pyenv's shims as well: if Homebrew has
its own `node` or `python3` (often installed as another formula's dependency),
login shells resolve those instead. When you `cd` into the repo, `.envrc` puts
the pyenv shims and nvm's Node first again. A login shell that *starts* in the
repo (an IDE terminal opened at the repo root, a restored Terminal tab) keeps the
system order, because direnv already loaded `.envrc` from `~/.zshenv`, before
`path_helper` ran, and has nothing new to apply. Don't fix that with
`direnv reload` or by `cd`-ing out and back in: both restore the PATH direnv
recorded before `/etc/zprofile`, which drops everything `path_helper` added
(every `/etc/paths.d` entry, where managed workstations add their own, and,
depending on how the terminal was launched, `/usr/sbin` and `/sbin`) and anything
`~/.zprofile` or `~/.zshrc` added. Open the terminal outside the repo and `cd`
in, which keeps every entry and only adds the shims and moves nvm's Node first,
or use `python` (which
already resolves to the shim) or `pyenv exec python3`. Don't
keep a Homebrew `node` (see the installation guide's Step 3); for `python3`, see
[`python3` resolves to `/usr/bin/python3`](#python3-resolves-to-usrbinpython3-instead-of-pyenv-shim).

```sh
# Put Homebrew ahead of the system paths again after /etc/zprofile's path_helper.
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

# Login-only PATH additions (nvm and pyenv live in .zshenv).
export PATH="$PATH:$HOME/Library/Application Support/JetBrains/Toolbox/scripts"
```

#### `~/.zshrc` — runs in **interactive** shells only

```sh
# direnv hook: auto-reload .envrc on cd between dirs
command -v direnv >/dev/null 2>&1 && eval "$(direnv hook zsh)"

# nvm completions (interactive nicety)
_NVM_PREFIX="$(brew --prefix nvm 2>/dev/null || true)"
[ -n "$_NVM_PREFIX" ] && [ -s "$_NVM_PREFIX/etc/bash_completion.d/nvm" ] && \
  . "$_NVM_PREFIX/etc/bash_completion.d/nvm"
unset _NVM_PREFIX

# Your own interactive-only settings go here; exports that scripts, IDEs and
# Claude Code need belong in ~/.zshenv. Tool-managed blocks (see above) stay
# as the tool wrote them, before or after this.
```

### Why this layout

- **`~/.zshenv` runs for everything** — including Claude Code's Bash tool,
  IDE-spawned shells, and cron. Putting toolchain PATH here means `sf`,
  `node`, `cci`, etc. are available even in non-interactive contexts.
- **No global `pyenv init`** — that's the historical source of stale
  `.pyenv-shim` lock files when multiple shells start concurrently. direnv
  handles pyenv per-project, only where needed.
- **direnv is sourced from both `.zshenv` and `.zshrc`.**
  - `.zshenv` runs `direnv export zsh` — activates `.envrc` on shell startup
    (the only path non-interactive shells get).
  - `.zshrc` adds `direnv hook zsh` — adds a `precmd` for interactive
    auto-reload when you `cd` between projects.

---

## 3. Per-project activation (direnv `.envrc`)

Each project owns its `.envrc`. Commit it to git so teammates get the same
pins. For **rlm-base-dev** it lives at the repo root:

```sh
# .envrc

# Python via pyenv — major.minor line, auto-resolve latest patch
if command -v pyenv >/dev/null 2>&1; then
  _PY_RESOLVED="$(pyenv latest 3.13 2>/dev/null)"
  if [ -n "$_PY_RESOLVED" ]; then
    export PYENV_VERSION="$_PY_RESOLVED"
    PATH_add "$(pyenv root)/shims"
  else
    echo ".envrc: no Python 3.13.x installed via pyenv. Run scripts/bash/update-toolchain.sh or 'pyenv install \$(pyenv latest -k 3.13)' to install the latest patch." >&2
  fi
  unset _PY_RESOLVED
fi

# Node via nvm — track active LTS line. brew --prefix nvm resolves to
# /opt/homebrew/opt/nvm (Apple Silicon) or /usr/local/opt/nvm (Intel).
export NVM_DIR="$HOME/.nvm"
_NVM_PREFIX="$(brew --prefix nvm 2>/dev/null || true)"
if [ -n "$_NVM_PREFIX" ] && [ -s "$_NVM_PREFIX/nvm.sh" ]; then
  . "$_NVM_PREFIX/nvm.sh" --no-use
  nvm use --silent lts/\* >/dev/null 2>&1 || nvm use --silent default >/dev/null 2>&1
fi
unset _NVM_PREFIX

# Per-workstation overrides: values only, read as dotenv (see below).
dotenv_if_exists .env.local
```

### First-time activation

```bash
cd path/to/rlm-base-dev
direnv allow              # one-time per workstation per .envrc revision
```

Machine-specific settings (a path that differs per workstation, such as the Chrome for
Testing overrides in [local-installation.md](local-installation.md#chrome-for-testing-managed-workstations))
go in `.env.local`, which git ignores. `.envrc` loads it as dotenv, and `./tui-cci` loads the same file for variables the shell has not already set: `KEY="value"` lines with
`$VAR` expansion, and never runs it as shell. direnv doesn't ask to approve a file loaded that
way, so it holds values only: direnv keeps a `$(cmd)` as literal text and `./tui-cci` skips
that variable, so neither runs it. Quote any value
with spaces, because one unparsable line stops the whole file from loading. `.envrc` itself is
tracked, so git overwrites local edits to it, and `direnv allow` is needed again when it changes.

### Verify

```bash
python --version          # → Python 3.13.x  (whatever latest installed patch is)
pyenv version             # → 3.13.x (set by PYENV_VERSION environment variable)
node --version            # → v24.x (latest LTS)
cci --version             # → CumulusCI 4.x
sf --version              # → @salesforce/cli/2.x
```

### Adapting to another project

Copy `.envrc`, edit the python/node lines (e.g. `pyenv latest 3.12` if the
project still needs 3.12), `direnv allow`. The system layer doesn't change.

---

## 4. Maintaining the toolchain

### Update routine

```bash
cd rlm-base-dev
scripts/bash/update-toolchain.sh
```

The script handles:

1. `brew update`, then `brew upgrade` once `openssl@3` is installed and
   marked installed on request (see [OpenSSL 4 migration](#cci-breaks-after-brew-upgrade-homebrew-openssl-4-migration))
2. `pyenv install --skip-existing $(pyenv latest -k 3.13)` — installs newest
   patch in the pinned major.minor line, **only if** there's a newer one —
   then stops, before touching Node, if that Python can't import `ssl`
3. `nvm install 'lts/*' --reinstall-packages-from=current --latest-npm` —
   keeps `sf` and other npm globals carried forward
4. `sf update` — uses the CLI's built-in updater
5. `pipx install --force cumulusci` (if Python patch bumped) **or**
   `pipx upgrade cumulusci` — required because patch upgrades break the
   venv's python symlink
6. `pipx inject --force cumulusci "setuptools>=75.4"` — snowfakery 4.x
   requires modern setuptools. The historical `<71` pin (older docs)
   is **incompatible**; see the [local installation guide](local-installation.md#step-7--install-cumulusci), *Note on setuptools*. Note CI
   (`.github/workflows/prepare-rlm-org.yml`) installs the same
   `setuptools>=75.4` with no upper bound, now that it pins CCI 4.10.1.
7. `sf plugins update`
8. Gate interpreter — if `<main checkout>/.venv` exists, rebuilds it with
   `python -m venv --clear` when its Python isn't the current 3.13 patch (a
   patch bump breaks its python symlink the same way as the pipx venv). Before
   clearing, `gate_python.py --carry-over` lists the venv's top-level packages (the
   doc snapshot tooling, Robot requirements, editable installs, …), reading
   site-packages directly so it works when the venv's Python is already gone. They
   are reinstalled afterwards, one at a time if the batch fails, and a pin that
   won't install on the new Python is retried unpinned. Anything that still can't
   come back is named in a warning, and the list is kept. If the packages can't be
   listed while the old Python still runs, the venv is left on its old patch with a
   warning rather than cleared (rerun once the cause is fixed); it is rebuilt anyway
   only when that Python is already gone. Then it reinstalls
   `pr_gate.py --requirements --all`.
   A `$RLM_GATE_PYTHON` override is probed but not managed. If the install fails,
   or `gate_python.py` still finds the gate interpreter unusable, the script exits
   nonzero after `validate_setup` (which only warns about it)
9. `cci task run validate_setup` — verifies every check still passes,
   including the "Gate interpreter" warning check

**When `DEPS` in `scripts/ai/pr_gate.py` changes** (a check gains a new
package, or the CumulusCI pin moves), the gate interpreter needs the new
requirements. Rerun the script, or just the install step:

```bash
.venv/bin/python -m pip install $(.venv/bin/python scripts/ai/pr_gate.py --requirements --all)
python3 scripts/ai/gate_python.py      # prints the interpreter; exit 1 names what's missing
```

### Bumping a major line

When Python 3.14 stabilizes for CCI, or Node 26 becomes LTS:

1. Edit `PY_LINE` / `NODE_LINE` at the top of `scripts/bash/update-toolchain.sh`
2. Edit the `pyenv latest <line>` call in `.envrc`
3. Run the script. It installs the new line, reinstalls CCI under the new
   Python, rebuilds the gate interpreter `.venv` on it, and verifies via
   `validate_setup`.
4. Commit `.envrc` + the script changes.
5. Optionally `pyenv uninstall <old.line>.x` and `nvm uninstall <old-node>`.

---

## 5. Replicating on a new workstation

For a clean macOS workstation, in order:

1. **System bootstrap** — follow the [local installation guide](local-installation.md#macos-environment-setup-homebrew--pyenv--nvm), *macOS Environment Setup*,
   Steps 1–11. That installs Homebrew, git, gh, GCM, nvm + Node LTS,
   pyenv + Python 3.13.x, the gate interpreter `.venv` (Step 6), pipx,
   CumulusCI, sf CLI, and SFDMU.
2. **Add direnv** — `brew install direnv`.
3. **Restructure shell configs** — merge the templates in §2 into `~/.zshenv`,
   `~/.zprofile` and `~/.zshrc`. Don't replace the files wholesale.
   1. Save backups first (`cp ~/.zshenv ~/.zshenv.bak.$(date +%Y%m%d)` etc.;
      skip a file that doesn't exist yet — `~/.zprofile` often doesn't on Intel).
   2. Remove what Steps 3–4 of the installation guide appended; the §2
      templates replace all of it:
      - in both `~/.zshenv` and `~/.zshrc`, the `NVM_DIR` and `PYENV_ROOT` exports, the pyenv `PATH`
        line and `eval "$(pyenv init -)"`;
      - in `~/.zshrc`, the one-line `nvm.sh` source, and the nvm
        `bash_completion` line (or keep that in place of the template's
        equivalent);
      - in `~/.zshenv`, the whole `# Bootstrap Homebrew in non-interactive
        shells` section: the `if ! command -v brew …` block and the
        `if command -v brew …` block after it that sets `NVM_PREFIX` and
        sources `nvm.sh`, through its closing `fi`.

      The ``# Created by `pipx` on <date>`` comment and the PATH line after it,
      which `pipx ensurepath` (Step 7) appends to `~/.zshrc` and/or `~/.zprofile`,
      are redundant with the `~/.zshenv` template; remove them or leave them. If you
      added the `brew shellenv` line the Homebrew installer suggests to
      `~/.zprofile`, keep it in place of the §2 `~/.zprofile` template's
      `brew shellenv` block (same effect; the template explains why it's
      needed). Without one, sub-step 3 adds the template block. Neither is a
      tool-managed block.
   3. Add the §2 template lines, and keep everything else, especially any
      **tool-managed block** (see §2), unchanged.
   4. Check with `diff ~/.zshrc ~/.zshrc.bak.<date>` (and the other two): only
      toolchain lines should differ (a file you just created has no backup to
      diff against).
4. **Clone and activate** —
   ```bash
   gh repo clone bgaldino/rlm-base-dev
   cd rlm-base-dev
   direnv allow
   # Gate interpreter (skip if you already created it in Step 6 of the installation guide)
   "$(pyenv prefix "$(pyenv latest 3.13)")/bin/python3" -m venv .venv
   .venv/bin/python -m pip install $(.venv/bin/python scripts/ai/pr_gate.py --requirements --all)
   cci task run validate_setup
   ```
5. **Restart your terminal app** (and Claude Code, IDEs) so they regenerate
   any cached shell snapshot from the new configs. Open the new window outside
   the repo, then `cd` in: a restored tab that reopens in the repo starts with
   the system PATH order (see §2, `~/.zprofile`).
6. **Managed workstation only: Chrome for Testing.** If stock Chrome can't
   drive Salesforce Setup pages on this machine, install Chrome for Testing and
   put `CHROME_BINARY` and `CHROMEDRIVER_PATH` in `.env.local` at the repo root
   (gitignored; `.envrc` and `./tui-cci` both load it), per
   [local-installation.md](local-installation.md#chrome-for-testing-managed-workstations).
   Don't put them in `.envrc` or your shell profile: `.envrc` is tracked, and
   `.env.local` keeps per-machine paths with the checkout they belong to. Open
   a new terminal outside the repo and `cd` in (direnv exports `.env.local` on
   entering the repo), then rerun `cci task run validate_setup`; it reports the
   overrides as
   `(from CHROME_BINARY)` and `(from CHROMEDRIVER_PATH)`.

---

## 6. Troubleshooting

### `pyenv: cannot rehash: couldn't acquire lock`
Stale shim lock from a previous interrupted rehash. Usually caused by
duplicated `eval "$(pyenv init -)"` in shell configs.

```bash
pkill -9 -f pyenv-rehash
rm -f ~/.pyenv/shims/.pyenv-shim
```

Prevented by the layout above (no global `pyenv init`).

### `cci` not found in Claude Code Bash tool
Claude Code captures a shell snapshot at startup. If it was launched from
Spotlight/Dock (minimal PATH), the snapshot misses your shell config. Fix:
launch Claude Code from a terminal, **or** restart Claude Code after
fixing `~/.zshenv`.

### `pipx` venv broken after Python patch bump
The CCI venv's python is a symlink to a specific pyenv patch dir
(`~/.pyenv/versions/<old-patch>/bin/python3`). Installing a newer patch
doesn't replace the old one, but if you uninstall the old patch the venv
dies. The update script handles this; manually:

```bash
# Refresh pipx under the new patch (in case pipx's own shebang was tied
# to the old patch), then reinstall CCI under it.
"$(pyenv prefix "$(pyenv latest 3.13)")/bin/python3" -m pip install --user --upgrade pipx
pipx install --force cumulusci --python "$(pyenv prefix "$(pyenv latest 3.13)")/bin/python3"
pipx inject --force cumulusci "setuptools>=75.4"
```

### `cci` breaks after `brew upgrade` (Homebrew OpenSSL 4 migration)
Symptom — after `brew upgrade` (or `scripts/bash/update-toolchain.sh`, which
runs it), every `cci` command dies at startup:

```
ImportError: dlopen(.../lib-dynload/_ssl.cpython-313-darwin.so, 0x0002):
Library not loaded: /opt/homebrew/opt/openssl@3/lib/libssl.3.dylib
```

Cause — Homebrew is migrating formulae to OpenSSL 4
([Homebrew/homebrew-core#278366](https://github.com/Homebrew/homebrew-core/issues/278366)).
`openssl@4` is now the default `openssl`, `openssl@3` is keg-only, and the
`pyenv` formula depends on `openssl@4`. A pyenv Python 3.13 built earlier
still links `/opt/homebrew/opt/openssl@3`, but Homebrew doesn't know that,
so once nothing it tracks needs `openssl@3`, `brew upgrade`'s automatic
cleanup/autoremove deletes it. CumulusCI imports `ssl` at startup, so `cci`
breaks before any task runs. (`validate_setup` can't detect it for the
same reason.)

Fix — reinstall it explicitly:

```bash
brew install openssl@3
brew tab --installed-on-request openssl@3
```

The second line marks `openssl@3` *installed on request* even when it was
already present as a dependency, so autoremove keeps it from then on.
`scripts/bash/update-toolchain.sh` runs both before `brew upgrade`. If the
target Python still can't import `ssl` after that, the script stops with
Python's own error and a `pyenv install --force <version>` hint: with
`openssl@3` present, that Python was built against another OpenSSL or its
install is broken. Confirm with
`brew info openssl@3` (shows `Installed (on request)`) and `cci version`.

Why not rebuild on OpenSSL 4 — the toolchain can't move yet. CumulusCI 4.10.1
requires Python `<3.14`, and CPython 3.13 does not support OpenSSL 4 (support
landed in 3.14.6+ and 3.15). Keep `openssl@3` installed until the Python line
moves past 3.13 (see [Bumping a major line](#bumping-a-major-line)). The
Docker image (`python:3.13-slim-bookworm`) uses Debian's OpenSSL and is
unaffected.

### `pr_gate.py` reports `MISSING-DEP`, or `validate_setup` warns "Gate interpreter"
The gate interpreter (`<main checkout>/.venv`, see §2) is missing, is on the
wrong Python, or lacks a package that `pr_gate.py`'s `DEPS` now lists. A common
case: the venv predates a new dependency (CumulusCI was added for the
`doc_build_steps` check, so any `.md` change hits it). `gate_python.py` names
the problem:

```bash
python3 scripts/ai/gate_python.py
```

From the main checkout root, install what's missing, or rebuild the venv if its
Python is wrong or its symlink is broken:

```bash
.venv/bin/python -m pip install $(.venv/bin/python scripts/ai/pr_gate.py --requirements --all)
```

```bash
python3 scripts/ai/gate_python.py --carry-over .venv > /tmp/gate-venv-packages.txt   # works with its python broken
"$(pyenv prefix "$(pyenv latest 3.13)")/bin/python3" -m venv --clear .venv
.venv/bin/python -m pip install -r /tmp/gate-venv-packages.txt
```

`--clear` empties the whole venv, so the `--carry-over` list (its top-level
packages, pinned, plus editable and VCS installs) is how anything else you
installed there comes back. After a rebuild, run the install command again.
`scripts/bash/update-toolchain.sh` does all of this, and installs package by
package when the list won't install in one go.

### `python3` resolves to `/usr/bin/python3` instead of pyenv shim
Cause — outside the repo this is by design: there's no global `pyenv init`, so
no pyenv shim is on PATH. Inside the repo it happens in a login shell that
*started* there: direnv added the shims from `~/.zshenv`, then macOS
`path_helper` (run from `/etc/zprofile`) moved `/usr/bin` ahead of them, and the
`brew shellenv` block in `~/.zprofile` put Homebrew first, so a Homebrew
`python3` (`/opt/homebrew/bin/python3`) can win the same way (see §2,
`~/.zprofile`). Open a terminal outside the repo and `cd` in instead; don't use
`direnv reload` or `cd` out and back in here, for the reason in §2 (`~/.zprofile`): it drops system and
managed PATH entries. Cosmetic — `python` (no `3`) resolves correctly because the system doesn't
ship one. CCI invokes `python`, so this won't break anything. If you need
the pyenv `python3` specifically, use `pyenv exec python3`.

### Node TLS errors behind a corporate CA (`NODE_EXTRA_CA_CERTS`)
Symptom: `npm` or `sf` fail with `UNABLE_TO_GET_ISSUER_CERT_LOCALLY` or
`SELF_SIGNED_CERT_IN_CHAIN`, or Node prints `Warning: Ignoring extra certs from
… load failed`.

`NODE_EXTRA_CA_CERTS` applies only to Node.js processes. `nvm install`
downloads Node, and the version index it resolves versions from, with `curl`
(or `wget` if `curl` is missing), and neither reads it. nvm fetches that index
silently, so a certificate problem shows only as a version that isn't found:
``Version '' (with LTS filter) not found - try `nvm ls-remote --lts` …`` for
`lts/*` (what `update-toolchain.sh` installs), or
``Version '24' not found - try `nvm ls-remote` …`` for an explicit version
such as `24` (nvm prints the version as you typed it).
To see the real error, run `curl -sSI https://nodejs.org/dist/index.tab`.

For nvm's downloads, fix the trust for `curl` (`CURL_CA_BUNDLE`; nvm runs curl with `-q`,
so `~/.curlrc` is ignored) or `wget` (`ca_certificate` in `~/.wgetrc`), not
`NODE_EXTRA_CA_CERTS`. Unlike `NODE_EXTRA_CA_CERTS`, those two *replace* the
default trust rather than adding to it, so point them at a full bundle (for
example a copy of `/etc/ssl/cert.pem` with your corporate CAs appended), not at
the Node extras file below. The npm steps that run under the new Node afterwards
(`--reinstall-packages-from`, `--latest-npm`) do use `NODE_EXTRA_CA_CERTS`.

`NODE_EXTRA_CA_CERTS` takes **one** PEM file. A colon-separated list of files is
treated as a single path that doesn't exist: Node warns (only once it opens its
first TLS connection) and loads none of them. If your workstation provides more
than one bundle, combine them into a single file and point the variable at that:

```bash
mkdir -p ~/.config/certs
# awk 1 ends every file with a newline; a plain cat can join two certificates on
# one line, and OpenSSL then skips the second without an error.
awk 1 /path/to/first-bundle.pem /path/to/second-bundle.pem > ~/.config/certs/node-extra-ca.pem
```

Put `export NODE_EXTRA_CA_CERTS="$HOME/.config/certs/node-extra-ca.pem"` in
`~/.zshenv`, so non-interactive shells (Claude Code, IDEs, tools that launch `sf`)
get it too. If a tool-managed block (see §2) in any of the three files sets the
variable after your export, it overrides it: in every shell for a block in
`~/.zshenv`, in login shells (every new Terminal window) for one in
`~/.zprofile`, and in interactive shells for one in `~/.zshrc`. Repeat the
export after that block. Rebuild the combined file whenever a source bundle
changes, and check both kinds of shell from a clean environment (without
`env -i`, the check inherits the value your current terminal already exported):

```bash
env -i HOME="$HOME" zsh -c   'echo $NODE_EXTRA_CA_CERTS'   # non-interactive (Claude Code, IDE tasks)
env -i HOME="$HOME" zsh -lic 'echo $NODE_EXTRA_CA_CERTS'   # login + interactive (a Terminal window)
```

Then verify with a TLS request from a new terminal (an open one still has the
old value), which surfaces the warning:

```bash
node -e 'const q = require("https").get("https://registry.npmjs.org/", r => { console.log(r.statusCode); process.exit(0) }); q.on("error", e => { console.log(e.code || e.message); process.exit(1) }); q.setTimeout(15000, () => { console.log("timeout"); process.exit(2) })'
```

It prints the status code and exits, or prints `timeout` after 15 seconds
(`process.exit`: without it, Node keeps the connection open and the command
doesn't return).

This plain `https.get` doesn't use `HTTPS_PROXY`, so behind an explicit proxy a
timeout here says nothing about the CA setup; check for the warning instead.

### `direnv` doesn't activate when cd'ing in
- Did you `direnv allow` in the project? (Run from inside the dir.)
- Is the `direnv hook zsh` line in `~/.zshrc`?
- Is your shell interactive? Non-interactive shells activate via the
  `direnv export zsh` line in `~/.zshenv` at startup, not on cd.

### `INVALID_AUTH_HEADER` / "Expired session" on `cci org info` or scratch creation
Symptom — a freshly created scratch org immediately fails, with a URL that
ends in a redacted placeholder, e.g.:

```
Error: Expired session for https://...my.salesforce.com/services/data/v68.0/
sobjects/Organization/[REDACTED] Use 'sf org auth show-access-token' to view.
[{'message': 'INVALID_AUTH_HEADER', 'errorCode': 'INVALID_AUTH_HEADER'}]
```

Cause — the May 2026 Salesforce CLI security change
([forcedotcom/cli#3560](https://github.com/forcedotcom/cli/issues/3560))
redacts access tokens from the `--json` output of `org create scratch`,
`org display`, `org list`, and the `org login *` commands. CumulusCI 4.10.0
and earlier parse those outputs for the token, so it grabs the literal
`[REDACTED] Use 'sf org auth show-access-token' to view.` string and sends it
as the auth header. It is **not** a real expired session or an org problem.

Fix — upgrade CumulusCI to 4.10.1 or later, which falls back to
`sf org auth show-access-token` when the token is redacted:

```bash
pipx upgrade cumulusci && cci version   # expect 4.10.1+
```

If your pipx CumulusCI was built on Python 3.10, `pipx upgrade` can't install 4.10.1
(it needs Python 3.11–3.13); rebuild it on a supported interpreter with
`pipx reinstall cumulusci --python "$(pyenv prefix)/bin/python3"` or
`scripts/bash/update-toolchain.sh`.

CI (`.github/workflows/prepare-rlm-org.yml`) pins 4.10.1. The repo no longer
exports the old `SF_TEMP_SHOW_SECRETS=true` shim for CumulusCI (a few scripts
still set it on their own `sf` calls); if you added it to `~/.zshenv`
or a LaunchAgent, remove it (see
[cci-sf-cli-token-workaround.md](cci-sf-cli-token-workaround.md)).

---

## 7. Reference

- Before editing shell configs, always save a dated backup:
  `cp ~/.zshenv ~/.zshenv.bak.$(date +%Y%m%d)` (repeat for `~/.zshrc`, `~/.zprofile`)
- Update script: `scripts/bash/update-toolchain.sh`
- Project .envrc: `.envrc` at repo root
- Validation: `cci task run validate_setup` (no org required)
- direnv docs: https://direnv.net/
- pyenv docs: https://github.com/pyenv/pyenv
- nvm docs: https://github.com/nvm-sh/nvm
