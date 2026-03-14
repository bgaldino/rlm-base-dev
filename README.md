# Revenue Cloud Base Foundations

**Salesforce Release:** 260 (Spring '26)
**API Version:** 66.0

This repository automates the creation and configuration of Salesforce environments that require Revenue Cloud (formerly Revenue Lifecycle Management) functionality.

The main branch targets Salesforce Release 260 (Spring '26, GA). Other branches exist for different release scenarios.

## Table of Contents

- [macOS Environment Setup (Homebrew + pyenv + nvm)](#macos-environment-setup-homebrew--pyenv--nvm)
  - [Using Claude Code with this project](#using-claude-code-with-this-project)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Setup for headless robot runs](#setup-for-headless-robot-runs)
- [Quick Start](#quick-start)
- [Feature Flags](#feature-flags)
- [Custom Tasks](#custom-tasks)
- [Flows](#flows)
- [Data Plans](#data-plans)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Branch Information](#branch-information)
- [Additional Resources](#additional-resources)

## macOS Environment Setup (Homebrew + pyenv + nvm)

> **Cursor users:** Open this README in [Cursor](https://www.cursor.com/), press `Cmd+L` to open the AI chat, and paste: *"Walk me through the macOS Environment Setup section of this README, running each command in the terminal."* The agent can execute each step interactively. Run the steps in order — each one builds on the previous.

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
> **Node LTS versions only:** Always use an even-numbered LTS release (v20, v22, v24) for tooling. Odd-numbered releases (v21, v23, v25) are short-lived "Current" releases with no long-term support — they reach end-of-life within 6 months and are not suitable for developer tools.

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
nvm alias default lts/*

# Verify
node --version   # Should show an even-numbered LTS version (v20, v22, v24, …)
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

### Step 5 — Create and activate a virtual environment (venv)

After cloning the repository (Step 8 below), create a project-specific virtual environment. This isolates the project's Python dependencies from your system and other projects.

> **If you install CumulusCI via pipx (recommended, Step 6), you do not need to manually install packages into this venv** — pipx manages CCI in its own isolated environment. Still create a venv if you want to run project scripts (`scripts/`, `tasks/`) directly outside of CCI, or if you choose `pip install cumulusci` instead.

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

### Step 6 — Install CumulusCI

**Recommended: use pipx** — pipx installs CumulusCI in its own isolated Python environment, keeping it separate from your project venv and system Python.

```bash
# Install pipx via pyenv's Python — keeps all Python tooling under pyenv, not Homebrew
# Uses the pyenv global set in Step 4 ($(pyenv prefix) resolves to that version)
$(pyenv prefix)/bin/python3 -m pip install --user pipx

# Ensure ~/.local/bin is in your PATH (pipx installs cci, snowfakery, etc. there)
$(pyenv prefix)/bin/python3 -m pipx ensurepath
source ~/.zshrc

# Install CumulusCI using the same Python version
pipx install cumulusci --python "$(pyenv prefix)/bin/python3"

# Fix a known compatibility issue: CCI depends on fs/pyfilesystem2 which requires
# pkg_resources from setuptools<71. Newer setuptools removes pkg_resources.
pipx inject cumulusci "setuptools<71"

# Verify
cci version   # Should show CumulusCI 4.x running on Python 3.13.x
```

> **Why `setuptools<71`?** CumulusCI 4.x depends on `pyfilesystem2` which uses `pkg_resources`, a module that was removed from `setuptools` in version 71+. The inject command pins setuptools in the CCI venv to a compatible version. This does not affect your global Python or project venv.

If you prefer to use the project venv instead (activate it first per Step 5, then):

```bash
pip install cumulusci "setuptools<71"
cci version
```

### Step 7 — Install Salesforce CLI (`sf`)

Install `@salesforce/cli` via npm using the nvm-managed Node from Step 3. This is the Salesforce-recommended installation method.

```bash
# Install sf CLI globally via npm (nvm-managed Node must be active)
npm install -g @salesforce/cli

# Verify (must be 2.x or later)
sf --version   # Should show @salesforce/cli/2.x darwin-arm64 node-v24.x.x
```

> **Why npm instead of Homebrew?** The Homebrew `sf` formula and `--cask sf` cask bundle their own copy of Node.js independently of nvm. This creates redundant Node installations and potential version conflicts. Installing via npm ties sf to your nvm-managed Node version, giving you a single Node installation to manage.

> **After switching from Homebrew sf to npm:** If you previously had `brew install --cask sf` or `brew install sf`, remove it first: `brew uninstall sf`. The Homebrew cask is also deprecated and scheduled for removal on 2026-09-01.

> **npm globals and nvm versions:** npm global packages (like `@salesforce/cli`) are installed per nvm Node version. If you switch Node versions with `nvm use`, run `npm install -g @salesforce/cli` again in the new version, or use `nvm reinstall-packages <old-version>` to copy all globals.

### Step 8 — Clone the repository

```bash
git clone <repository-url>
cd rlm-base-dev
```

> Replace `<repository-url>` with the actual repo URL from GitHub (use `gh repo clone <org>/<repo>` if you used `gh auth login` above).

### Step 9 — Install SFDMU plugin (v5+)

SFDMU is a Salesforce CLI plugin for bulk data loading. **Version 5.0.0 or later is required.**

```bash
sf plugins install sfdmu

# Verify (should show 5.x)
sf plugins list
```

### Step 10 — Authenticate with Salesforce

```bash
# For a standard org
sf org login web

# For a Dev Hub (required for scratch orgs)
sf org login web --alias devhub --instance-url https://login.salesforce.com

# Set your default org for CCI
cci org default <your-org-alias>
```

### Step 11 — Verify the full setup

Run the built-in setup validator (no org connection required):

```bash
cci task run validate_setup
```

This checks Python, CumulusCI, Salesforce CLI, SFDMU plugin version, Node.js, and Robot Framework dependencies. Robot Framework and SeleniumLibrary are **required**; `validate_setup` ensures that either `webdriver-manager` is installed in the CCI environment (preferred) or a compatible `chromedriver` binary is available on PATH. When `auto_fix_robot` is true (default), missing Robot Framework pieces and `webdriver-manager` are auto-installed via `pipx inject`. Chrome or Chromium must be installed manually — `validate_setup` will report FAIL if no supported browser is found. A passing summary confirms your environment is ready.

> **What is and isn't auto-fixed:** `validate_setup` auto-fixes the SFDMU plugin version, Robot Framework deps (Robot, SeleniumLibrary, webdriver-manager via `pipx inject -r robot/requirements.txt`), and optionally urllib3 (`auto_fix_urllib3=true`). It does **not** auto-install sf CLI, Node.js, Python, or Chrome/Chromium — those must be installed manually. Install Chrome before running flows: `brew install --cask google-chrome` (macOS) or your distribution's chromium package (Linux).

### Using Claude Code with this project

[Claude Code](https://claude.com/claude-code) spawns **non-interactive shells** (it does not source `~/.zshrc`). Without `~/.zshenv`, Claude Code's Bash tool cannot find nvm-managed Node (`sf`, `node`) or pyenv-managed Python (`python`, `cci`). Steps 3 and 4 above add the required init blocks to `~/.zshenv` — if you skipped those additions, add them now.

**Verify Claude Code can see your tools** by asking it to run:

```bash
node --version && sf --version && cci version && python --version
```

If any command returns "not found", check that `~/.zshenv` contains the nvm and pyenv init blocks (see Steps 3 and 4), then **restart Claude Code** so it picks up the updated PATH.

**After any PATH change** (new nvm version, new pyenv version, new pipx install), restart Claude Code — it inherits the PATH from the shell that launched it and does not reload `~/.zshenv` mid-session.

**Validating the full setup from Claude Code:** Ask Claude to run `cci task run validate_setup`. This checks all required tools and — when the relevant auto-fix options are enabled — can auto-fix missing robot deps (default on) and update the SFDMU version (default on). urllib3 is upgraded as a side-effect of the robot dep fix, or independently with `auto_fix_urllib3=true`. No org connection needed. It is the fastest way to confirm your environment is ready before running flows.

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
   - Version 2.x or later; requires an LTS Node.js (v20, v22, or v24 — **not** odd-numbered releases like v25 which are unsupported)
   - Installation (macOS): `npm install -g @salesforce/cli` — see https://developer.salesforce.com/tools/salesforcecli
   - Verify: `sf --version`

5. **CumulusCI** (CCI)
   - Minimum version: 4.0.0 (as specified in `cumulusci.yml`)
   - Installation: **prefer** `pipx install cumulusci --python "$(pyenv prefix)/bin/python3"` then `pipx inject cumulusci "setuptools<71"` (ensure your pyenv global is set to a supported version — 3.12 or 3.13). If you don't use pipx: create a virtual environment and run `pip install cumulusci "setuptools<71"` inside it.
   - Verify: `cci version`

6. **SFDMU (Salesforce Data Move Utility)**
   - **Version 5.0.0 or later required** (v4.x is no longer supported)
   - Required for data loading tasks
   - Installation: `sf plugins install sfdmu`
   - Verify: `sf plugins list` (should show sfdmu 5.x)
   - The `validate_setup` task checks and auto-updates the SFDMU version
   - Documentation: https://help.sfdmu.com/

7. **Node.js** — required by the `sf` CLI and SFDMU plugin
   - Use an LTS version (even-numbered: v20, v22, v24); odd-numbered releases (v21, v23, v25) are not supported by sf CLI
   - Installation (macOS): `brew install nvm` then `nvm install --lts` (recommended) — see Step 3 in the macOS setup guide
   - Verify: `node --version`

8. **Python** (for custom tasks)
   - Python 3.8 or later; **3.12 recommended** for CumulusCI (3.13 is acceptable; 3.14 has known dependency compatibility issues)
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
   cd rlm-base-dev
   ```

2. **Install CumulusCI:**
   ```bash
   pipx install cumulusci
   ```
   Prefer **pipx** so CumulusCI runs in an isolated environment and does not install into your global Python. If you don't use pipx, create a [virtual environment](https://docs.python.org/3/library/venv.html) first, then run `pip install cumulusci` inside it.

   #### Setup for headless robot runs

   Required if you use `prepare_docgen`, `enable_document_builder_toggle`, `enable_constraints_settings`, or `configure_revenue_settings`:

   1. **Python packages** — Robot Framework, SeleniumLibrary, webdriver-manager, urllib3. Keep them in the **same environment as CumulusCI** so CCI tasks can run the `robot` command. A full dependency set is in **`robot/requirements.txt`**. If you use **pipx** for CumulusCI (recommended):
     ```bash
     pipx inject cumulusci robotframework robotframework-seleniumlibrary webdriver-manager "urllib3>=2.6.3"
     ```
     If you use a project virtual environment: `pip install -r robot/requirements.txt` inside the venv. If you previously installed these globally, uninstall first: `python3 -m pip uninstall -y robotframework-seleniumlibrary robotframework webdriver-manager`.

   2. **Chrome or Chromium** — Robot tasks run headless by default and require Chrome or Chromium. (Use `BROWSER=firefox` to run with Firefox instead.)
     - **macOS:** Install [Google Chrome](https://www.google.com/chrome/) or `brew install chromium`
     - **Linux:** `apt install chromium` (Debian/Ubuntu) or `dnf install chromium` (Fedora)
     - **CI:** Set `CHROME_BIN` to the browser path (e.g. `/usr/bin/chromium`)

   3. **ChromeDriver** — webdriver-manager downloads it automatically at runtime. If webdriver-manager is not installed, ChromeDriver must be on `PATH` or at `/usr/bin/chromedriver` (e.g. `apt install chromium-driver` on Debian/Ubuntu).

   4. **Salesforce CLI** — The task uses `sf org open --url-only` to authenticate the browser; ensure `sf` is installed and the org is logged in.

   5. **Verify** — Run `cci task run validate_setup` (no org required) to check all dependencies including Chrome/Chromium and ChromeDriver.

3. **Install SFDMU (v5+):**
   ```bash
   sf plugins install sfdmu
   ```

4. **Verify installations:**
   ```bash
   sf --version
   cci version
   sf plugins list  # Should show sfdmu 5.x
   ```
   **Headless robot env — no org or flow required:** To confirm all headless robot dependencies (Robot, SeleniumLibrary, webdriver-manager, Chrome/Chromium, ChromeDriver, urllib3), run:
   ```bash
   cci task run validate_setup
   ```
   Or manually: `~/.local/pipx/venvs/cumulusci/bin/robot --version` and `~/.local/pipx/venvs/cumulusci/bin/python -c "import SeleniumLibrary; print('SeleniumLibrary OK')"` (pipx path; on Windows use `...\Scripts\robot.bat`). If all checks pass, your env is ready for headless robot tasks when the org is configured.

5. **Authenticate with Salesforce:**
   ```bash
   sf org login web
   # OR for Dev Hub (for scratch orgs)
   sf org login web --alias devhub --instance-url https://login.salesforce.com
   ```

6. **Initialize CumulusCI:**
   ```bash
   cci org default <your-org-alias>
   ```

## Quick Start

### Create a Scratch Org

```bash
# Create a basic dev scratch org
cci org scratch dev <org-alias>

# Create an enhanced dev scratch org (with additional features)
cci org scratch dev_enhanced <org-alias>
```

### Deploy to an Existing Org

```bash
# Set default org
cci org default <org-alias>

# Run the main deployment flow
cci flow run prepare_rlm_org
```

### Reset default or target scratch org and run full flow

To remove your current default (or target) scratch org, create a new one, and run the full RLM prepare flow (includes billing data when applicable), use your scratch org config and alias (e.g. `beta`, `dev`, `dev_enhanced`—see `orgs/` and `cumulusci.yml` under `orgs.scratch`):

```bash
# Delete existing scratch org (use the same alias you created it with)
cci org scratch_delete <org-alias>

# Create a new scratch org (config name and alias; set as default if desired)
cci org scratch <config-name> <org-alias> --default --days 30

# Run the full prepare flow on that org
cci flow run prepare_rlm_org --org <org-alias>
```

Decision tables under `unpackaged/pre/5_decisiontables` are deployed by this flow. Active decision tables are excluded per run by moving them into a `.skip` subdirectory before deploy (no `.forceignore` changes). Permission set groups are recalculated only when they are in **Outdated** state; if all are already **Updated**, the recalc step exits without waiting.

### List Available Flows and Tasks

```bash
cci flow list
cci task list
```

## Feature Flags

The project uses custom flags in `cumulusci.yml` under `project.custom` to control feature deployment. Modify these flags or override them at runtime with `-o <flag> <value>`.

### Core Flags

| Flag | Default | Description |
|------|---------|-------------|
| `qbrix` | `false` | Use xDO base (false for dev scratch orgs without xDO licenses) |
| `tso` | `false` | Is Trialforce Source Org? (false for dev scratch orgs) |
| `qb` | `true` | QuantumBit dataset family |
| `q3` | `false` | Include Q3 data |
| `quantumbit` | `true` | QuantumBit features |
| `product_dataset` | `qb` | Default product dataset to use |
| `locale` | `en_US` | Default locale |
| `refresh` | `false` | Data refresh flag (skips initial data loads when true) |

### Data Flags

| Flag | Default | Description |
|------|---------|-------------|
| `rating` | `true` | Insert Rating design-time data |
| `rates` | `true` | Insert Rates |
| `ramps` | `true` | Insert and configure ramps |
| `clm_data` | `false` | Load Contract Lifecycle Management data |
| `constraints_data` | `true` | Load constraint model data (CML import + activation) |

### Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `calmdelete` | `true` | Use CALM Delete |
| `tax` | `true` | Use Tax engine |
| `billing` | `true` | Use Billing |
| `payments` | `true` | Use Payments |
| `approvals` | `true` | Use Approvals |
| `clm` | `true` | Use Contract Lifecycle Management |
| `dro` | `true` | Use Dynamic Revenue Orchestration |
| `einstein` | `true` | Use Einstein AI |
| `agents` | `false` | Deploy Agentforce Agent configurations |
| `prm` | `true` | Use Partner Relationship Management |
| `prm_exp_bundle` | `false` | Use PRM Experience Bundle |
| `commerce` | `false` | Use Commerce |
| `breconfig` | `false` | Business Rules Engine configuration |
| `docgen` | `true` | Use Document Generation |
| `constraints` | `true` | Use Constraint Builder (metadata setup) |
| `guidedselling` | `false` | Use Guided Selling |
| `procedureplans` | `true` | Use Procedure Plans |
| `visualization` | `false` | Use Visualization components (Flow with Visuals, LWC styling) |

### Deployment Flags

| Flag | Default | Description |
|------|---------|-------------|
| `sharingsettings` | `false` | Deploy Sharing Settings |

## Custom Tasks

This project includes custom Python task modules in the `tasks/` directory, each registered as one or more CCI tasks in `cumulusci.yml`.

### Data Management Tasks

Data management tasks are organized into two CCI groups so you can list or run by group:

- **Data Management - Extract** — SFDMU extract tasks (org → CSV). Output in `datasets/sfdmu/extractions/<plan_name>/<timestamp>`. **The same flow applies to every plan:** each task uses its plan directory from `cumulusci.yml`; post-process runs by default and writes re-import-ready CSVs to `<timestamp>/processed/`.
- **Data Management - Idempotency** — Idempotency test tasks (load twice, assert no record count increase; validates SFDMU v5 composite keys).

**List tasks by group:**

```bash
cci task list --group "Data Management - Extract"
cci task list --group "Data Management - Idempotency"
```

**Run all extract tasks or all idempotency tests (flows):**

```bash
cci flow run run_qb_extracts --org <org>
cci flow run run_qb_idempotency_tests --org <org>
```

| Task Name | Group | Description | Documentation |
|-----------|--------|-------------|---------------|
| `extract_qb_pcm_data` | Data Management - Extract | Extract qb-pcm (product catalog) from org to CSV | See `cumulusci.yml` |
| `extract_qb_pricing_data` | Data Management - Extract | Extract qb-pricing from org to CSV | See `cumulusci.yml` |
| `extract_qb_product_images_data` | Data Management - Extract | Extract qb-product-images from org to CSV | See `cumulusci.yml` |
| `extract_qb_dro_data` | Data Management - Extract | Extract qb-dro from org to CSV | See `cumulusci.yml` |
| `extract_qb_clm_data` | Data Management - Extract | Extract qb-clm from org to CSV | See `cumulusci.yml` |
| `extract_qb_rating_data` | Data Management - Extract | Extract qb-rating from org to CSV | See `cumulusci.yml` |
| `extract_qb_rates_data` | Data Management - Extract | Extract qb-rates from org to CSV | See `cumulusci.yml` |
| `extract_qb_transactionprocessingtypes_data` | Data Management - Extract | Extract qb-transactionprocessingtypes from org to CSV | See `cumulusci.yml` |
| `extract_qb_guidedselling_data` | Data Management - Extract | Extract qb-guidedselling from org to CSV | See `cumulusci.yml` |
| `test_qb_pcm_idempotency` | Data Management - Idempotency | Idempotency test for qb-pcm (supports extraction roundtrip) | [qb-pcm README](datasets/sfdmu/qb/en-US/qb-pcm/README.md) |
| `test_qb_pricing_idempotency` | Data Management - Idempotency | Idempotency test for qb-pricing | See `cumulusci.yml` |
| `test_qb_product_images_idempotency` | Data Management - Idempotency | Idempotency test for qb-product-images | See `cumulusci.yml` |
| `test_qb_dro_idempotency` | Data Management - Idempotency | Idempotency test for qb-dro | See `cumulusci.yml` |
| `test_qb_clm_idempotency` | Data Management - Idempotency | Idempotency test for qb-clm | See `cumulusci.yml` |
| `test_qb_rating_idempotency` | Data Management - Idempotency | Idempotency test for qb-rating | See `cumulusci.yml` |
| `test_qb_rates_idempotency` | Data Management - Idempotency | Idempotency test for qb-rates | See `cumulusci.yml` |
| `test_qb_transactionprocessingtypes_idempotency` | Data Management - Idempotency | Idempotency test for qb-transactionprocessingtypes | See `cumulusci.yml` |
| `test_qb_guidedselling_idempotency` | Data Management - Idempotency | Idempotency test for qb-guidedselling | See `cumulusci.yml` |
| `extract_qb_prm_data` | Data Management - Extract | Extract qb-prm (partner relationship management) from org to CSV | See `cumulusci.yml` |
| `test_qb_prm_idempotency` | Data Management - Idempotency | Idempotency test for qb-prm | See `cumulusci.yml` |
| `post_process_extraction` | Revenue Lifecycle Management | Post-process extracted CSVs (composite keys, header normalization) for re-import; see `scripts/post_process_extraction.py` | See `cumulusci.yml` |
| `load_sfdmu_data` | Revenue Lifecycle Management | Load SFDMU data plans (generic; supports simulation, object_sets, dynamic DRO user) | See `cumulusci.yml` |
| `export_cml` | Revenue Lifecycle Management | Export constraint model data (CSVs + blob) from an org | [Constraints Utility Guide](datasets/constraints/README.md) |
| `import_cml` | Revenue Lifecycle Management | Import constraint model data into an org (polymorphic resolution, dry run) | [Constraints Utility Guide](datasets/constraints/README.md) |
| `validate_cml` | Revenue Lifecycle Management | Validate CML file structure and ESC association coverage (no org needed) | [Constraints Utility Guide](datasets/constraints/README.md) |
| `sync_pricing_data` | Revenue Lifecycle Management | Sync pricing data (PricebookEntry/PriceAdjustmentSchedule) | See `cumulusci.yml` |

Extract output is written to `datasets/sfdmu/extractions/<plan_name>/<timestamp>/`. **Post-process runs by default** after extraction; re-import-ready CSVs are in `<timestamp>/processed/`. To skip post-process (raw SFDMU output only), pass `run_post_process: false` (e.g. `cci task run extract_qb_pcm_data --org <org> -o run_post_process false`). You can also run `post_process_extraction` manually for an existing extraction. See [Composite Key Optimizations](docs/sfdmu_composite_key_optimizations.md).

**Supported plans (same behavior for each):** Each extract task is wired to a plan directory in `cumulusci.yml`; the task and post-process script are plan-agnostic. Output paths and post-process logic use the plan name derived from the task’s `pathtoexportjson` (e.g. qb-pcm → `extractions/qb-pcm/<timestamp>/`, qb-rating → `extractions/qb-rating/<timestamp>/`). All nine plans (qb-pcm, qb-pricing, qb-product-images, qb-dro, qb-clm, qb-rating, qb-rates, qb-transactionprocessingtypes, qb-guidedselling) are supported; single-pass and multi-pass (objectSets) export.json formats are handled by the post-process script.

### Apex Execution Tasks

| Task Class                      | Module               | Purpose                                              | Use Case                                                                 |
|---------------------------------|----------------------|------------------------------------------------------|--------------------------------------------------------------------------|
| `FileBasedAnonymousApexTask`    | `rlm_apex_file.py`   | Execute large Apex scripts without URI limitations  | Fixes HTTP 414 errors for scripts >8KB; fully compatible with `AnonymousApexTask` |

**Why FileBasedAnonymousApexTask?**

CumulusCI's built-in `AnonymousApexTask` uses the Salesforce Tooling API's `executeAnonymous` endpoint with GET requests, which pass Apex code as URI parameters. This hits HTTP 414 URI Too Long errors for scripts exceeding ~8KB.

`FileBasedAnonymousApexTask` solves this by using `sf apex run --file`, which has no practical size limits and can handle scripts >100KB. It maintains full compatibility with all `AnonymousApexTask` options (path, apex, managed, namespaced, param1, param2) while providing:

- No URI length limitations
- Secure file handling with restricted permissions
- Comprehensive error handling (compilation/runtime errors)
- Support for namespace injection and parameter replacement

Currently used by `activate_rating_records` task for the large [activateRatingRecords.apex](scripts/apex/activateRatingRecords.apex) script (382 lines).

### Metadata Management Tasks

| Task Name | Module | Description | Documentation |
|-----------|--------|-------------|---------------|
| `manage_decision_tables` | `rlm_manage_decision_tables.py` | Decision Table management: list, query, refresh, activate, deactivate, validate_lists | [Decision Table Examples](docs/DECISION_TABLE_EXAMPLES.md) |
| `manage_flows` | `rlm_manage_flows.py` | Flow management (list, query, activate, deactivate) | [Task Examples](docs/TASK_EXAMPLES.md) |
| `manage_expression_sets` | `rlm_manage_expression_sets.py` | Expression Set management: list, query, activate/deactivate versions | [Task Examples](docs/TASK_EXAMPLES.md) |
| `manage_transaction_processing_types` | `rlm_manage_transaction_processing_types.py` | Manage TransactionProcessingType records (list, upsert, delete) | [Constraints Setup](docs/constraints_setup.md) |
| `manage_context_definition` | `rlm_context_service.py` | Modify context definitions via Context Service API | [Context Service Utility](docs/context_service_utility.md) |
| `extend_standard_context` | `rlm_extend_stdctx.py` | Extend standard context definitions with custom attributes | [Context Service Utility](docs/context_service_utility.md) |

### Decision Table Refresh Tasks

| Task Name | Module | Description |
|-----------|--------|-------------|
| `refresh_dt_rating` | `rlm_refresh_decision_table.py` | Refresh rating decision tables |
| `refresh_dt_rating_discovery` | `rlm_refresh_decision_table.py` | Refresh rating discovery decision tables |
| `refresh_dt_default_pricing` | `rlm_refresh_decision_table.py` | Refresh default pricing decision tables |
| `refresh_dt_pricing_discovery` | `rlm_refresh_decision_table.py` | Refresh pricing discovery decision tables |
| `refresh_dt_asset` | `rlm_refresh_decision_table.py` | Refresh asset decision tables |
| `refresh_dt_commerce` | `rlm_refresh_decision_table.py` | Refresh commerce decision tables |

### Deployment & Permissions Tasks

| Task Name | Module | Description |
|-----------|--------|-------------|
| `cleanup_settings_for_dev` | `rlm_cleanup_settings.py` | Remove unsupported settings for dev scratch orgs |
| `exclude_active_decision_tables` | `rlm_exclude_active_decision_tables.py` | Move active decision tables to `.skip` dir before deploy |
| `assign_permission_set_groups_tolerant` | `rlm_assign_permission_set_groups.py` | Assign PSGs with tolerance for missing permissions |
| `recalculate_permission_set_groups` | `rlm_recalculate_permission_set_groups.py` | Recalculate PSGs and wait for Updated status (retries, delays) |

### Activation Tasks

| Task Name | Module | Description |
|-----------|--------|-------------|
| `activate_decision_tables` | `rlm_manage_decision_tables.py` | Activate decision tables |
| `deactivate_decision_tables` | `rlm_manage_decision_tables.py` | Deactivate decision tables |
| `activate_expression_sets` | `rlm_manage_expression_sets.py` | Activate expression sets |
| `deactivate_expression_sets` | `rlm_manage_expression_sets.py` | Deactivate expression sets |
| `activate_default_payment_term` | `rlm_sfdmu.py` | Activate default payment term |
| `activate_billing_records` | `rlm_sfdmu.py` | Activate billing records |
| `activate_tax_records` | `rlm_sfdmu.py` | Activate tax records |
| `activate_price_adjustment_schedules` | `rlm_repair_pricing_schedules.py` | Activate price adjustment schedules |
| `activate_rating_records` | `rlm_apex_file.py` | Activate rating records (uses file-based Apex execution) |
| `activate_rates` | `rlm_sfdmu.py` | Activate rates |

### Data Maintenance Tasks

| Task Name | Module | Description |
|-----------|--------|-------------|
| `delete_quantumbit_pricing_data` | `tasks.rlm_sfdmu.DeleteSFDMUData` | Delete all Insert-operation records from the qb-pricing plan (PriceAdjustmentTier, AttributeAdjustmentCondition, AttributeBasedAdjustment, BundleBasedAdjustment, PricebookEntry, PricebookEntryDerivedPrice) in reverse plan order (children first). Shape-agnostic — reads `export.json` at runtime. Runs automatically as step 1 of `prepare_pricing_data`. |
| `delete_qb_rates_data` | `scripts/apex/deleteQbRatesData.apex` | Delete all qb-rates data (RateAdjustmentByTier, RateCardEntry, PriceBookRateCard, RateCard) in dependency order. Use before re-running `insert_qb_rates_data` or `test_qb_rates_idempotency` when duplicates exist. |
| `delete_qb_rating_data` | `scripts/apex/deleteQbRatingData.apex` | Delete all qb-rating data (PUG, PURP, PUR, rating policies, etc.) in dependency order. Use before re-running `insert_qb_rating_data` when duplicates exist. |
| `delete_draft_billing_records` | `scripts/apex/deleteDraftBillingRecords.apex` | Delete all draft billing-related records (BillingTreatmentItem, BillingTreatment, BillingPolicy, PaymentTermItem, PaymentTerm) in dependency order. Use before re-running the billing data plan to avoid duplicates. |

### Setup & Configuration Tasks

| Task Name | Module | Description | Documentation |
|-----------|--------|-------------|---------------|
| `create_rule_library` | `rlm_sfdmu.py` | Create BRE rule library | See `cumulusci.yml` |
| `create_docgen_library` | `rlm_sfdmu.py` | Create document generation library | See `cumulusci.yml` |
| `create_dro_rule_library` | `rlm_sfdmu.py` | Create DRO rule library | See `cumulusci.yml` |
| `create_tax_engine` | `rlm_sfdmu.py` | Create tax engine records | See `cumulusci.yml` |
| `validate_setup` | `rlm_validate_setup.py` | Validate local developer setup: Python, CumulusCI, Salesforce CLI, SFDMU plugin version, Node.js, Robot Framework, SeleniumLibrary, webdriver-manager, Chrome/Chromium, ChromeDriver, urllib3. Auto-fixes outdated SFDMU when `auto_fix=true`. No org required. | See `cumulusci.yml` |
| `enable_document_builder_toggle` | `rlm_enable_document_builder_toggle.py` | Enable Document Builder, Document Templates Export, and Design Document Templates via Robot Framework browser automation | [Robot Setup README](robot/rlm-base/tests/setup/README.md) |
| `fix_document_template_binaries` | `rlm_docgen.py` | Corrects DocumentTemplate ContentDocument binaries after a batch metadata deploy (Salesforce assigns the same binary to all templates; this task uploads the correct `.dt` binary to each). Run automatically as step 7 of `prepare_docgen`. | [DocGen Setup](docs/docgen_setup.md) |
| `enable_constraints_settings` | `rlm_enable_constraints_settings.py` | Set Default Transaction Type, Asset Context, and enable Constraints Engine toggle via Robot Framework | [Constraints Setup](docs/constraints_setup.md) |
| `configure_revenue_settings` | `rlm_configure_revenue_settings.py` | Configure Revenue Settings: Pricing Procedure, Usage Rating, Instant Pricing toggle, Create Orders Flow (Robot Framework) | See `cumulusci.yml` |
| `reconfigure_pricing_discovery` | `rlm_reconfigure_expression_set.py` | Reconfigure autoproc `Salesforce_Default_Pricing_Discovery_Procedure`: fix context definition, rank, start date | See `cumulusci.yml` |
| `create_procedure_plan_definition` | `rlm_create_procedure_plan_def.py` | Create Procedure Plan Definition + inactive Version via Connect API (idempotent) | [procedure-plans README](datasets/sfdmu/procedure-plans/README.md) |
| `activate_procedure_plan_version` | `rlm_create_procedure_plan_def.py` | Activate ProcedurePlanDefinitionVersion after data load (idempotent) | [procedure-plans README](datasets/sfdmu/procedure-plans/README.md) |
| `deploy_billing_id_settings` | (CCI Deploy) | Deploy Billing Settings with org-specific record IDs resolved via XPath transform SOQL queries | See `cumulusci.yml` |
| `deploy_billing_template_settings` | (CCI Deploy) | Re-enable Invoice Email/PDF toggles to trigger default template auto-creation (cycle step 3) | See `cumulusci.yml` |
| `ensure_pricing_schedules` | `rlm_repair_pricing_schedules.py` | Ensure pricing schedules exist before expression set deploy | See `cumulusci.yml` |

### Using Custom Tasks

All custom tasks are automatically available via CumulusCI. Use them like any standard CCI task:

```bash
# List decision tables (includes UsageType)
cci task run manage_decision_tables --operation list

# Validate decision table lists vs org
cci task run manage_decision_tables --operation validate_lists

# Manage flows
cci task run manage_flows --operation list --process_type ScreenFlow

# Manage expression sets
cci task run manage_expression_sets --operation list

# Export a constraint model
cci task run export_cml --org <org> -o developer_name QuantumBitComplete -o version 1 -o output_dir datasets/constraints/qb/QuantumBitComplete

# Import a constraint model (with dry run)
cci task run import_cml --org <org> -o data_dir datasets/constraints/qb/QuantumBitComplete -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm" -o dry_run true

# Validate CML files
cci task run validate_cml -o cml_dir scripts/cml -o data_dir datasets/constraints/qb/QuantumBitComplete
```

For detailed examples and usage, see:
- [Decision Table Examples](docs/DECISION_TABLE_EXAMPLES.md)
- [Flow and Expression Set Examples](docs/TASK_EXAMPLES.md)
- [Constraints Utility Guide](datasets/constraints/README.md)

### Custom Task Development

Custom tasks are Python modules in the `tasks/` directory. They inherit from CumulusCI's `BaseTask` (or `BaseSalesforceTask` for org-connected tasks) and are automatically discovered by CumulusCI.

To add a new custom task:
1. Create a Python file in `tasks/` (e.g., `tasks/rlm_my_task.py`)
2. Define your task class inheriting from the appropriate base
3. Add task configuration to `cumulusci.yml` under `tasks:`
4. Reference the task in flows or run directly

Example task structure:
```python
from cumulusci.core.tasks import BaseTask
from cumulusci.core.exceptions import TaskOptionsError

class MyCustomTask(BaseTask):
    task_options = {
        "option1": {"description": "Description", "required": True}
    }
    
    def _run_task(self):
        # Task implementation
        pass
```

For tasks that need Salesforce org access (REST API, SOQL, etc.):
```python
from cumulusci.tasks.salesforce import BaseSalesforceTask

class MyOrgTask(BaseSalesforceTask):
    task_options = {
        "option1": {"description": "Description", "required": True}
    }
    
    def _run_task(self):
        # self.org_config provides access_token, instance_url, etc.
        pass
```

## Flows

All flows belong to the **Revenue Lifecycle Management** group. The main orchestration flow is `prepare_rlm_org`, which calls sub-flows in sequence.

### Main Orchestration

| Flow | Description |
|------|-------------|
| `prepare_rlm_org` | **Master flow** -- runs all sub-flows in order (29 steps). This is the primary flow for full org setup. |

#### prepare_rlm_org Step Order

| Step | Flow/Task | Condition |
|------|-----------|-----------|
| 1 | `prepare_core` | Always |
| 2 | `prepare_decision_tables` | Always |
| 3 | `prepare_expression_sets` | Always |
| 4 | `create_partner_central` | `prm` |
| 5 | `create_payments_webhook` | `payments` |
| 6 | `deploy_full` | Always |
| 7 | `prepare_price_adjustment_schedules` | Always |
| 8 | `prepare_scratch` | Always |
| 9 | `prepare_payments` | Always |
| 10 | `prepare_quantumbit` | Always |
| 11 | `prepare_product_data` | Always |
| 12 | `prepare_pricing_data` | Always |
| 13 | `prepare_docgen` | Always |
| 14 | `prepare_dro` | Always |
| 15 | `prepare_tax` | Always |
| 16 | `prepare_billing` | Always |
| 17 | `prepare_clm` | Always |
| 18 | `prepare_rating` | Always |
| 19 | `activate_and_deploy_expression_sets` | Always |
| 20 | `prepare_tso` | Always |
| 21 | `prepare_procedureplans` | Always |
| 22 | `prepare_prm` | Always |
| 23 | `prepare_agents` | Always |
| 24 | `prepare_constraints` | Always |
| 25 | `prepare_guidedselling` | Always |
| 26 | `prepare_visualization` | Always |
| 27 | `configure_revenue_settings` | Always |
| 28 | `reconfigure_pricing_discovery` | Always |
| 29 | `refresh_all_decision_tables` | Always |

> **Note:** "Always" means the flow/task runs as a step, but individual tasks inside each sub-flow may be gated by feature flags.

### Data Management flows

Use these flows to run all QB extract tasks or all QB idempotency tests by group:

| Flow | Description |
|------|-------------|
| `run_qb_extracts` | Runs all 9 Data Management - Extract tasks (extract_qb_pcm_data, extract_qb_pricing_data, extract_qb_product_images_data, extract_qb_dro_data, extract_qb_clm_data, extract_qb_rating_data, extract_qb_rates_data, extract_qb_transactionprocessingtypes_data, extract_qb_guidedselling_data). Requires `--org`. Output in `datasets/sfdmu/extractions/<plan>/<timestamp>/`. |
| `run_qb_idempotency_tests` | Runs all 9 Data Management - Idempotency tasks (test_qb_*_idempotency for the same plans). Loads each plan twice and fails if any object's record count increases. qb-pcm uses extraction roundtrip by default. Requires `--org`. |

See [Data Management Tasks](#data-management-tasks) for per-task details and group listing.

### Sub-Flows

| Flow | Description | Key Feature Flags |
|------|-------------|-------------------|
| `prepare_core` | PSL/PSG assignment, context definitions, rule libraries, settings cleanup | `clm`, `einstein`, `dro`, `breconfig`, `billing` |
| `extend_context_definitions` | Extend all standard context definitions | `commerce`, `billing`, `dro`, `clm`, `rating` |
| `prepare_expression_sets` | Deactivate, ensure pricing schedules, deploy expression sets | Scratch only |
| `prepare_product_data` | Load PCM + product image SFDMU data | `qb`, `q3` |
| `prepare_pricing_data` | Load pricing SFDMU data | `qb` |
| `prepare_scratch` | Insert scratch-only data | Scratch only, not `tso` |
| `prepare_quantumbit` | Deploy QuantumBit metadata, permissions, CALM delete | `quantumbit`, `billing`, `approvals`, `calmdelete` |
| `prepare_tso` | TSO-specific PSL/PSG/permissions/metadata | `tso` |
| `prepare_dro` | Load DRO data (dynamic user resolution), PFDR update (260 bug fix) | `dro`, `qb`, `q3` |
| `prepare_clm` | Load CLM data | `clm`, `clm_data` |
| `prepare_docgen` | Create docgen library, enable Document Builder + Document Templates Export + Design Document Templates toggles, deploy metadata | `docgen` |
| `prepare_billing` | Load billing data, activate flows/records, deploy ID-based settings via XPath transforms, trigger default template auto-creation (3-step cycle) | `billing`, `qb`, `q3`, `refresh` |
| `prepare_prm` | Deploy PRM metadata, publish community, sharing rules, assign RLM_PRM permission set, load PRM data | `prm`, `prm_exp_bundle`, `sharingsettings`, `qb` |
| `prepare_tax` | Create tax engine, load data, activate records | `tax`, `qb`, `q3`, `refresh` |
| `prepare_rating` | Load rating + rates data, activate | `rating`, `rates`, `qb`, `q3`, `refresh` |
| `extract_rating` | Extract rating and rates data from an org | -- |
| `prepare_agents` | Deploy Agentforce agents, settings, permissions | `agents` |
| `refresh_all_decision_tables` | Sync pricing, refresh all DT categories | `rating`, `commerce` |
| `prepare_decision_tables` | Activate decision tables | Scratch only |
| `prepare_price_adjustment_schedules` | Activate price adjustment schedules | Scratch only |
| `prepare_procedureplans` | Deploy procedure plans metadata + `skipOrgSttPricing` setting, create PPD via Connect API, load sections/options, activate | `procedureplans` |
| `prepare_constraints` | Load TransactionProcessingTypes, deploy metadata, configure settings, import CML models, activate | `constraints`, `constraints_data`, `qb` |
| `prepare_guidedselling` | Load guided selling data, deploy metadata | `guidedselling`, `qb` |
| `prepare_visualization` | Deploy visualization components | `visualization` |
| `prepare_payments` | Deploy payments site, publish community, deploy settings | `payments` |

### Utility Flows and Tasks

| Flow/Task | Type | Description |
|-----------|------|-------------|
| `deploy_full` | Task | Full metadata deployment (source, pre/post bundles) |
| `activate_and_deploy_expression_sets` | Task | Re-deploy expression sets with Draft status transformed to Active via XPath |

## Data Plans

Data plans provide the reference data loaded during org setup. This project uses two mechanisms:

### SFDMU Data Plans

> **Requires SFDMU v5.0.0+.** All data plans have been migrated for SFDMU v5 compatibility
> and idempotency. See [Composite Key Optimizations](docs/sfdmu_composite_key_optimizations.md)
> for the full migration details and known limitations.

SFDMU data plans are located under `datasets/sfdmu/` and are loaded by the `load_sfdmu_data` task infrastructure. Each plan contains an `export.json` defining the objects, fields, and ordering for SFDMU.

#### Validating SFDMU Data Plans

The project includes `scripts/validate_sfdmu_v5_datasets.py` for validating SFDMU v5 compliance:

**Validation:**

```bash
# Validate all SFDMU datasets
python scripts/validate_sfdmu_v5_datasets.py

# Validate specific dataset
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb/en-US/qb-billing

# Validate all QB datasets
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb

# Generate report file
python scripts/validate_sfdmu_v5_datasets.py --output docs/sfdmu_v5_validation_report.md
```

**Automatic Fixes:**

```bash
# Fix empty CSV headers
python scripts/validate_sfdmu_v5_datasets.py --fix-headers

# Fix missing composite key columns
python scripts/validate_sfdmu_v5_datasets.py --fix-composite-keys

# Fix all issues (dry-run first recommended)
python scripts/validate_sfdmu_v5_datasets.py --fix-all --dry-run
python scripts/validate_sfdmu_v5_datasets.py --fix-all
```

The validator checks for:

- Legacy `$$` notation in externalId definitions (v5 requires semicolon format)
- Missing composite key columns in CSVs
- Empty CSV files without headers
- Nested relationship paths that cause v5 flattening errors

To generate a validation report:

```bash
# Console output
python scripts/validate_sfdmu_v5_datasets.py

# Save to file
python scripts/validate_sfdmu_v5_datasets.py --output validation_report.md
```

#### Data plan directory structure

Plans follow a **shape / locale / plan-name** tree so multiple data shapes (e.g. QuantumBit, Manufacturing) can coexist:

```
datasets/sfdmu/
├── <shape>/           # e.g. qb, mfg, q3
│   └── <locale>/      # e.g. en-US
│       └── <plan-name>/   # e.g. qb-pcm, mfg-pcm
│           ├── export.json
│           ├── Object1.csv
│           ├── Object2.csv
│           └── (optional) objectset_source/   # for multi-pass plans
├── procedure-plans/
└── extractions/       # extract output: <plan-name>/<timestamp>/ and .../processed/
```

**Examples:** `datasets/sfdmu/qb/en-US/qb-pcm`, `datasets/sfdmu/mfg/en-US/mfg-pcm`. The same tooling (extract task, post-process script, idempotency task) works for any plan path: each task gets its plan directory from `cumulusci.yml` via a path anchor, and extraction output goes to `datasets/sfdmu/extractions/<plan-name>/<timestamp>/` (and `<timestamp>/processed/` after post-process).

**Adding a new data shape (e.g. mfg):**

1. Create the directory tree: `datasets/sfdmu/mfg/en-US/<plan-name>/` (e.g. `mfg-pcm`).
2. Add `export.json` and CSV files following the same patterns as QB (single-pass with flat `objects`, or multi-pass with `objectSets`; see [qb-pcm](datasets/sfdmu/qb/en-US/qb-pcm/README.md) or [qb-rating](datasets/sfdmu/qb/en-US/qb-rating/README.md) as reference).
3. In `cumulusci.yml`, under **DATA PLAN NAMES AND PATHS**, add an anchor (e.g. `mfg_pcm_dataset: &mfg_pcm_dataset "datasets/sfdmu/mfg/en-US/mfg-pcm"`).
4. Add load, extract, and idempotency tasks that reference that anchor (`pathtoexportjson: *mfg_pcm_dataset`). Use the same task classes (`LoadSFDMUData`, `ExtractSFDMUData`, `TestSFDMUIdempotency`) and groups (Data Management - Extract / Idempotency) so extract runs post-process by default and output goes to `extractions/mfg-pcm/<timestamp>/processed/`.
5. Add a README in the plan directory and, if desired, list the plan in the table below.

#### QuantumBit (QB) Data Plans

| Data Plan | Directory | Description | Documentation |
|-----------|-----------|-------------|---------------|
| qb-pcm | `datasets/sfdmu/qb/en-US/qb-pcm/` | Product Catalog Management -- products, classifications, components, attributes | [README](datasets/sfdmu/qb/en-US/qb-pcm/README.md) |
| qb-product-images | `datasets/sfdmu/qb/en-US/qb-product-images/` | Product images and content document links | [README](datasets/sfdmu/qb/en-US/qb-product-images/README.md) |
| qb-pricing | `datasets/sfdmu/qb/en-US/qb-pricing/` | Pricing data (pricebook entries, price adjustments) | [README](datasets/sfdmu/qb/en-US/qb-pricing/README.md) |
| qb-tax | `datasets/sfdmu/qb/en-US/qb-tax/` | Tax engine data (tax treatments, policies) | [README](datasets/sfdmu/qb/en-US/qb-tax/README.md) |
| qb-billing | `datasets/sfdmu/qb/en-US/qb-billing/` | Billing data (billing terms, schedules) | [README](datasets/sfdmu/qb/en-US/qb-billing/README.md) |
| qb-dro | `datasets/sfdmu/qb/en-US/qb-dro/` | Dynamic Revenue Orchestration plans | [README](datasets/sfdmu/qb/en-US/qb-dro/README.md) |
| qb-transactionprocessingtypes | `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/` | Transaction Processing Type records | [README](datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/README.md) |
| qb-rating | `datasets/sfdmu/qb/en-US/qb-rating/` | Rating design-time data | [README](datasets/sfdmu/qb/en-US/qb-rating/README.md) |
| qb-rates | `datasets/sfdmu/qb/en-US/qb-rates/` | Rates data | [README](datasets/sfdmu/qb/en-US/qb-rates/README.md) |
| qb-prm | `datasets/sfdmu/qb/en-US/qb-prm/` | Partner Relationship Management (channel programs, levels, members) | [README](datasets/sfdmu/qb/en-US/qb-prm/README.md) |

#### Procedure Plans Data Plan

| Data Plan | Directory | Description | Documentation |
|-----------|-----------|-------------|---------------|
| procedure-plans | `datasets/sfdmu/procedure-plans/` | Procedure Plan sections and options with expression set links (2-pass upsert + Connect API + activation) | [README](datasets/sfdmu/procedure-plans/README.md) |

#### Archived Data Plans

Deprecated data plans are retained in `datasets/sfdmu/_archived/` for reference. These are no longer used:

- `qb-constraints-product` -- replaced by CML utility
- `qb-constraints-component` -- replaced by CML utility
- `qb-constraints-consolidated` -- replaced by CML utility
- `qb-constraints-prc-aisummit` -- replaced by CML utility

### Constraint Model Data Plans

Constraint model data is managed by the Python-based CML utility (`tasks/rlm_cml.py`) instead of SFDMU. These plans are stored under `datasets/constraints/` and include CSVs for Expression Sets, ESC associations, and binary ConstraintModel blobs.

| Model | Directory | ESC Records | Documentation |
|-------|-----------|-------------|---------------|
| QuantumBitComplete | `datasets/constraints/qb/QuantumBitComplete/` | 43 | [Constraints Utility Guide](datasets/constraints/README.md) |
| Server2 | `datasets/constraints/qb/Server2/` | 81 | [Constraints Utility Guide](datasets/constraints/README.md) |

For details on exporting new models, importing into target orgs, polymorphic ID resolution, and CCI integration, see the [Constraints Utility Guide](datasets/constraints/README.md).

## Documentation

### Primary Guides

| Document | Description |
|----------|-------------|
| [Constraints Utility Guide](datasets/constraints/README.md) | CML constraint model export, import, validate -- architecture, workflows, polymorphic resolution |
| [Constraints Setup](docs/constraints_setup.md) | `prepare_constraints` flow order, feature flags, deployment phases |
| [Decision Table Examples](docs/DECISION_TABLE_EXAMPLES.md) | Comprehensive examples for Decision Table management tasks |
| [Task Examples](docs/TASK_EXAMPLES.md) | Examples for Flow and Expression Set management tasks |
| [Context Service Utility](docs/context_service_utility.md) | Context Service utility usage and plan examples |
| [DocGen Setup](docs/docgen_setup.md) | Document Generation architecture, deployment flow, Metadata API binary bug, seller token implementation |

### Analysis & Planning

| Document | Description |
|----------|-------------|
| [Tooling Opportunities](docs/TOOLING_OPPORTUNITIES.md) | Analysis of Spring '26 features and opportunities for new tooling tasks |
| [Composite Key Optimizations](docs/sfdmu_composite_key_optimizations.md) | SFDMU v5 migration, composite key analysis, idempotency verification |
| [RCA/RCB Unique ID Fields](docs/rca_rcb_unique_id_fields.md) | Unique ID field analysis for Revenue Cloud objects |

### SFDMU Data Plan READMEs

Each SFDMU data plan has its own detailed README documenting objects, fields, load order, external IDs, and optimization opportunities:

- [qb-pcm README](datasets/sfdmu/qb/en-US/qb-pcm/README.md) -- Product Catalog Management
- [qb-product-images README](datasets/sfdmu/qb/en-US/qb-product-images/README.md) -- Product Images
- [qb-pricing README](datasets/sfdmu/qb/en-US/qb-pricing/README.md) -- Pricing
- [qb-tax README](datasets/sfdmu/qb/en-US/qb-tax/README.md) -- Tax
- [qb-billing README](datasets/sfdmu/qb/en-US/qb-billing/README.md) -- Billing
- [qb-dro README](datasets/sfdmu/qb/en-US/qb-dro/README.md) -- Dynamic Revenue Orchestration
- [qb-transactionprocessingtypes README](datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/README.md) -- Transaction Processing Types
- [qb-rating README](datasets/sfdmu/qb/en-US/qb-rating/README.md) -- Rating
- [qb-rates README](datasets/sfdmu/qb/en-US/qb-rates/README.md) -- Rates
- [qb-prm README](datasets/sfdmu/qb/en-US/qb-prm/README.md) -- Partner Relationship Management
- [procedure-plans README](datasets/sfdmu/procedure-plans/README.md) -- Procedure Plans
- [mfg README](datasets/sfdmu/mfg/README.md) -- Manufacturing data shape (add plans under mfg/en-US/; same patterns as qb)

### Robot Framework

- [Robot Setup README](robot/rlm-base/tests/setup/README.md) -- Browser automation for setup page toggles and picklists (Document Builder, Constraints Settings, Revenue Settings)

### Configuration Files

- **`cumulusci.yml`** -- Main CumulusCI configuration with all tasks, flows, and project settings
- **`sfdx-project.json`** -- Salesforce DX project configuration
- **`orgs/`** -- Scratch org definition files for different scenarios

## Project Structure

```
rlm-base-dev/
├── force-app/                  # Main Salesforce metadata (source format)
├── unpackaged/                 # Conditional metadata (deployed based on flags)
│   ├── pre/                    # Pre-deployment metadata
│   │   └── 5_decisiontables/   # Decision tables (active ones auto-excluded)
│   ├── post_approvals/         # Approvals metadata
│   ├── post_billing/           # Billing metadata (toggles, flexipages, billingContextDefinition)
│   ├── post_billing_id_settings/ # Billing settings with org-specific record IDs (XPath transforms)
│   ├── post_billing_template_settings/ # Re-enable invoice toggles (template auto-creation cycle step 3)
│   ├── post_commerce/          # Commerce metadata
│   ├── post_constraints/       # Constraints metadata
│   ├── post_docgen/            # Document Generation metadata
│   ├── post_guidedselling/     # Guided Selling metadata
│   ├── post_payments/          # Payments metadata
│   ├── post_prm/               # Partner Relationship Management metadata
│   ├── post_procedureplans/    # Procedure Plans metadata + RevenueManagement.settings (skipOrgSttPricing)
│   ├── post_scratch/           # Scratch org-only metadata
│   ├── post_tso/               # TSO-specific metadata
│   ├── post_utils/             # Utility metadata
│   └── post_visualization/     # Visualization metadata
├── tasks/                      # Custom CumulusCI Python task modules
│   ├── rlm_cml.py              # CML constraint utility (ExportCML, ImportCML, ValidateCML)
│   ├── rlm_sfdmu.py            # SFDMU data loading tasks
│   ├── rlm_manage_decision_tables.py
│   ├── rlm_manage_expression_sets.py
│   ├── rlm_manage_flows.py
│   ├── rlm_manage_transaction_processing_types.py
│   ├── rlm_context_service.py
│   ├── rlm_extend_stdctx.py
│   ├── rlm_enable_document_builder_toggle.py
│   ├── rlm_enable_constraints_settings.py
│   ├── rlm_configure_revenue_settings.py
│   ├── rlm_reconfigure_expression_set.py
│   ├── rlm_create_procedure_plan_def.py
│   ├── rlm_refresh_decision_table.py
│   ├── rlm_sync_pricing_data.py
│   ├── rlm_repair_pricing_schedules.py
│   ├── rlm_cleanup_settings.py
│   ├── rlm_assign_permission_set_groups.py
│   ├── rlm_recalculate_permission_set_groups.py
│   ├── rlm_exclude_active_decision_tables.py
│   ├── rlm_modify_context.py
│   └── sfdmuload.py
├── robot/                      # Robot Framework tests
│   └── rlm-base/
│       ├── resources/          # Keywords, WebDriverManager helper
│       ├── tests/setup/        # Setup page automation (Document Builder, Constraints, Revenue Settings)
│       └── results/            # Runtime output (gitignored)
├── datasets/                   # Data plans
│   ├── sfdmu/                  # SFDMU data plans
│   │   ├── qb/en-US/           # QuantumBit data shape (10 active plans)
│   │   │   ├── qb-pcm/
│   │   │   ├── qb-product-images/
│   │   │   ├── qb-pricing/
│   │   │   ├── qb-tax/
│   │   │   ├── qb-billing/
│   │   │   ├── qb-dro/
│   │   │   ├── qb-transactionprocessingtypes/
│   │   │   ├── qb-rating/
│   │   │   ├── qb-rates/
│   │   │   └── qb-prm/
│   │   ├── mfg/en-US/          # Manufacturing data shape (e.g. mfg-pcm) — same patterns as qb
│   │   ├── procedure-plans/    # Procedure Plans data plan (sections + options)
│   │   └── _archived/          # Deprecated SFDMU plans (constraints attempts)
│   ├── constraints/            # CML constraint model data plans
│   │   ├── qb/
│   │   │   ├── QuantumBitComplete/
│   │   │   └── Server2/
│   │   └── README.md           # Constraints utility guide
│   └── context_plans/          # Context definition update plans (JSON manifests)
│       ├── ConstraintEngineNodeStatus/  # Adds ConstraintEngineNodeStatus to SalesTransaction context
│       │   ├── manifest.json
│       │   └── contexts/
│       └── archive/            # Archived/previous context plans
├── scripts/                    # Utility scripts
│   ├── apex/                   # Anonymous Apex scripts
│   ├── cml/                    # CML source files (.cml) and deprecated Python scripts
│   └── bash/                   # Bash scripts
├── docs/                       # Documentation
│   ├── constraints_setup.md
│   ├── DECISION_TABLE_EXAMPLES.md
│   ├── TASK_EXAMPLES.md
│   ├── context_service_utility.md
│   ├── TOOLING_OPPORTUNITIES.md
│   ├── sfdmu_composite_key_optimizations.md
│   └── rca_rcb_unique_id_fields.md
├── orgs/                       # Scratch org definitions
├── cumulusci.yml               # CumulusCI configuration
├── sfdx-project.json           # Salesforce DX configuration
└── README.md                   # This file
```

## Common Workflows

### Full Org Setup

```bash
# 1. Create scratch org
cci org scratch dev my-org

# 2. Set as default
cci org default my-org

# 3. Run full deployment flow
cci flow run prepare_rlm_org
```

### Deploy Specific Features

```bash
# Enable a feature flag in cumulusci.yml, then:
cci flow run prepare_rlm_org
```

### Prepare Constraints (with Data)

```bash
# Run constraints flow with CML data loading enabled
cci flow run prepare_constraints --org <org> -o constraints_data true
```

This will validate CML files, import both QuantumBitComplete and Server2 models, and activate their expression sets. See [Constraints Setup](docs/constraints_setup.md) for flow details.

### Export a Constraint Model

```bash
# Export from a source org to a local data plan directory
cci task run export_cml --org <source_org> \
    -o developer_name QuantumBitComplete \
    -o version 1 \
    -o output_dir datasets/constraints/qb/QuantumBitComplete
```

See the [Constraints Utility Guide](datasets/constraints/README.md) for full export/import/validate documentation.

### Load Product Data

```bash
# Load QuantumBit PCM data
cci task run insert_quantumbit_pcm_data

# Load product images
cci task run insert_quantumbit_product_image_data
```

### Load Billing Data

```bash
cci task run insert_billing_data
```

The `prepare_billing` flow deploys Billing Settings in a 3-step cycle to properly configure ID-based fields and trigger default template auto-creation:

1. **Step 6** (`deploy_post_billing`): Enable billing toggles (`enableInvoiceEmailDelivery`, `enableInvoicePdfGeneration` = `true`) and set `billingContextDefinition`
2. **Step 7** (`deploy_billing_id_settings`): Set context mapping, DPE definition names, and record IDs via XPath transforms; disable invoice toggles (`false`)
3. **Step 8** (`deploy_billing_template_settings`): Re-enable invoice toggles (`true`) to trigger Salesforce auto-creation of default invoice preview and document templates

The ID fields (`defaultBillingTreatment`, `defaultLegalEntity`, `defaultTaxTreatment`) use XPath transform SOQL queries to resolve org-specific record IDs at deploy time. The `billingContextDefinition` must be deployed in step 6 (before step 7) because `billingContextSourceMapping` requires it to already be persisted.

DRO data (prepare_dro flow) uses a single **qb-dro** data plan for both scratch and non-scratch orgs. The task replaces the placeholder `__DRO_ASSIGNED_TO_USER__` in `FulfillmentStepDefinition.csv`, `User.csv`, and `UserAndGroup.csv` with the target org's default user Name (e.g. "User User" in scratch orgs, "Admin User" in TSO) before loading. Step 4 runs `update_product_fulfillment_decomp_rules` (Apex) as a temporary fix for a 260 bug: ExecuteOnRuleId is not generated on INSERT and must be triggered by an UPDATE. No separate scratch-specific DRO plan is required.

### Extract Rating Data

```bash
# Extract rating and rates data from an org
cci flow run extract_rating --org <org>
```

### Manage Decision Tables

```bash
# List all active decision tables (with UsageType)
cci task run manage_decision_tables --operation list

# Validate project list anchors against the org
cci task run manage_decision_tables --operation validate_lists

# Refresh all decision tables (full or incremental)
cci task run manage_decision_tables --operation refresh
# Or use the flow: cci flow run refresh_all_decision_tables
```
Decision table activate/deactivate and expression set version activation use CCI tasks only; the former SFDMU data plans for these have been removed.

## Troubleshooting

### Fixing a global pip install (headless robot tasks)

If you installed Robot Framework or SeleniumLibrary with `pip install` and got a warning about modifying the global environment:

1. Uninstall from the Python you used:
   ```bash
   python3 -m pip uninstall -y robotframework-seleniumlibrary robotframework webdriver-manager
   ```
2. Install them into CumulusCI's environment so headless robot tasks can run. If you use **pipx** for CumulusCI:
   ```bash
   pipx inject cumulusci robotframework robotframework-seleniumlibrary webdriver-manager "urllib3>=2.6.3"
   ```
3. Run `cci task run validate_setup` to confirm all headless robot dependencies (Robot, SeleniumLibrary, webdriver-manager, Chrome/Chromium, ChromeDriver). Once the org is ready, run the task to confirm end-to-end.

### Headless robot: Chrome/Chromium or ChromeDriver not found

Robot tasks run headless and require Chrome or Chromium plus ChromeDriver. Run `cci task run validate_setup` to diagnose. Common fixes:

- **Chrome/Chromium missing:** Install per [Setup for headless robot runs](#setup-for-headless-robot-runs) (macOS: `brew install chromium`; Linux: `apt install chromium`).
- **ChromeDriver missing:** Install webdriver-manager (`pipx inject cumulusci webdriver-manager`) so it downloads ChromeDriver at runtime, or install chromedriver on PATH (e.g. `apt install chromium-driver` on Debian/Ubuntu).
- **CI:** Set `CHROME_BIN` to the browser path (e.g. `/usr/bin/chromium`).

### Document Builder: "Timeout value connect was &lt;object object at ...&gt;"

This is a Selenium 3.x / urllib3 2.x compatibility issue. Selenium 3.x passes `socket._GLOBAL_DEFAULT_TIMEOUT` (a sentinel `object()`) to `urllib3.PoolManager`, which urllib3 2.x rejects. The project's `WebDriverManager.py` patches `RemoteConnection._timeout` at import time to resolve this automatically. If you still encounter it, ensure your Robot dependencies are up to date:

```bash
pipx inject cumulusci -r robot/requirements.txt --force
```

Use `--force` to upgrade existing packages. CumulusCI currently pins `selenium<4`, so the automatic patch in `WebDriverManager.py` is required for urllib3 2.x compatibility. Then re-run the Document Builder task or flow.

### CumulusCI Not Found

```bash
# Install CumulusCI (prefer pipx to avoid global Python install)
pipx install cumulusci
# If you don't use pipx, use a virtual environment first, then: pip install cumulusci

# Verify installation
cci version
```

### SFDMU Not Found or Outdated

```bash
# Install or update SFDMU (v5+ required)
sf plugins install sfdmu

# Verify installation (should show 5.x)
sf plugins list
```

The `validate_setup` task checks and auto-updates SFDMU when `auto_fix=true` (the default):
```bash
cci task run validate_setup
```

### SFDMU Duplicate Records on Re-run

If you see duplicate records after running data tasks multiple times, verify you are on
SFDMU v5. The data plans have been migrated for v5 idempotency; v4.x may create duplicates
due to differences in how composite `externalId` definitions are processed. See
[Composite Key Optimizations](docs/sfdmu_composite_key_optimizations.md) for details.

### Permission Set Groups stuck Outdated / Updating

- After assigning permission set licenses or deploying PSG metadata, the platform may queue recalculation. The `recalculate_permission_set_groups` task waits with an initial delay, polls for Updated status, and retries with a delay on timeout (see `initial_delay_seconds`, `retry_count`, `retry_delay_seconds`, `post_trigger_delay_seconds` in `cumulusci.yml`). If you still hit timeouts, increase those options or run the flow again once the org has finished recalculating.

### Permission Errors

- Ensure your Salesforce user has appropriate permissions
- For scratch orgs, ensure Dev Hub is enabled
- Check org access: `sf org display`

### Deployment Errors

- Check feature flags in `cumulusci.yml` match your org's capabilities
- Review deployment logs for specific error messages
- Some features require specific licenses (e.g., Einstein, QuantumBit)

### Constraint Import Errors

- **MALFORMED_QUERY**: Product names with special characters (single quotes, backslashes) can cause SOQL issues. The CML utility automatically escapes these, but if you encounter this error, check that you're using the latest `tasks/rlm_cml.py`.
- **NOT_FOUND for ExpressionSetConstraintObj**: The target org may not have the RLM Constraints feature enabled. Enable it in Setup before running the import.
- **Could not resolve ReferenceObjectId**: The target org is missing products or PRC records that the constraint model references. Ensure the product data plan (e.g., `qb-pcm`) has been loaded first.

## Contributing

When contributing to this project:

1. Follow the existing code structure and patterns
2. Document custom tasks in `cumulusci.yml` and create example documentation
3. Test changes with appropriate scratch org configurations
4. Update this README if adding new prerequisites or workflows
5. Add detailed READMEs for new data plans
6. Register new tasks and flows in `cumulusci.yml`

## Branch Information

- **main**: Salesforce Release 260 (Spring '26, GA)
- Other branches exist for different release scenarios and preview features

## Additional Resources

- [CumulusCI Documentation](https://cumulusci.readthedocs.io/)
- [Salesforce CLI Documentation](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/)
- [SFDMU Documentation](https://help.sfdmu.com/)
- [Revenue Cloud Developer Guide (Release 260)](https://developer.salesforce.com/docs/atlas.en-us.260.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm)
- [Revenue Cloud Help Documentation](https://help.salesforce.com/s/articleView?id=ind.revenue_lifecycle_management_get_started.htm&type=5)

**Note:** This project works with all Revenue Cloud capabilities documented in both the Developer Guide and Help Documentation for Release 260 (Spring '26).

## License

[Add your license information here]
