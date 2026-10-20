# Local Installation

[Home](../../README.md) · [Documentation](../index.md) · [Org operations](org-operations.md)

Install the local toolchain and authenticate before running Salesforce workflows.
Before cloning, run the bootstrap commands from your chosen workspace directory.
After cloning, run commands from the repository root unless a step says otherwise.
For a containerized toolchain, use the [Docker guide](../../docker/README.md).

> **Pasting commands into an interactive zsh?** Run `setopt interactivecomments`
> first. Without it zsh treats `#` as a command, so a comment line can run or
> swallow the commands after it.

- [macOS bootstrap](#macos-environment-setup-homebrew--pyenv--nvm)
- [Required software and Salesforce access](#prerequisites)
- [Installation and headless browser setup](#installation)

## macOS Environment Setup (Homebrew + pyenv + nvm)

> **Cursor users:** Open this guide in [Cursor](https://www.cursor.com/), press `Cmd+L` to open the AI chat, and paste: *"Walk me through the macOS Environment Setup section of this guide, running each command in the terminal."* The agent can execute each step interactively. Run the steps in order — each one builds on the previous.

> **For the layered/canonical view** (shell config architecture, per-project
> `.envrc` activation via direnv, major-line pin strategy, and the
> `scripts/bash/update-toolchain.sh` maintenance routine), see
> [`docs/guides/dev-environment-setup.md`](dev-environment-setup.md).
> Steps 1–11 below are the first-time bootstrap; the guide describes the
> target architecture and ongoing maintenance you'll move to after that.

This section walks through a full, clean environment setup on macOS using [Homebrew](https://brew.sh/) for package management, [pyenv](https://github.com/pyenv/pyenv) for Python version management, and [nvm](https://github.com/nvm-sh/nvm) for Node.js version management. Using version managers (pyenv + nvm) keeps your tool installations isolated from the macOS system Python and Node, avoiding conflicts when multiple projects need different versions. Skip any step for tools you already have installed.

### Step 1 — Install Homebrew

If you don't have Homebrew installed, run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the post-install instructions to add Homebrew to your `PATH` (shown at the end of the installer output). Then verify:

```bash
brew --version
```

### Step 2 — Install core tools (git, gh, GCM)

```bash
# Install git (version control)
brew install git

# Install GitHub CLI (gh) — used for PR workflows, cloning private repos, etc.
brew install gh

# Install Git Credential Manager (recommended) — secure credential storage for HTTPS git operations
brew install --cask git-credential-manager
```

Verify and authenticate:

```bash
git --version
gh --version

# Authenticate with GitHub (if you haven't already)
gh auth login
```

### Step 3 — Install Node.js via nvm

[nvm](https://github.com/nvm-sh/nvm) (Node Version Manager) lets you install and switch between Node.js versions without touching the system Node. This is the recommended approach if you manage multiple projects — it prevents conflicts between the sf CLI's Node dependency and any other Node-based tools on your system.

> **Why nvm over `brew install node`?** Homebrew installs a single Node version system-wide. nvm lets you pin projects to specific Node versions and keeps global npm packages (like `@salesforce/cli`) tied to the version they were installed with.
>
> **Node.js 24, the line pinned in `.nvmrc`:** the repo's `.envrc` selects it with a bare `nvm use` (with Homebrew's nvm, or one from nvm's own installer in `$NVM_DIR` or `$XDG_CONFIG_HOME/nvm`), `package.json` declares `engines.node: >=24`, and the Docker image and the build workflow use Node 24 too. The line moves only by a deliberate change to `.nvmrc` (see [Bumping a major line](dev-environment-setup.md#bumping-a-major-line)).

```bash
# Install nvm via Homebrew, and create the directory nvm keeps Node versions in
brew install nvm
mkdir -p ~/.nvm
```

nvm is a shell function, so a startup file has to load it in every shell, including the
non-interactive ones that IDE tasks, scripts and Claude Code's Bash tool start. Don't
`echo` lines of your own into `~/.zshenv` or `~/.zshrc`: copy them from the templates in
[dev-environment-setup.md §2](dev-environment-setup.md#shell-config-responsibilities).
Their `~/.zshenv` NVM block loads nvm without switching Node (`--no-use`), puts nvm's
`default` Node first, and in a shell started from the repo keeps the repo's Node instead.

1. Back up the two files (one that doesn't exist yet is skipped):

   ```bash
   for f in ~/.zshenv ~/.zshrc; do [ -f "$f" ] && cp "$f" "$f.bak.$(date +%Y%m%d)"; done
   ```

2. In `~/.zshenv`, add two blocks from the
   [`~/.zshenv` template](dev-environment-setup.md#zshenv--runs-in-every-shell), in this
   order: the Homebrew block at its top (`if [ -x /opt/homebrew/bin/brew ]` through its
   `fi`; skip it if `~/.zshenv` already runs `brew shellenv`), then the NVM block
   (`# NVM —` through the `unset _NVM_PREFIX …` line). The NVM block finds Homebrew's nvm
   through `brew`, so the Homebrew block has to come first. Lines you merge later go where
   the template has them: the pipx `~/.local/bin` line goes between these two blocks,
   because the NVM block keeps nvm's Node ahead of anything prepended before it, not after.
3. In `~/.zshrc`, add the nvm completion lines from the
   [`~/.zshrc` template](dev-environment-setup.md#zshrc--runs-in-interactive-shells-only)
   (`# nvm completions` through `unset _NVM_PREFIX`). `~/.zshrc` needs nothing else for
   nvm: `~/.zshenv` already runs for interactive shells.

Copy the lines exactly, and add them around any tool-managed block rather than inside it.
The rest of the templates gets merged after the bootstrap, in
[dev-environment-setup.md §5](dev-environment-setup.md#5-replicating-on-a-new-workstation),
step 3.

> **Set up from an earlier version of this step?** It appended its own nvm lines to both
> files: in `~/.zshrc` an `NVM_DIR` export, an `nvm.sh` source line and a completion line,
> and in `~/.zshenv` an `NVM_DIR` export and a `# Bootstrap Homebrew in non-interactive
> shells` section. Those load nvm with its auto-use, which slows every shell, and an
> interactive shell loads it twice, putting nvm's Node on PATH twice. Remove them (the
> nvm items in [§5, step 3](dev-environment-setup.md#5-replicating-on-a-new-workstation)'s
> list; leave the pyenv lines until that merge), then add the blocks above.

```bash
# Load the new ~/.zshenv into this shell
source ~/.zshenv

# Install the repo's Node line (the major in .nvmrc) — the newest 24.x
nvm install 24

# Make it the default for all new shells
nvm alias default 24

# Verify
# Should show v24.x
node --version
npm --version
```

> **After setup, restart your terminal** (or any IDE/tool that spawns shells) so the updated PATH takes effect in all contexts.

If you already have `brew install node` and want to migrate to nvm, remove the Homebrew version after installing nvm — it is no longer needed:
```bash
# safe after nvm is installed and default is set
brew uninstall node
```

### Step 4 — Install pyenv and Python

[pyenv](https://github.com/pyenv/pyenv) lets you install and switch between Python versions without touching the system Python.

**Python 3.12 or 3.13 is recommended for CumulusCI** — both are stable and tested with CCI 4.x. Python 3.14 is very new (released October 2025) and has known dependency compatibility issues. Avoid it for CCI.

```bash
# Install pyenv, plus OpenSSL 3 for the Python 3.13 build (see the note below)
brew install pyenv openssl@3
```

Homebrew's pyenv is already on PATH, so it can install Python without any shell setup.
What pyenv adds to a shell is its shims, which make `python` resolve to a pyenv version,
and those come per project: the repo's `.envrc` puts them on PATH through
[direnv](dev-environment-setup.md#3-per-project-activation-direnv-envrc), set up in
[dev-environment-setup.md §5](dev-environment-setup.md#5-replicating-on-a-new-workstation).
Don't `echo` pyenv lines of your own into `~/.zshenv` or `~/.zshrc`, and don't add
`eval "$(pyenv init -)"` to either: a global `pyenv init` is the historical cause of stale
`.pyenv-shim` locks when several shells start at once
([pyenv rehash lock errors](dev-environment-setup.md#pyenv-cannot-rehash-couldnt-acquire-lock)),
and in both files it runs twice in every interactive shell.

In `~/.zshenv` (Step 3 backed it up), add the pyenv block from the
[`~/.zshenv` template](dev-environment-setup.md#zshenv--runs-in-every-shell)
(`# pyenv binary on PATH` through the `[ -d "$PYENV_ROOT/bin" ] …` line) after the NVM
block, where the template has it. It sets `PYENV_ROOT` and puts only pyenv's own `bin` on
PATH, for a pyenv installed from git rather than Homebrew; it has no `pyenv init`. Copy the
lines exactly, and add them around any tool-managed block rather than inside it.
`~/.zshrc` needs nothing for pyenv.

> **Set up from an earlier version of this step?** It appended three lines to both
> `~/.zshrc` and `~/.zshenv`: an `export PYENV_ROOT="$HOME/.pyenv"`, a
> `[[ -d $PYENV_ROOT/bin ]] && export PATH=…` line and `eval "$(pyenv init -)"`, so every
> interactive shell ran `pyenv init` twice. Remove all six (the pyenv items in
> [§5, step 3](dev-environment-setup.md#5-replicating-on-a-new-workstation)'s list), then
> add the block above. `python` then resolves to pyenv's only in the repo, once direnv is set
> up; outside it, that's by design (see
> [`python3` resolves to `/usr/bin/python3`](dev-environment-setup.md#python3-resolves-to-usrbinpython3-instead-of-pyenv-shim)).

```bash
# Load the new ~/.zshenv into this shell
source ~/.zshenv

# Install the latest 3.13.x patch automatically
PYTHON_VERSION=$(pyenv install --list | grep -E "^[[:space:]]*3\.13\.[0-9]+$" | tail -1 | tr -d '[:space:]')
pyenv install "$PYTHON_VERSION"
pyenv global "$PYTHON_VERSION"

# Verify
# Should show the latest 3.13.x patch. With no global pyenv init, `pyenv exec` runs the
# Python pyenv selects; a bare `python` resolves to it only in the repo, through .envrc.
pyenv exec python --version
```

> **`pyenv global` is the Python pyenv selects outside a project that pins its own:** what `pyenv exec` and `pyenv prefix` resolve to there, and what Step 7 builds pipx and CumulusCI on. `scripts/bash/update-toolchain.sh` moves it to each new 3.13 patch, but only when the old one holds no packages you pip-installed straight into it; otherwise it warns and leaves it. Prefer pipx or a virtualenv for tools, so that move stays automatic ([dev-environment-setup.md §4](dev-environment-setup.md#update-routine)).

> **Keep `openssl@3` installed.** Python 3.13 needs OpenSSL 3, but Homebrew is migrating to OpenSSL 4: plain `openssl` is now OpenSSL 4 and `pyenv` depends on it. Install `openssl@3` before `pyenv install` (the 3.13 build definition prefers it and otherwise falls back to Homebrew's default `openssl`), and leave it installed. Installing it by name marks it *installed on request*, so `brew upgrade` won't remove it later — if it does go missing, `cci` fails at startup with `Library not loaded: /opt/homebrew/opt/openssl@3/lib/libssl.3.dylib`. See [the troubleshooting entry](dev-environment-setup.md#cci-breaks-after-brew-upgrade-homebrew-openssl-4-migration) for the cause and why the toolchain can't move to OpenSSL 4 yet.

> **Using multiple Python versions?** You can install additional versions alongside (for example, another 3.12.x or 3.13.x patch) and switch per-project with a `.python-version` file. Keep whichever version you use for CCI consistent with what you pass to `pipx install cumulusci --python`.

### Step 5 — Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

> Replace `<repository-url>` with the actual repo URL from GitHub (use `gh repo clone <org>/<repo>` if you used `gh auth login` above).

### Step 6 — Create and activate a virtual environment (venv)

From the repository cloned in Step 5, create a project-specific virtual environment. This isolates the project's Python dependencies from your system and other projects.

This `.venv` is also the **gate interpreter**: the Python that runs the pre-merge gate (`scripts/ai/pr_gate.py`). The loop Stop hook (`.claude/hooks/stop_gate.py`) and the `validate_setup` "Gate interpreter" check look for it at `<main checkout>/.venv/bin/python`, and a git worktree resolves to the main checkout's `.venv`. (`$RLM_GATE_PYTHON` overrides this path if you keep the venv somewhere else.) Create it with Python 3.13, which is what CI uses, and install the gate's requirements into it:

```bash
# From the repo root. Named explicitly, so the venv is on 3.13 even if pyenv's global
# (or a .python-version) selects another version; `python` alone would use that one.
"$(pyenv prefix "$(pyenv latest 3.13)")/bin/python3" -m venv .venv

# Install everything pr_gate.py needs to run all of its checks (including cumulusci)
.venv/bin/python -m pip install $(.venv/bin/python scripts/ai/pr_gate.py --requirements --all)

# Activate the venv
source .venv/bin/activate

# Your prompt should now show (.venv) prefix
# Verify
# Python 3.13.x
python --version
pip --version
# prints the interpreter path; names anything missing
python scripts/ai/gate_python.py
```

You don't need to activate it to run the gate. `.envrc` selects the pyenv Python and doesn't activate `.venv`, so `python scripts/ai/pr_gate.py --base origin/main` starts under the pyenv Python (until direnv is set up, per [dev-environment-setup.md §5](dev-environment-setup.md#5-replicating-on-a-new-workstation), `pyenv exec python scripts/ai/pr_gate.py --base origin/main` does the same). When that interpreter lacks a selected check's dependency, the gate re-runs itself under this `.venv` (also from a git worktree) and prints a `note:` line saying so. If the venv is missing or incomplete, the note names the problem and the affected checks report `MISSING-DEP`.

> **Install the gate requirements even if you install CumulusCI via pipx (recommended, Step 7).** pipx keeps CCI in its own isolated environment, so the CCI you run day to day doesn't come from this venv. The gate does: without `cumulusci` and the other requirements here, `pr_gate.py` reports `MISSING-DEP` for a check whose dependency is absent, and a change to any `.md` file fails the gate for a setup reason. When `DEPS` in `scripts/ai/pr_gate.py` changes, rerun the install command above (`scripts/bash/update-toolchain.sh` does this for you).

To deactivate the venv when you're done:

```bash
deactivate
```

> **Tip:** Add `.venv/` to your `.gitignore` if it isn't already (this project's `.gitignore` covers it).

### Step 7 — Install CumulusCI

**Recommended: use pipx** — pipx installs CumulusCI in its own isolated Python environment, keeping it separate from your project venv and system Python.

```bash
# Install pipx via pyenv's Python — keeps all Python tooling under pyenv, not Homebrew
# Uses the pyenv global set in Step 4 ($(pyenv prefix) resolves to that version)
$(pyenv prefix)/bin/python3 -m pip install --user pipx

# Persist the pipx executable path for future shells, then update this shell too
$(pyenv prefix)/bin/python3 -m pipx ensurepath
export PATH="$HOME/.local/bin:$PATH"

# Install CumulusCI using the same Python version
pipx install cumulusci --python "$(pyenv prefix)/bin/python3"

# Verify
# Should show CumulusCI 4.x running on Python 3.13.x
cci version
```

> **Note on setuptools:** Earlier versions of this guide instructed `pipx inject cumulusci "setuptools<71"` to work around a `pkg_resources` issue in `pyfilesystem2`. This pin is **no longer needed or valid** — modern CumulusCI (4.8+) with snowfakery 4.x requires `setuptools>=75.4`, making the `<71` pin incompatible. If you have an older CCI install with the pin, remove it: `pipx inject --force cumulusci "setuptools>=75.4"`.

If you prefer to use the project venv instead (activate it first per Step 6, then):

```bash
pip install cumulusci
cci version
```

### Step 8 — Install Salesforce CLI (`sf`)

Install `@salesforce/cli` via npm using the nvm-managed Node from Step 3. This is the Salesforce-recommended installation method.

```bash
# Install sf CLI globally via npm (nvm-managed Node must be active)
npm install -g @salesforce/cli

# Verify (must be 2.x or later)
# Check CLI >=2 and Node 24 (the line pinned in .nvmrc); platform/architecture and patch versions vary
sf --version
```

> **Why npm instead of Homebrew?** The Homebrew `sf` formula and `--cask sf` cask bundle their own copy of Node.js independently of nvm. This creates redundant Node installations and potential version conflicts. Installing via npm ties sf to your nvm-managed Node version, giving you a single Node installation to manage.

> **After switching from Homebrew sf to npm:** If you previously had `brew install --cask sf` or `brew install sf`, remove it first: `brew uninstall sf`.

> **npm globals and nvm versions:** npm global packages (like `@salesforce/cli`) are installed per nvm Node version. If you switch Node versions with `nvm use`, run `npm install -g @salesforce/cli` again in the new version, or use `nvm reinstall-packages <old-version>` to copy all globals.

### Step 9 — Install SFDMU plugin (v5.6.4+)

SFDMU is a Salesforce CLI plugin for bulk data loading. **Version 5.6.4 or later is required** (5.6.4 fixed upsert matching for relationship-traversal externalIds; older 5.x releases duplicate records on rerun).

```bash
sf plugins install sfdmu

# Verify (should show 5.6.4 or later)
sf plugins list
```

### Step 10 — Authenticate with Salesforce

Salesforce CLI and CumulusCI keep separate org registries. An SF CLI login does
not create a CCI alias. For an existing org, authenticate to the same target org
in both tools; use `<sf-alias>` with `sf` and `<cci-alias>` with `cci`.

```bash
# Register an existing org with Salesforce CLI
sf org login web --alias <sf-alias>
# For a sandbox, add --instance-url https://test.salesforce.com

# Register that existing org with CCI (once per new CCI alias)
cci org connect <cci-alias>
# For a sandbox, add --sandbox to the connect command
cci org default <cci-alias>
```

For scratch-org creation, authenticate the Dev Hub separately in Salesforce CLI:

```bash
sf org login web --alias devhub --set-default-dev-hub --instance-url https://login.salesforce.com
```

Create the target scratch org using the [org-operations quick start](org-operations.md#create-a-scratch-org); `cci org scratch` registers its CCI alias.

### Step 11 — Verify the full setup

The validator checks Python, CumulusCI, Salesforce CLI, SFDMU, Node.js,
Robot/browser dependencies, and the gate interpreter (the `.venv` from
[Step 6](#step-6--create-and-activate-a-virtual-environment-venv)) without
connecting to an org. A missing or incomplete gate interpreter is a warning,
not a failure. Install Chrome or
Chromium yourself before running it: `brew install --cask google-chrome` on
macOS, or your distribution's Chromium package on Linux.

**CCI installed with pipx:** Robot dependency auto-fix targets the pipx CumulusCI
environment via `pipx inject cumulusci --force -r robot/requirements.txt`.
With the default `auto_fix_robot=true`, it runs when Robot Framework,
SeleniumLibrary or webdriver-manager is missing, or selenium is missing or below
4.10 (only selenium has a version check):

```bash
cci task run validate_setup
```

**CCI installed in a project venv:** activate that venv and install the Robot
requirements there first. The validator's Robot and urllib3 auto-fixes use pipx,
so disable them to avoid modifying a separate environment:

```bash
source .venv/bin/activate
python -m pip install --upgrade -r robot/requirements.txt
cci task run validate_setup -o auto_fix_robot false -o auto_fix_urllib3 false
```

A passing result requires the Robot packages in the environment running CCI,
Chrome/Chromium, and either webdriver-manager or a compatible ChromeDriver on
PATH. SFDMU updates are controlled by `auto_fix` (default true). The independent
`auto_fix_urllib3` option defaults to false and also targets pipx when enabled;
`robot/requirements.txt` includes the required urllib3 version for either setup.
The validator does not install Salesforce CLI, Node.js, Python, or a browser.

### Using Claude Code with this project

[Claude Code](https://claude.com/claude-code) spawns **non-interactive shells**, so don't rely on `~/.zshrc` for anything it needs: depending on how it was launched it may not see that file, or may see a snapshot taken when it started. Without `~/.zshenv`, Claude Code's Bash tool cannot find nvm-managed Node (`sf`, `node`), pipx's `cci` or pyenv. Steps 3 and 4 above copy the Homebrew, NVM and pyenv blocks of the [§2 `~/.zshenv` template](dev-environment-setup.md#zshenv--runs-in-every-shell) into `~/.zshenv`, and [dev-environment-setup.md §5](dev-environment-setup.md#5-replicating-on-a-new-workstation) merges the rest, including the `~/.local/bin` line for `cci` and the direnv line that puts pyenv's `python` on PATH in the repo. If you skipped those blocks, add them now. The template deliberately has no `pyenv init`; don't add one.

**Verify Claude Code can see your tools** by asking it to run:

```bash
node --version && sf --version && cci version && pyenv exec python --version
```

If any command returns "not found", check that `~/.zshenv` contains the blocks from the §2 `~/.zshenv` template (Steps 3 and 4 copy the Homebrew, NVM and pyenv ones), then **restart Claude Code** so it picks up the updated PATH. A bare `python --version` reports pyenv's Python only inside the repo, once direnv is set up ([dev-environment-setup.md §5](dev-environment-setup.md#5-replicating-on-a-new-workstation)); before that, or outside the repo, it reports macOS's `/usr/bin/python3` or nothing. That's by design (there's no global `pyenv init`), so don't add one to fix it.

**After any PATH change** (new nvm version, new pyenv version, new pipx install), restart Claude Code — it inherits the PATH from the shell that launched it and does not reload `~/.zshenv` mid-session.

### Ongoing toolchain maintenance

Once the bootstrap above is complete, ongoing updates (new Python patches,
Node LTS refreshes, sf/CCI/SFDMU upgrades) are handled by a single script:

```bash
scripts/bash/update-toolchain.sh
```

It walks `brew update` → keep `openssl@3` installed on request → `brew upgrade --formula` (casks are yours to upgrade) → latest patch in your pinned Python line (stopping if it can't import `ssl`) → the newest patch of the Node line in `.nvmrc` → `sf` via `npm install -g`, or `sf update` for an installer-based `sf` → CCI reinstall/upgrade → Robot pins re-injected → `sf plugins update` → gate interpreter `.venv` refresh (if it exists) → `cci task run validate_setup`. Major-line pins: Python's (3.13) is at the top of the script, Node's (24) is `.nvmrc`.

For the full architecture — shell config responsibilities, the per-project `.envrc` pattern via [direnv](https://direnv.net/), troubleshooting, and instructions for replicating on a new workstation — see [`docs/guides/dev-environment-setup.md`](dev-environment-setup.md).

**Validating the full setup from an agent:** Follow [Step 11](#step-11--verify-the-full-setup) using the command for your CCI installation method. The Robot and urllib3 auto-fixes target pipx, not a project venv. No org connection is needed.

---

## Prerequisites

> **macOS users:** See [macOS Environment Setup (Homebrew + pyenv + nvm)](#macos-environment-setup-homebrew--pyenv--nvm) for a step-by-step guide using Homebrew, pyenv (Python), nvm (Node.js), and pipx — including git, gh, GCM, and Cursor integration.

### Required Software

1. **git**
   - Installation (macOS): `brew install git` — or use the Xcode Command Line Tools (`xcode-select --install`)
   - Verify: `git --version`

2. **GitHub CLI** (`gh`) — recommended
   - Used for cloning, PR workflows, and authentication
   - Installation: `brew install gh` (macOS) — see https://cli.github.com/
   - Verify: `gh --version`
   - Authenticate: `gh auth login`

3. **Git Credential Manager** (GCM) — recommended
   - Provides secure, cross-platform credential storage for HTTPS git operations
   - Installation: `brew install --cask git-credential-manager` (macOS) — see https://github.com/git-ecosystem/git-credential-manager
   - Configured automatically after installation

4. **Salesforce CLI** (`sf` CLI)
   - Version 2.x or later; use Node.js 24, the line pinned in `.nvmrc`, to meet this repository's npm engine requirement (`engines.node: >=24`)
   - Installation (macOS): `npm install -g @salesforce/cli` — see https://developer.salesforce.com/tools/salesforcecli
   - Verify: `sf --version`

5. **CumulusCI** (CCI)
   - Minimum version: 4.10.1 (as specified in `cumulusci.yml`; older versions fail with `INVALID_AUTH_HEADER` against current `sf`)
   - Installation: **prefer** `pipx install cumulusci --python "$(pyenv prefix)/bin/python3"` (ensure your pyenv global is set to a supported version — 3.12 or 3.13). If you don't use pipx: create a virtual environment and run `pip install cumulusci` inside it.
   - Verify: `cci version`

6. **SFDMU (Salesforce Data Move Utility)**
   - **Version 5.6.4 or later required** (v4.x is no longer supported; pre-5.6.4 5.x breaks Upsert matching on relationship externalIds)
   - Required for data loading tasks
   - Installation: `sf plugins install sfdmu`
   - Verify: `sf plugins list` (should show sfdmu 5.6.4 or later)
   - The `validate_setup` task checks and auto-updates the SFDMU version
   - Documentation: https://help.sfdmu.com/

7. **Node.js** — required by the `sf` CLI and SFDMU plugin
   - Use **Node 24**, the line pinned in `.nvmrc` (`package.json` declares `engines.node: >=24`; the Docker image and the build workflow use 24)
   - Installation (macOS): `brew install nvm` then `nvm install 24` (recommended) — see Step 3 in the macOS setup guide
   - Verify: `node --version`

8. **Python** (for custom tasks and the repo's AI/schema-diff scripts)
   - Python 3.11 to 3.13 (CumulusCI 4.10.1 requires `>=3.11,<3.14`); **3.12 recommended** for CumulusCI (3.13 is what the CI workflow uses and is the dev-environment-setup default; 3.14 has known dependency compatibility issues). (The standalone schema-diff and skill-manifest scripts need only 3.10.)
   - macOS: use [pyenv](https://github.com/pyenv/pyenv) — `brew install pyenv` — to manage versions
   - Required packages are included with CumulusCI; use a venv for local script development
   - The repo's `.venv` is also the gate interpreter for `scripts/ai/pr_gate.py`: create it with Python 3.13 and install the gate requirements into it (see [Step 6](#step-6--create-and-activate-a-virtual-environment-venv))

### Required Salesforce Access

- Salesforce org with Revenue Cloud licenses
- Appropriate permissions for metadata deployment
- For scratch orgs: Dev Hub enabled

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install CumulusCI:**
   ```bash
   pipx install cumulusci
   ```
   Prefer **pipx** so CumulusCI runs in an isolated environment and does not install into your global Python. If you don't use pipx, create a [virtual environment](https://docs.python.org/3/library/venv.html) first, then run `pip install cumulusci` inside it.

   #### Setup for headless robot runs

   Required if you use Robot-backed setup tasks such as `prepare_docgen`, `enable_document_builder_toggle`, `enable_constraints_settings`, `configure_revenue_settings`, `configure_core_pricing_setup`, `configure_product_discovery_settings`, `enable_timeline`, or `reorder_app_launcher`:

   1. **Python packages** — Robot Framework, selenium (4.10+), SeleniumLibrary, webdriver-manager, urllib3. Keep them in the **same environment as CumulusCI** so CCI tasks can run the `robot` command. A full dependency set is in **`robot/requirements.txt`**. If you use **pipx** for CumulusCI (recommended):
     ```bash
     pipx inject cumulusci --force -r robot/requirements.txt
     ```
     If you use a project virtual environment: `python -m pip install --upgrade -r robot/requirements.txt` inside the venv. Use the [venv validation command](#step-11--verify-the-full-setup) with pipx auto-fixes disabled. If you previously installed these globally, uninstall first: `python3 -m pip uninstall -y robotframework-seleniumlibrary robotframework selenium webdriver-manager`.

     > **selenium 4.10+ required:** The `executable_path` argument was removed from the Chrome WebDriver in selenium 4.10. The `robot/requirements.txt` pins `selenium>=4.51.0,<5`. If selenium is older than that pin, update the requirements in the environment running CCI. Validator auto-upgrade targets pipx only; venv users should run `python -m pip install --upgrade -r robot/requirements.txt` inside the venv.

   2. **Chrome or Chromium** — Robot tasks run headless by default and require Chrome or Chromium. (Use `BROWSER=firefox` to run with Firefox instead.)
     - **macOS:** Install [Google Chrome](https://www.google.com/chrome/) or `brew install chromium`
     - **Linux:** `apt install chromium` (Debian/Ubuntu) or `dnf install chromium` (Fedora)
     - **CI:** Set `CHROME_BIN` to the browser path (e.g. `/usr/bin/chromium`)
     - **Alternate browser:** Set `CHROME_BINARY` to launch a specific Chrome executable instead of the stock install. It takes precedence over `CHROME_BIN`. Pair it with `CHROMEDRIVER_PATH` (step 3) so the driver matches. See [Chrome for Testing](#chrome-for-testing-managed-workstations).

   3. **ChromeDriver** — webdriver-manager downloads it automatically at runtime. If webdriver-manager is not installed, ChromeDriver must be on `PATH` or at `/usr/bin/chromedriver` (e.g. `apt install chromium-driver` on Debian/Ubuntu). Set `CHROMEDRIVER_PATH` to force a specific driver; it wins over every other lookup, and is ignored with a warning if it is not an executable file.

   4. **Salesforce CLI** — The task uses `sf org open --url-only` to authenticate the browser; ensure `sf` is installed and the org is logged in.

   5. **Verify** — Use the [validation command for your CCI environment](#step-11--verify-the-full-setup) (no org required) to check dependencies, including Chrome/Chromium and ChromeDriver. It reports the overrides above when set, and flags a Chrome/ChromeDriver major-version mismatch: it fails when the browser comes from an override, and warns when the browser path was found by search. It also warns when a browser override is set but no ChromeDriver is (webdriver-manager would size its driver for stock Chrome, not the override), and fails when an override exists but does not run cleanly (e.g. a build for the wrong architecture, or one that exits with an error such as a missing shared library).

   #### Chrome for Testing (managed workstations)

   Optional. Most machines run the Robot tasks on stock Chrome. On some managed workstations, stock headless Chrome crashes on Salesforce Setup pages (the root cause is not confirmed; it has only been seen on managed machines): the Robot step (e.g. `enable_document_builder_toggle` in `prepare_docgen`) fails with `Unable to receive message from renderer`, even though Chrome loads other sites. [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) is a separate Chrome build that does not touch your regular install, and it loads those pages. Install a browser and a driver of the **same version** (`npx` ships with Node.js):

   ```bash
   # any Chrome for Testing version; keep browser and driver identical
   CFT_VERSION=154.0.8037.92
   npx -y @puppeteer/browsers install "chrome@$CFT_VERSION" --path ~/.cache/cft
   npx -y @puppeteer/browsers install "chromedriver@$CFT_VERSION" --path ~/.cache/cft
   ```

   Each command prints the installed executable's path. Export both before running CCI (macOS Apple silicon paths for 154.0.8037.92 shown; substitute your version, since `CFT_VERSION` is not kept once the shell exits), then rerun `validate_setup`:

   ```bash
   export CHROME_BINARY="$HOME/.cache/cft/chrome/mac_arm-154.0.8037.92/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
   export CHROMEDRIVER_PATH="$HOME/.cache/cft/chromedriver/mac_arm-154.0.8037.92/chromedriver-mac-arm64/chromedriver"
   ```

   Both variables are unset by default, and nothing changes when they are unset. On machines that need them, put them in `.env.local` at the repo root as `KEY="value"` lines without `export` (`$HOME` expands; quote the value, since the Chrome path has spaces and one unparsable line stops the file from loading). It's gitignored. The tracked `.envrc` loads it as dotenv, and `./tui-cci` loads the same file for any variable the shell has not already set. Don't add them to `.envrc` itself: it's tracked, so git overwrites local edits to it.

3. **Install SFDMU (v5.6.4+):**
   ```bash
   sf plugins install sfdmu
   ```

4. **Verify installations:**
   ```bash
   sf --version
   cci version
   # Should show sfdmu 5.6.4 or later
   sf plugins list
   ```
   **Headless robot env — no org or flow required:** With pipx, run the command below. For project-venv CCI, use the [venv validation command](#step-11--verify-the-full-setup) after installing its requirements:
   ```bash
   cci task run validate_setup
   ```
   Or manually: `~/.local/pipx/venvs/cumulusci/bin/robot --version` and `~/.local/pipx/venvs/cumulusci/bin/python -c "import SeleniumLibrary; print('SeleniumLibrary OK')"` (pipx path; on Windows use `...\Scripts\robot.bat`). If all checks pass, your env is ready for headless robot tasks when the org is configured.

5. **Authenticate an existing org with Salesforce CLI:**
   ```bash
   sf org login web --alias <sf-alias>
   # For a sandbox, add --instance-url https://test.salesforce.com
   ```
   For scratch orgs, follow [Step 10](#step-10--authenticate-with-salesforce) for Dev Hub authentication and scratch-org creation instead.

6. **Register the same existing org with CumulusCI:**
   SF CLI and CCI aliases belong to separate registries. Connect once per new CCI alias, then select it as the default:
   ```bash
   cci org connect <cci-alias>
   # For a sandbox, add --sandbox to the connect command
   cci org default <cci-alias>
   ```
