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
> install steps (Homebrew, git, nvm, pyenv), follow the README's
> *macOS Environment Setup* (Steps 1–11). This doc describes the **target
> architecture** and **ongoing maintenance** once those are in place.

---

## 1. Toolchain inventory

| Tool | Installer | Purpose | Pin strategy |
|------|-----------|---------|--------------|
| **Homebrew** | macOS pkg installer (one-time) | Package manager for everything below | latest |
| **direnv** | `brew install direnv` | Per-project env activation on `cd` | latest |
| **nvm** | `brew install nvm` | Node version manager | latest |
| **Node.js** | `nvm install --lts` | JavaScript runtime for `sf` CLI | major LTS line (`lts/*`) |
| **pyenv** | `brew install pyenv` | Python version manager | latest |
| **Python** | `pyenv install 3.13.x` | Runtime for CumulusCI + scripts | major.minor line (`3.13`) |
| **pipx** | `$(pyenv prefix)/bin/python3 -m pip install --user pipx` | Isolated CLI installs (CCI) | latest |
| **CumulusCI** | `pipx install cumulusci --python "$(pyenv prefix)/bin/python3"` | Orchestration engine | latest; ensure `setuptools>=75.4,<77` (snowfakery 4.x requirement) |
| **Salesforce CLI (`sf`)** | `npm install -g @salesforce/cli` | Salesforce metadata + data | latest (built-in auto-updater) |
| **SFDMU plugin** | `sf plugins install sfdmu` | Bulk data import/export | v5+ required (enforced by `cci task run validate_setup`) |
| **gh, git, GCM** | `brew install gh git git-credential-manager` | Source control + PR workflow | latest |

**Pin philosophy:**
- **Major line, not minor.** Patch versions move forward automatically. Bumping
  a major line (Python 3.13 → 3.14, Node 24 → 26) is a deliberate, tested
  change tracked in `scripts/bash/update-toolchain.sh`.
- **pyenv and nvm are version managers, not version pickers.** Let them
  resolve the latest installed patch via `pyenv latest 3.13` and `nvm use lts/*`.

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
```

### Shell config responsibilities

Each file does one job. No duplication.

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
export NVM_DIR="$HOME/.nvm"
_NVM_PREFIX="$(brew --prefix nvm 2>/dev/null || true)"
if [ -n "$_NVM_PREFIX" ] && [ -s "$_NVM_PREFIX/nvm.sh" ]; then
  . "$_NVM_PREFIX/nvm.sh" --no-use
  if [ -s "$NVM_DIR/alias/default" ]; then
    _NVM_DEF="$(cat "$NVM_DIR/alias/default")"
    while [ -s "$NVM_DIR/alias/$_NVM_DEF" ]; do
      _NVM_DEF="$(cat "$NVM_DIR/alias/$_NVM_DEF")"
    done
    _NVM_VER="v${_NVM_DEF#v}"
    [ -d "$NVM_DIR/versions/node/$_NVM_VER/bin" ] && \
      export PATH="$NVM_DIR/versions/node/$_NVM_VER/bin:$PATH"
    unset _NVM_DEF _NVM_VER
  fi
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
Homebrew setup. `.zprofile` is reserved for login-only extras.

```sh
# Login-only PATH additions (Homebrew + nvm + pyenv all live in .zshenv).
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

# Project / org env vars (Anthropic, Vertex, etc.) go here
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
  export PYENV_VERSION="${_PY_RESOLVED:-3.13.12}"
  unset _PY_RESOLVED
  PATH_add "$(pyenv root)/shims"
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
```

### First-time activation

```bash
cd path/to/rlm-base-dev
direnv allow              # one-time per workstation per .envrc revision
```

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

1. `brew update && brew upgrade`
2. `pyenv install --skip-existing $(pyenv latest -k 3.13)` — installs newest
   patch in the pinned major.minor line, **only if** there's a newer one
3. `nvm install --lts --reinstall-packages-from=current --latest-npm` —
   keeps `sf` and other npm globals carried forward
4. `sf update` — uses the CLI's built-in updater
5. `pipx install --force cumulusci` (if Python patch bumped) **or**
   `pipx upgrade cumulusci` — required because patch upgrades break the
   venv's python symlink
6. `pipx inject --force cumulusci "setuptools>=75.4,<77"` — snowfakery 4.x
   requires modern setuptools (the historical `<71` pin documented in
   earlier guides is **incompatible** with current CCI; see README's
   *Note on setuptools*)
7. `sf plugins update`
8. `cci task run validate_setup` — verifies all 12 checks still pass

### Bumping a major line

When Python 3.14 stabilizes for CCI, or Node 26 becomes LTS:

1. Edit `PY_LINE` / `NODE_LINE` at the top of `scripts/bash/update-toolchain.sh`
2. Edit the `pyenv latest <line>` call in `.envrc`
3. Run the script. It installs the new line, reinstalls CCI under the new
   Python, and verifies via `validate_setup`.
4. Commit `.envrc` + the script changes.
5. Optionally `pyenv uninstall <old.line>.x` and `nvm uninstall <old-node>`.

---

## 5. Replicating on a new workstation

For a clean macOS workstation, in order:

1. **System bootstrap** — follow `README.md` § *macOS Environment Setup*
   Steps 1–11. That installs Homebrew, git, gh, GCM, nvm + Node LTS,
   pyenv + Python 3.13.x, pipx, CumulusCI, sf CLI, and SFDMU.
2. **Add direnv** — `brew install direnv`.
3. **Restructure shell configs** — replace `~/.zshenv`, `~/.zprofile`,
   `~/.zshrc` with the templates in §2 above. Save backups first
   (`cp ~/.zshenv ~/.zshenv.bak.$(date +%Y%m%d)` etc.).
4. **Clone and activate** —
   ```bash
   gh repo clone bgaldino/rlm-base-dev
   cd rlm-base-dev
   direnv allow
   cci task run validate_setup
   ```
5. **Restart your terminal app** (and Claude Code, IDEs) so they regenerate
   any cached shell snapshot from the new configs.

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
The CCI venv's python is a symlink to `~/.pyenv/versions/3.13.12/bin/python`.
Installing 3.13.13 doesn't replace 3.13.12, but if you uninstall the old
patch the venv dies. The update script handles this; manually:

```bash
pipx install --force cumulusci --python "$(pyenv prefix 3.13)/bin/python3"
pipx inject --force cumulusci "setuptools>=75.4,<77"
```

### `python3` resolves to `/usr/bin/python3` instead of pyenv shim
Cosmetic — `python` (no `3`) resolves correctly because the system doesn't
ship one. CCI invokes `python`, so this won't break anything. If you need
the pyenv `python3` specifically, use `pyenv exec python3`.

### `direnv` doesn't activate when cd'ing in
- Did you `direnv allow` in the project? (Run from inside the dir.)
- Is the `direnv hook zsh` line in `~/.zshrc`?
- Is your shell interactive? Non-interactive shells activate via the
  `direnv export zsh` line in `~/.zshenv` at startup, not on cd.

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
