# Local Installation

[Home](../../README.md) · [Documentation](../index.md) · [Org operations](org-operations.md)

Install the local toolchain and authenticate before running Salesforce workflows.
Before cloning, run the bootstrap commands from your chosen workspace directory.
After cloning, run commands from the repository root unless a step says otherwise.
For a containerized toolchain, use the [Docker guide](../../docker/README.md).

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
> **Node.js 22 or later required:** The repository npm tooling declares `engines.node: >=22` in `package.json`. Use an LTS release meeting that floor; the build workflow uses Node 24.

```bash
# Install nvm via Homebrew
brew install nvm

# Add nvm to your interactive shell (~/.zshrc)
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
echo '[ -s "$(brew --prefix nvm)/nvm.sh" ] && \. "$(brew --prefix nvm)/nvm.sh"' >> ~/.zshrc
echo '[ -s "$(brew --prefix nvm)/etc/bash_completion.d/nvm" ] && \. "$(brew --prefix nvm)/etc/bash_completion.d/nvm"' >> ~/.zshrc

# Also add nvm to ~/.zshenv so non-interactive shells see it
# (required for IDE tools, CI runners, and Claude Code which spawn non-interactive shells)
# Homebrew is often only on PATH in login shells (~/.zprofile); fall back to known absolute
# locations so this works in non-interactive shells that never source ~/.zprofile.
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshenv
echo '# Bootstrap Homebrew in non-interactive shells' >> ~/.zshenv
echo 'if ! command -v brew >/dev/null 2>&1; then' >> ~/.zshenv
echo '  for _brew in /opt/homebrew/bin/brew /usr/local/bin/brew; do' >> ~/.zshenv
echo '    [ -x "$_brew" ] && eval "$($_brew shellenv)" && break' >> ~/.zshenv
echo '  done' >> ~/.zshenv
echo 'fi' >> ~/.zshenv
echo 'if command -v brew >/dev/null 2>&1; then' >> ~/.zshenv
echo '  NVM_PREFIX="$(brew --prefix nvm 2>/dev/null)"' >> ~/.zshenv
echo '  if [ -n "$NVM_PREFIX" ] && [ -s "$NVM_PREFIX/nvm.sh" ]; then' >> ~/.zshenv
echo '    \. "$NVM_PREFIX/nvm.sh"' >> ~/.zshenv
echo '  fi' >> ~/.zshenv
echo 'fi' >> ~/.zshenv

# Reload your shell
source ~/.zshrc

# Install the latest LTS version of Node.js
nvm install --lts

# Set LTS as the default for all new shells
nvm alias default 'lts/*'

# Verify
node --version   # Should show an LTS release >=22 (the build workflow uses Node 24)
npm --version
```

> **After setup, restart your terminal** (or any IDE/tool that spawns shells) so the updated PATH takes effect in all contexts.

If you already have `brew install node` and want to migrate to nvm, remove the Homebrew version after installing nvm — it is no longer needed:
```bash
brew uninstall node   # safe after nvm is installed and default is set
```

### Step 4 — Install pyenv and Python

[pyenv](https://github.com/pyenv/pyenv) lets you install and switch between Python versions without touching the system Python.

**Python 3.12 or 3.13 is recommended for CumulusCI** — both are stable and tested with CCI 4.x. Python 3.14 is very new (released October 2025) and has known dependency compatibility issues. Avoid it for CCI.

```bash
# Install pyenv
brew install pyenv

# Add pyenv to your interactive shell (~/.zshrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Also add pyenv to ~/.zshenv for non-interactive shells
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshenv
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshenv
echo 'eval "$(pyenv init -)"' >> ~/.zshenv

# Reload your shell
source ~/.zshrc

# Install the latest 3.13.x patch automatically
PYTHON_VERSION=$(pyenv install --list | grep -E "^[[:space:]]*3\.13\.[0-9]+$" | tail -1 | tr -d '[:space:]')
pyenv install "$PYTHON_VERSION"
pyenv global "$PYTHON_VERSION"

# Verify
python --version   # Should show the latest 3.13.x patch
```

> **Using multiple Python versions?** You can install additional versions alongside (for example, another 3.12.x or 3.13.x patch) and switch per-project with a `.python-version` file. Keep whichever version you use for CCI consistent with what you pass to `pipx install cumulusci --python`.

> **Non-interactive shell note:** The `~/.zshenv` additions above ensure that IDE tools, CI runners, and Claude Code (which spawn non-interactive shells) can find your pyenv-managed Python. Without `~/.zshenv`, only interactive terminal sessions see pyenv.

### Step 5 — Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

> Replace `<repository-url>` with the actual repo URL from GitHub (use `gh repo clone <org>/<repo>` if you used `gh auth login` above).

### Step 6 — Create and activate a virtual environment (venv)

From the repository cloned in Step 5, create a project-specific virtual environment. This isolates the project's Python dependencies from your system and other projects.

> **If you install CumulusCI via pipx (recommended, Step 7), you do not need to manually install packages into this venv** — pipx manages CCI in its own isolated environment. Still create a venv if you want to run project scripts (`scripts/`, `tasks/`) directly outside of CCI, or if you choose `pip install cumulusci` instead.

```bash
# From the repo root (uses whichever Python pyenv points to — 3.12 recommended)
python -m venv .venv

# Activate the venv
source .venv/bin/activate

# Your prompt should now show (.venv) prefix
# Verify
python --version
pip --version
```

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
cci version   # Should show CumulusCI 4.x running on Python 3.13.x
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
sf --version   # Check CLI >=2 and Node LTS >=22; platform/architecture and patch versions vary
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

The validator checks Python, CumulusCI, Salesforce CLI, SFDMU, Node.js, and
Robot/browser dependencies without connecting to an org. Install Chrome or
Chromium yourself before running it: `brew install --cask google-chrome` on
macOS, or your distribution's Chromium package on Linux.

**CCI installed with pipx:** Robot dependency auto-fix targets the pipx CumulusCI
environment via `pipx inject cumulusci --force -r robot/requirements.txt`.
With the default `auto_fix_robot=true`, missing or outdated Robot Framework,
selenium (4.10+), SeleniumLibrary, and webdriver-manager can be installed there:

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

[Claude Code](https://claude.com/claude-code) spawns **non-interactive shells** (it does not source `~/.zshrc`). Without `~/.zshenv`, Claude Code's Bash tool cannot find nvm-managed Node (`sf`, `node`) or pyenv-managed Python (`python`, `cci`). Steps 3 and 4 above add the required init blocks to `~/.zshenv` — if you skipped those additions, add them now.

**Verify Claude Code can see your tools** by asking it to run:

```bash
node --version && sf --version && cci version && python --version
```

If any command returns "not found", check that `~/.zshenv` contains the nvm and pyenv init blocks (see Steps 3 and 4), then **restart Claude Code** so it picks up the updated PATH.

**After any PATH change** (new nvm version, new pyenv version, new pipx install), restart Claude Code — it inherits the PATH from the shell that launched it and does not reload `~/.zshenv` mid-session.

### Ongoing toolchain maintenance

Once the bootstrap above is complete, ongoing updates (new Python patches,
Node LTS refreshes, sf/CCI/SFDMU upgrades) are handled by a single script:

```bash
scripts/bash/update-toolchain.sh
```

It walks `brew update && brew upgrade` → latest patch in your pinned Python line → latest LTS Node → `sf update` → CCI reinstall/upgrade → `sf plugins update` → `cci task run validate_setup`. Major-line pins (e.g. Python 3.13, Node `lts/*`) are configured at the top of the script.

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
   - Version 2.x or later; use an LTS Node.js release **22 or later** to meet this repository's npm engine requirement
   - Installation (macOS): `npm install -g @salesforce/cli` — see https://developer.salesforce.com/tools/salesforcecli
   - Verify: `sf --version`

5. **CumulusCI** (CCI)
   - Minimum version: 4.0.0 (as specified in `cumulusci.yml`)
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
   - Use an LTS release **22 or later**, matching `package.json`; the build workflow uses Node 24
   - Installation (macOS): `brew install nvm` then `nvm install --lts` (recommended) — see Step 3 in the macOS setup guide
   - Verify: `node --version`

8. **Python** (for custom tasks and the repo's AI/schema-diff scripts)
   - Python 3.10 or later; **3.12 recommended** for CumulusCI (3.13 is what the CI workflow uses and is the dev-environment-setup default; 3.14 has known dependency compatibility issues). The 3.10 floor matches what the schema-diff and skill-manifest scripts already use (PEP 604 unions).
   - macOS: use [pyenv](https://github.com/pyenv/pyenv) — `brew install pyenv` — to manage versions
   - Required packages are included with CumulusCI; use a venv for local script development

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

     > **selenium 4.10+ required:** The `executable_path` argument was removed from the Chrome WebDriver in selenium 4.10. The `robot/requirements.txt` pins `selenium>=4.10,<5`. If selenium is older, update the requirements in the environment running CCI. Validator auto-upgrade targets pipx only; venv users should run `python -m pip install --upgrade -r robot/requirements.txt` inside the venv.

   2. **Chrome or Chromium** — Robot tasks run headless by default and require Chrome or Chromium. (Use `BROWSER=firefox` to run with Firefox instead.)
     - **macOS:** Install [Google Chrome](https://www.google.com/chrome/) or `brew install chromium`
     - **Linux:** `apt install chromium` (Debian/Ubuntu) or `dnf install chromium` (Fedora)
     - **CI:** Set `CHROME_BIN` to the browser path (e.g. `/usr/bin/chromium`)

   3. **ChromeDriver** — webdriver-manager downloads it automatically at runtime. If webdriver-manager is not installed, ChromeDriver must be on `PATH` or at `/usr/bin/chromedriver` (e.g. `apt install chromium-driver` on Debian/Ubuntu).

   4. **Salesforce CLI** — The task uses `sf org open --url-only` to authenticate the browser; ensure `sf` is installed and the org is logged in.

   5. **Verify** — Use the [validation command for your CCI environment](#step-11--verify-the-full-setup) (no org required) to check dependencies, including Chrome/Chromium and ChromeDriver.

3. **Install SFDMU (v5.6.4+):**
   ```bash
   sf plugins install sfdmu
   ```

4. **Verify installations:**
   ```bash
   sf --version
   cci version
   sf plugins list  # Should show sfdmu 5.6.4 or later
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
