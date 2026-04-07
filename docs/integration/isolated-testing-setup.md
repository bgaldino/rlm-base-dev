# Distill & Aegis: Isolated Testing Setup Guide

> **Purpose:** Stand up Distill and Aegis locally for independent validation before beginning integration work with Revenue Cloud Foundations.
> **Last Updated:** 2026-04-07
> **Part of:** [Revenue Cloud Engineering Platform](revenue-cloud-platform.md)
>
> **Prerequisite:** A Foundations-provisioned Salesforce org (via `cci flow run prepare_rlm_org --org <alias>`) for Aegis testing. Distill can be tested independently.

---

## Agent-Assisted Setup

This document is designed for an AI coding agent (Cursor, Claude Code, etc.) to follow end-to-end. You can set up both platforms, or just one.

### Setup Scope

Not every user needs both Distill and Aegis. Choose the scope that matches your goal:

| Scope | What gets installed | Prerequisites skipped |
|---|---|---|
| **Both** (default) | Distill + Aegis + shared prereqs | Nothing skipped |
| **Distill only** | Distill + shared prereqs | Sections 3, 4.2, 4.3; no Chrome/Playwright, no SF credentials, no VPN |
| **Aegis only** | Aegis + shared prereqs | Sections 2, 4.1; no gcloud, cmake, Embark, Gemini API key |

**Shared prerequisites** (always needed): git, pyenv, Python 3.12, Homebrew (macOS).

### Example Prompts

> **Both Distill and Aegis** — paste this to set up the full integration workspace:

```
Follow the setup guide at docs/integration/isolated-testing-setup.md to set up
the Distill and Aegis integration workspace on my machine.

Scope: both

Rules:
- Do NOT install, modify, or delete anything without showing me what you plan
  to do and getting my explicit approval first.
- Before each step, check whether the tool/repo/config already exists and skip
  it if so. Use the validation script in --scan mode as the first step.
- If you detect conflicts (wrong Python version in a venv, PATH shadowing,
  etc.), explain the conflict and proposed resolution, then wait for my approval.
- Work through the guide section by section (0 → 1 → 2 → 3 → 4). Do not jump
  ahead. Skip sections not applicable to the chosen scope.
- For any step that requires credentials or API keys (GEMINI_API_KEY, SF_URL,
  etc.), prompt me to provide them rather than using placeholders.
- If a step fails, stop and show me the error rather than retrying automatically.
- Do NOT modify my shell profile (~/.zshrc, ~/.bashrc) without showing me the
  exact lines and getting approval.
- Summarize what was completed at the end of each major section.
```

> **Distill only:**

```
Follow the setup guide at docs/integration/isolated-testing-setup.md to set up
Distill on my machine.

Scope: distill-only

Follow the same rules as the full setup, but skip all Aegis sections (3, 4.2,
4.3). Skip Chrome/Playwright, SF credentials, and VPN checks in prerequisites.
Only clone the foundations and distill repos in Section 1.
```

> **Aegis only:**

```
Follow the setup guide at docs/integration/isolated-testing-setup.md to set up
Aegis on my machine.

Scope: aegis-only

Follow the same rules as the full setup, but skip all Distill sections (2, 4.1).
Skip gcloud, cmake, Embark GCP project, and Gemini API key in prerequisites.
Only clone the foundations and aegis repos in Section 1.
```

> **No prompt — agent should ask:** If the user simply says *"set up my integration environment"* without specifying scope, the agent should ask:
>
> *"Which platforms do you want to set up? (1) Both Distill and Aegis, (2) Distill only, (3) Aegis only"*

### How the Agent Should Execute This Guide

The guide is structured so an agent can follow it linearly. Each section builds on the previous one. Sections marked with a scope tag should be skipped if that scope doesn't apply.

```
Section 0: Prerequisites
  ├─ 0.1-0.3: Always (shared prereqs: git, pyenv, Python 3.12)
  ├─ 0.4: Always (nvm/Node — Foundations needs it regardless of scope)
  ├─ 0.5: Distill only — skip entirely for aegis-only scope
  │       (Embark, gcloud, cmake, Gemini API key, Claude cleanup)
  ├─ 0.6: Always (run validation script)
  └─ 0.7: Always (resolve conflicts)

Section 1: Workspace Setup
  ├─ Clone foundations: Always
  ├─ Clone distill: Skip for aegis-only
  ├─ Clone aegis: Skip for distill-only (also needs VPN)
  └─ Pin Python versions: Only for repos that were cloned

Section 2: Distill Local Setup — skip entirely for aegis-only
  ├─ Install dependencies
  ├─ Configure .env.local + credential checkpoint
  └─ Database initialization

Section 3: Aegis Local Setup — skip entirely for distill-only
  ├─ Install dependencies + Playwright
  └─ Configure credentials + credential checkpoint

Section 4: Post-Setup Validation
  ├─ 4.1: Distill validation — skip for aegis-only
  ├─ 4.2: Aegis validation — skip for distill-only
  ├─ 4.3: Cross-platform — skip unless scope is both
  └─ 4.4: validate_setup relationship — always
```

**Key agent behaviors at each step:**

| Before doing this... | Agent should first check... | Scope |
|---|---|---|
| Installing Homebrew | `command -v brew` — skip if present | All |
| Installing pyenv | `command -v pyenv` — skip if present | All |
| Installing Python 3.12 via pyenv | `pyenv versions \| grep 3.12` — skip if present | All |
| Installing nvm | `type nvm` or check `$NVM_DIR/nvm.sh` — skip if present | All |
| Installing Node.js LTS | `node --version` — skip if 18+ | All |
| Creating GCP project on Embark | Ask user — cannot be checked programmatically | Distill |
| Installing/updating gcloud | `command -v gcloud` — if present, run `gcloud components update`; if missing, install | Distill |
| Authenticating gcloud | `gcloud auth list` for active `@salesforce.com` account AND `gcloud config get-value project` for set project — skip auth if both present | Distill |
| Installing cmake | `command -v cmake` — skip if present | Distill |
| Creating Gemini API key | Try `gcloud services api-keys list` to retrieve automatically; fall back to prompting user if gcloud unavailable or no keys exist | Distill |
| Cleaning up Claude Code config | `grep -l "BEDROCK\|AWS" <files>` — skip if no matches | Distill |
| Cloning distill repo | Check if `$RC_WORKSPACE/distill/.git` exists — skip if present | Distill |
| Cloning aegis repo | Check if `$RC_WORKSPACE/aegis/.git` exists — skip if present | Aegis |
| Creating Distill venv | Check if `distill/.venv/bin/python3` exists and correct version | Distill |
| Creating Aegis venv | Check if `aegis/venv/bin/python3` exists and correct version | Aegis |
| Setting `pyenv local` | Check if `.python-version` already has correct value | Per repo |
| Writing `.env.local` | Check if file exists — ask before overwriting | Distill |
| Configuring SF credentials | Check `$SF_URL`; if empty, auto-detect from `cci org default` or `sf config get target-org` — confirm with user before using | Aegis |
| Modifying shell profile | Show exact lines to add — **always ask first** | All |
| Installing Playwright browsers | `playwright install --dry-run` — skip if up to date | Aegis |

> **The validation script (`./scripts/validate_integration_prereqs.sh --scan`) performs most of these checks automatically.** An agent should run it first and use its output to determine which steps to skip.

---

## 0. Prerequisites

This section ensures your workstation has the complete toolchain to run all three projects side by side. The three repos have **conflicting Python requirements** — Distill requires 3.10--3.12 while Foundations and the system may already be on 3.13+. The approach below uses **pyenv** and **nvm** to manage multiple runtimes cleanly.

### 0.1 Version Compatibility Matrix

| Tool | Foundations | Distill | Aegis | Notes |
|---|---|---|---|---|
| **Python** | 3.8+ (via CCI/pipx) | **3.10 -- 3.12 only** | 3.8+ | Distill fails on 3.13+ (`torch`, `sentence-transformers`) |
| **Node.js** | LTS 18+ (for `sf` CLI + SFDMU) | Not required | Not required | Only Foundations needs Node.js |
| **cmake** | Not required | **Required** | Not required | Needed to build `sentence-transformers` |
| **gcloud** | Not required | **Required** | Not required | Vertex AI fallback for local LLM |
| **Chrome** | Required (Robot Framework) | Not required | Required (Playwright) | Playwright can also download its own Chromium |
| **CCI** | 4.0.0+ (via pipx) | Not required | Not required | Foundations-only |
| **SF CLI** | 2.x+ | Not required | Not required | Foundations-only |
| **SFDMU** | 5.0.0+ (sf plugin) | Not required | Not required | Foundations-only |
| **VPN** | Not required | Not required | **Required for clone** | Aegis is on `git.soma.salesforce.com` |

### 0.2 System-Level Tools

**macOS (Homebrew):**

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Verify
brew --version
git --version
```

**Linux (apt):**

```bash
sudo apt update && sudo apt install -y build-essential git curl
```

### 0.3 Python Version Management with pyenv

If you have already completed the Foundations setup, your system likely has Python 3.13+ as the default. Distill **will not work** with 3.13+ — `torch` and `sentence-transformers` fail to build. Use pyenv to maintain both versions side by side.

**Install pyenv:**

```bash
# macOS
brew install pyenv

# Linux
curl https://pyenv.run | bash
```

**Add to your shell profile** (`~/.zshrc` for macOS, `~/.bashrc` for Linux):

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Restart your shell (or `exec "$SHELL"`), then verify:

```bash
pyenv --version
```

**Install the required Python versions:**

```bash
# Python 3.12 — required by Distill, compatible with Aegis
pyenv install 3.12

# Verify both are available
pyenv versions
```

> **If you already have 3.13+ installed** (either as system Python or via pyenv), it will remain available. pyenv lets each directory use a different version without affecting the others.

**Pin Python versions per repo** (done later during workspace setup):

```bash
# Distill — must be 3.12
cd "$RC_WORKSPACE/distill"
pyenv local 3.12
python3 --version   # Should show 3.12.x

# Aegis — use 3.12 for compatibility
cd "$RC_WORKSPACE/aegis"
pyenv local 3.12
python3 --version   # Should show 3.12.x

# Foundations — do NOT set pyenv local
# CCI manages its own Python via pipx and uses whatever the system provides.
# Setting pyenv local here could interfere with pipx.
```

The `pyenv local` command writes a `.python-version` file in the repo directory. These files are already in each project's `.gitignore` so they won't be committed.

### 0.4 Node.js Version Management with nvm

Only Foundations needs Node.js (for the `sf` CLI and its SFDMU plugin). Distill and Aegis do not require it. If you already have Node.js installed from the Foundations setup, this section is informational.

**Install nvm (if not already present):**

```bash
# macOS
brew install nvm

# Linux / macOS (alternative)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```

**Add to your shell profile** (nvm's installer usually does this automatically):

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

Restart your shell, then:

```bash
# Install Node.js LTS
nvm install --lts
nvm use --lts

# Verify
node --version    # Should be v18+ or v20+
npm --version
```

### 0.5 Distill-Specific Tools `[distill-only | both]`

> **Scope:** Skip this entire subsection if scope is **aegis-only**.

These are only needed if you are setting up Distill. The steps must be followed in order — Embark provisions the GCP project that gcloud authenticates against, which is where the Gemini API key is created.

#### Step 1: Create a GCP Project on Embark

Embark is Salesforce's internal tool for provisioning Google Cloud Platform projects. You need a GCP project before you can authenticate gcloud or create API keys.

1. Navigate to [Embark](https://embark.sfdcbt.net/)
2. Sign in with your Salesforce SSO credentials
3. Create a new GCP project (or use an existing one)
4. Note the **Project ID** — you'll need it for gcloud configuration

> **Agent note:** This step requires manual browser interaction. Prompt the user to complete it and provide the GCP Project ID before continuing.

#### Step 2: Install or Update Google Cloud CLI (gcloud)

**New install:**

```bash
# macOS
brew install google-cloud-sdk

# Linux — see: https://cloud.google.com/sdk/docs/install
```

**Already installed — check for updates:**

```bash
gcloud --version
gcloud components update    # interactive — shows changes and prompts Y/n
```

> **Agent note:** Run `command -v gcloud` first. If present, skip the install and run `gcloud components update` instead. Outdated SDK versions can cause compatibility issues with Gemini API client libraries.

#### Step 3: Authenticate and Configure gcloud

**Check existing authentication first:**

```bash
# Check if already authenticated
GCLOUD_ACCOUNT=$(gcloud config get-value account 2>/dev/null)
GCLOUD_PROJECT=$(gcloud config get-value project 2>/dev/null)

echo "Account: ${GCLOUD_ACCOUNT:-NOT SET}"
echo "Project: ${GCLOUD_PROJECT:-NOT SET}"
```

If both show valid values (a `@salesforce.com` account and an Embark project ID), skip to the verification step below. Otherwise, run the relevant commands:

```bash
# Only if not authenticated:
gcloud auth login

# Only if no project is set:
gcloud config set project <your-project-id>
```

**Verify:**

```bash
gcloud config get-value account    # Should show your @salesforce.com email
gcloud config get-value project    # Should show your project ID
```

> **Agent note:** Check `gcloud auth list` for an active `@salesforce.com` account AND `gcloud config get-value project` for a set project. Skip authentication entirely if both are already configured. Only prompt the user for `gcloud auth login` if no account is found, and only ask for a project ID if none is set.

> **If you get authentication errors later** (e.g., when Distill tries to access Vertex AI), re-run `gcloud auth login` and also run `gcloud auth application-default login` for Application Default Credentials (ADC).

#### Step 4: Install cmake

```bash
# macOS
brew install cmake

# Linux
sudo apt install -y cmake

# Verify
cmake --version
```

#### Step 5: Create and Export Gemini API Key

The Gemini API key is created within your Embark-provisioned GCP project. Distill's DataMapper uses it for schema mapping via the Gemini API.

**Automated retrieval (preferred — if gcloud is authenticated):**

```bash
# List existing API keys in the project
GCP_PROJECT=$(gcloud config get-value project 2>/dev/null)
KEY_ID=$(gcloud services api-keys list --project="$GCP_PROJECT" \
  --format='value(uid)' --limit=1 2>/dev/null)

if [[ -n "$KEY_ID" ]]; then
  # Retrieve the key string
  GEMINI_API_KEY=$(gcloud services api-keys get-key-string "$KEY_ID" \
    --project="$GCP_PROJECT" --format='value(keyString)' 2>/dev/null)
  export GEMINI_API_KEY
  echo "Retrieved API key from project $GCP_PROJECT"
else
  echo "No API keys found — create one manually (see below)"
fi
```

> **Agent note:** Always attempt the automated retrieval first. If `gcloud services api-keys list` returns a key, use `get-key-string` to retrieve it and stamp it into `.env.local` and the current shell. Only fall back to the manual flow below if gcloud is not authenticated, no project is set, or no keys exist in the project.

**Manual creation (fallback):**

1. Open [GCP Console > APIs & Credentials](https://console.cloud.google.com/apis/credentials)
2. Ensure you are in the correct project (the one created on Embark in Step 1)
3. Click **Create Credentials** → **API Key**
4. (Recommended) Restrict the key to the **Generative Language API** only
5. Copy the key and export it:

```bash
export GEMINI_API_KEY="your-key-here"
```

**Persisting the key** across shell sessions:

```bash
# Option A: Shell profile (available everywhere)
echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.zshrc

# Option B: Distill .env.local (project-specific, not committed)
# Add to $RC_WORKSPACE/distill/.env.local:
#   GEMINI_API_KEY=your-key-here
```

#### Step 6: Claude Code Cleanup (conditional)

Only needed if you previously configured Claude Code to use AWS Bedrock. Distill uses Vertex AI (via GCP), and leftover Bedrock configuration causes conflicts.

**Check if cleanup is needed:**

```bash
# macOS — check for Bedrock config
grep -l "BEDROCK\|AWS" "/Library/Application Support/ClaudeCode/managed-settings.json" ~/.claude/settings.json 2>/dev/null
```

If either file contains BEDROCK or AWS properties:

1. **Back up** the existing files first
2. Remove BEDROCK/AWS-related properties from `/Library/Application Support/ClaudeCode/managed-settings.json`
3. Remove BEDROCK/AWS-related properties from `~/.claude/settings.json`

> **Agent note:** Show the user the exact properties to remove and get approval before modifying these files.

### 0.6 Prerequisites Validation Script

A standalone bash script validates all integration prerequisites in one pass. It does **not** check CCI, SF CLI, SFDMU, or Robot Framework — those are validated by `cci task run validate_setup` inside Foundations.

The script operates in three modes:

| Mode | Command | What it does |
|---|---|---|
| **Scan** | `./scripts/validate_integration_prereqs.sh --scan` | Inventory-only — lists everything installed, detects conflicts, no pass/fail |
| **Validate** | `./scripts/validate_integration_prereqs.sh` | Full check — PASS/WARN/FAIL for each prerequisite + conflict detection |
| **Fix** | `./scripts/validate_integration_prereqs.sh --fix` | Same as validate, but attempts auto-install of missing tools via Homebrew |

**Recommended workflow — scan first, then validate:**

```bash
# Step 1: See what's already installed and if there are conflicts
./scripts/validate_integration_prereqs.sh --scan

# Step 2: Resolve any conflicts reported (see 0.7 below)

# Step 3: Validate all prerequisites
./scripts/validate_integration_prereqs.sh

# Step 4 (optional): Auto-install missing tools
./scripts/validate_integration_prereqs.sh --fix
```

**Workspace-aware scanning:** If `RC_WORKSPACE` is set, the script also checks for existing clones, virtual environments, `.python-version` files, and venvs built with the wrong Python version:

```bash
export RC_WORKSPACE=~/workspace/revenue-cloud
./scripts/validate_integration_prereqs.sh --scan
```

**What the script checks (10 sections):**

1. **Existing Installation Scan** — inventories all Python installs (system, Homebrew, pyenv), Node.js versions (system, nvm), existing repo clones, venvs, and `.python-version` files
2. **Conflict Detection** — identifies version mismatches, PATH shadowing, stale venvs, and configuration issues (see 0.7)
3. **System-Level Tools** — git, Homebrew
4. **Python / pyenv** — pyenv installed, Python 3.12 available, 3.13+ for Foundations
5. **Node.js / nvm** — nvm installed, Node LTS available
6. **Distill-Specific** — gcloud (+ auth check), cmake
7. **Aegis-Specific** — Chrome/Chromium, Playwright browsers
8. **Network Access** — github.com, git.soma.salesforce.com (VPN)
9. **Environment Variables** — GEMINI_API_KEY, SF_URL
10. **Optimization Suggestions** — cleanup recommendations for multi-version environments

Tools that are already installed show as `[SKIP]` instead of `[PASS]`, making it easy to see what's new vs. pre-existing.

**Expected output when everything is ready:**

```
── 1. Existing Installation Scan ──
  [INFO]  System python3: 3.13.x
  [INFO]  pyenv versions: 3.12.x 3.13.x
  [INFO]  nvm: 0.40.x
  [INFO]  Active Node.js: v24.x

── 2. Conflict Detection ──
  [PASS]  System Python 3.13.x — pyenv 3.12 available for Distill
  [PASS]  No conflicts detected

── 3. System-Level Tools ──
  [PASS]  git 2.x
  [PASS]  Homebrew x.x

── 4-10. ...
  [SKIP]  pyenv x.x — already installed
  [SKIP]  Python 3.12.x — already available via pyenv
  [SKIP]  cmake x.x — already installed
  ...

── Summary ──
  Installs: N Python, Node vXX.x
  N tool(s) already installed — skipped.
  All required checks passed.
```

Once all FAIL items are resolved and no CONFLICT items remain, proceed to Section 1.

### 0.7 Common Conflicts and Resolution

The validation script detects these conflicts automatically. If any appear, resolve them before proceeding.

**System Python 3.13+ without pyenv 3.12:**

```
[CONFLICT]  System Python is 3.13.x (3.13+) — incompatible with Distill
```

Distill requires 3.10-3.12. Install pyenv and add Python 3.12:

```bash
brew install pyenv          # or: curl https://pyenv.run | bash
pyenv install 3.12
```

**Homebrew Python shadows pyenv:**

```
[WARN]  Homebrew Python may shadow pyenv in PATH
```

Ensure pyenv shims are first in PATH. Verify with `which python3` — it should show `~/.pyenv/shims/python3`, not a Homebrew path. If Homebrew wins:

```bash
# Option A: Unlink Homebrew Python
brew unlink python@3

# Option B: Ensure pyenv init is last in shell profile
# (pyenv shims must come before /opt/homebrew/bin in PATH)
```

**Existing venv built with wrong Python:**

```
[CONFLICT]  distill/.venv/ was created with Python 3.13.x (expected 3.12.x)
```

Delete and recreate the venv with the correct Python:

```bash
cd "$RC_WORKSPACE/distill"
rm -rf .venv
python3 -m venv .venv        # pyenv local ensures this uses 3.12
source .venv/bin/activate
pip install -e ".[dev]"
```

**.python-version points to missing pyenv version:**

```
[CONFLICT]  distill/.python-version requests 3.12 but it's not installed in pyenv
```

Install the requested version:

```bash
pyenv install 3.12
```

**Foundations has a .python-version file:**

```
[CONFLICT]  foundations/.python-version exists — may interfere with CCI/pipx
```

CCI runs via pipx with its own Python. A `.python-version` in the Foundations directory can confuse pyenv:

```bash
rm "$RC_WORKSPACE/foundations/.python-version"
```

**pipx uses pyenv-managed Python:**

```
[INFO]  pipx is using pyenv Python 3.13.x — keep this version installed
```

This is normal and expected when using pyenv. The only risk is if you run `pyenv uninstall` on the specific version pipx is linked to. As long as that version stays installed, CCI and other pipx tools will keep working — changing `pyenv global` does **not** break them.

```bash
# To check which Python pipx is using:
pipx environment | grep PYTHON

# DON'T uninstall this version:
pyenv versions   # note which one pipx references
```

**nvm Node.js shadowed by Homebrew Node:**

```
[WARN]  Homebrew Node.js vXX may shadow nvm in PATH
```

Either unlink Homebrew's Node or ensure nvm sourcing comes after Homebrew in your shell profile:

```bash
brew unlink node
```

---

## 1. Workspace Setup

Choose a workspace root directory. All three repositories will be cloned as siblings under this root.

```bash
export RC_WORKSPACE=~/workspace/revenue-cloud
mkdir -p "$RC_WORKSPACE"
cd "$RC_WORKSPACE"
```

### Clone Repositories

Clone Foundations plus the repos for your chosen scope. Skip repos you don't need.

```bash
# Revenue Cloud Foundations (always — this repo)
git clone https://github.com/salesforce-internal/revenue-cloud-foundations.git foundations
cd foundations && git checkout feat/distill-aegis-integration && cd ..

# Distill (AI-powered customization migration) — skip for aegis-only
git clone https://github.com/sf-industries/distill.git distill

# Aegis (BDD test automation — requires VPN) — skip for distill-only
git clone https://git.soma.salesforce.com/industries/Automated-Remote-Org-Test.git aegis
```

> **Agent note:** Only clone repos that match the chosen scope. Check if each repo already exists (`[ -d "$RC_WORKSPACE/<repo>/.git" ]`) before cloning.

### Pin Python Versions

Set `pyenv local` only for repos that were cloned:

```bash
# Distill — must be 3.10-3.12 (skip for aegis-only)
cd "$RC_WORKSPACE/distill"
pyenv local 3.12
python3 --version   # Verify: 3.12.x

# Aegis — use 3.12 for compatibility (skip for distill-only)
cd "$RC_WORKSPACE/aegis"
pyenv local 3.12
python3 --version   # Verify: 3.12.x

# Foundations — no pyenv local (CCI manages its own Python)
cd "$RC_WORKSPACE"
```

After setup, your workspace looks like:

```
$RC_WORKSPACE/
├── foundations/          # Revenue Cloud Foundations (rlm-base-dev)
│   └── (no .python-version — CCI/pipx manages Python)
├── distill/             # Distill
│   └── .python-version  # → 3.12 (created by pyenv local)
└── aegis/               # Aegis (Automated-Remote-Org-Test)
    └── .python-version  # → 3.12 (created by pyenv local)
```

---

## 2. Distill — Local Setup `[distill-only | both]`

> **Scope:** Skip this entire section if scope is **aegis-only**.

**Repository:** `sf-industries/distill`
**What it does:** AI-powered Salesforce customization migration using Claude Agent SDK.
**Why test it:** Validate that the Insights pipeline, DataMapper, and API server work before wiring them into CCI tasks.

### 2.1 Installation

```bash
cd "$RC_WORKSPACE/distill"

# Verify Python version is 3.12.x (set by pyenv local in Section 1)
python3 --version

# Option A: Automatic (recommended) — handles venv, deps, and startup
cp .env.example .env.local
./distill start

# Option B: Manual
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

The `./distill` launcher auto-creates `.venv` using the pyenv-selected Python, installs all dependencies, and runs the requested command.

### 2.2 Configuration

Create `.env.local` from the example template (if not done in 2.1):

```bash
cp .env.example .env.local
```

**Minimum viable `.env.local` for local testing:**

```bash
# Core
DISTILL_ENV=dev
DISTILL_DEV_MODE=true

# LLM
DISTILL_LLM__PROVIDER=anthropic
DISTILL_LLM__MODEL=claude-sonnet-4-5@20250929

# Storage
DISTILL_STORAGE__BACKEND=hybrid
DISTILL_STORAGE__DATA_DIR=./output
DISTILL_STORAGE__DATABASE__URL=sqlite:///./output/distill.db

# Database — users via deployed API, kits/projects local SQLite
DISTILL_CENTRAL_DB_BACKEND=postgresql
DISTILL_API_URL=https://distill-cli.sfproxy.scratchpad14.aws-dev4-uswest2.aws.sfdc.cl

# SSL (required for local dev — internal Salesforce CAs)
API_DISABLE_SSL_VERIFY=true
OIDC_DISABLE_SSL_VERIFY=true

# DataMapper LLM (Gemini for schema mapping)
PROVIDER=gemini
GEMINI_API_KEY=<your-gemini-api-key>
MODEL_NAME=gemini-2.5-pro

# Logging
DISTILL_LOGGING__LEVEL=INFO
```

#### Credential Verification Checkpoint

Before continuing, the agent **must** verify that `.env.local` contains a real Gemini API key — not a placeholder.

```bash
# Check if GEMINI_API_KEY is still a placeholder
grep -q '<your-gemini-api-key>\|your.key.here\|your_gemini_api_key_here' "$RC_WORKSPACE/distill/.env.local" && echo "PLACEHOLDER DETECTED" || echo "OK"
```

> **Agent note:** If the check prints `PLACEHOLDER DETECTED`, attempt automated retrieval first:
>
> ```bash
> # Try to retrieve from gcloud (if authenticated with a project set)
> GCP_PROJECT=$(gcloud config get-value project 2>/dev/null)
> KEY_ID=$(gcloud services api-keys list --project="$GCP_PROJECT" \
>   --format='value(uid)' --limit=1 2>/dev/null)
> if [[ -n "$KEY_ID" ]]; then
>   GEMINI_KEY=$(gcloud services api-keys get-key-string "$KEY_ID" \
>     --project="$GCP_PROJECT" --format='value(keyString)' 2>/dev/null)
>   sed -i '' "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=${GEMINI_KEY}|" "$RC_WORKSPACE/distill/.env.local"
>   export GEMINI_API_KEY="$GEMINI_KEY"
>   echo "Stamped API key from project $GCP_PROJECT"
> fi
> ```
>
> If automated retrieval fails (gcloud not authenticated, no project, or no keys), fall back to prompting the user:
>
> *"Your `.env.local` still has a placeholder for GEMINI_API_KEY and I couldn't retrieve it automatically from gcloud. Please provide your Gemini API key (created in Section 0.5, Step 5 from your Embark GCP project) and I'll update the file."*
>
> Once the user provides the key, replace the placeholder line in `.env.local`:
> ```bash
> sed -i '' "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=${USER_PROVIDED_KEY}|" "$RC_WORKSPACE/distill/.env.local"
> ```
>
> Also check if `GEMINI_API_KEY` is exported in the current shell (needed for some Distill operations that read from environment rather than `.env.local`):
> ```bash
> echo "${GEMINI_API_KEY:-NOT SET}"
> ```
> If not set, export it: `export GEMINI_API_KEY="<key>"`

### 2.3 Database Initialization

**User account requirement:** You must have an entry in the production PostgreSQL users table before running locally.

**Option A — Login via QuantumK once (recommended):**
1. Navigate to `https://distill-cli-crossfd.sfproxy.scratchpad14.aws-dev4-uswest2.aws.sfdc.cl:7443/`
2. Login with Salesforce SSO (QuantumK OIDC)
3. Your user is auto-created with roles from QuantumK

**Option B — Auto-insert test user:**
```bash
./insert-test-user.sh
```
Creates `test-viewer-001` with viewer role. This is also run automatically by `start-services-local.sh` when `DISTILL_DEV_MODE=true`.

**Local SQLite databases** (`output/distill.db`, `output/central.db`) are created automatically on first run.

### 2.4 Running Distill

**All-in-one startup (recommended):**

```bash
cd "$RC_WORKSPACE/distill"
./start-services-local.sh
```

This starts both the API server (port 8000) and dashboard (port 5000), creates `.env.local` if missing, inserts test user in dev mode, and opens the browser.

| Access Point | URL |
|---|---|
| Dashboard | http://localhost:5000 |
| API Server | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

**Individual components:**

```bash
# Dashboard only
./distill start

# API server only
python serve_api.py

# CLI (interactive chat)
./distill chat

# Both (same as start-services-local.sh)
./distill start-all
```

### 2.5 Running Tests

```bash
cd "$RC_WORKSPACE/distill"
source .venv/bin/activate

# All tests
pytest

# Unit tests only
pytest -m unit

# Integration tests (may need external services)
pytest -m integration

# Specific test file
pytest tests/test_api_endpoints.py

# With verbose output
pytest -v --no-header
```

### 2.6 Known Issues

- **Python 3.13+** is not supported — `torch` and `sentence-transformers` fail to build. Use pyenv to pin 3.12.
- **VPC restrictions** prevent direct PostgreSQL access from local machines — the `APIAdapter` routes through the deployed API endpoint.
- **`run_file_migration` is hardcoded to Gemini** — `GEMINI_API_KEY` is required even if using Einstein LLM for other operations.
- **Einstein LLM Gateway** requires OAuth credentials from Falcon Vault — not available locally without `LLM_GATEWAY_MODE=prod` and vault-mounted secrets. Set `LLM_GATEWAY_MODE=test` for local development.

---

## 3. Aegis — Local Setup `[aegis-only | both]`

> **Scope:** Skip this entire section if scope is **distill-only**.

**Repository:** `industries/Automated-Remote-Org-Test`
**What it does:** BDD test automation for Revenue Cloud using Behave + Playwright/Selenium.
**Why test it:** Validate that `RevenueGoFoundation` scenarios pass against a Foundations-provisioned org before wiring Aegis into CCI flows.

### 3.1 Installation

```bash
cd "$RC_WORKSPACE/aegis"

# Verify Python version is 3.12.x (set by pyenv local in Section 1)
python3 --version

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (all RevenueGoFoundation tests use @playwright)
playwright install chromium

# Configure git hooks
git config core.hooksPath .githooks
```

### 3.2 Configuration

**Environment variables — set before running tests:**

```bash
# Required — Salesforce org credentials
export SF_URL="https://your-org.my.salesforce.com/"
export SF_USERNAME="admin@your-org.com"
export SF_PASSWORD="your-password"
export SF_TOKEN=""  # Leave empty if IP-restricted or using session injection
```

#### Credential Verification Checkpoint

Before continuing to test execution, the agent **must** verify that Salesforce credentials are set to real values — not placeholders.

```bash
# Check if SF_URL is set and not a placeholder
if [[ -z "${SF_URL:-}" || "$SF_URL" == *"your-org"* ]]; then
  echo "SF_URL NOT SET or placeholder"
else
  echo "SF_URL OK: $SF_URL"
fi
```

> **Agent note:** If `SF_URL` is unset or contains `your-org`, attempt auto-detection first:
>
> ```bash
> # 1. Check CCI default org
> cd "$RC_WORKSPACE/foundations"
> CCI_DEFAULT=$(cci org default 2>/dev/null)
>
> # 2. Check SF CLI default target-org
> SF_TARGET=$(sf config get target-org --json 2>/dev/null \
>   | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('value',''))" 2>/dev/null)
> ```
>
> If either is found, retrieve org details and **prompt the user to confirm**:
>
> *"Found default org: `<username>` at `<instance_url>`. Use this for Aegis testing? (Y/n)"*
>
> If confirmed, export the values. If neither default is set or the user declines, fall back to one of:
>
> **Option A — User specifies a CCI org alias:**
> *"Which CCI org alias should I use? (e.g., `dev`, `beta`)"*
> If provided, run the CCI export command below to set credentials automatically.
>
> **Option B — User has manual credentials:**
> *"Please provide your Salesforce org URL, username, and password (or session ID) for Aegis testing."*
>
> **Option C — User wants to skip Aegis live testing:**
> *"We can skip live testing for now and just do the dry-run validation (Section 4.2, Step 1) which doesn't need credentials."*
>
> Never proceed to `behave features/RevenueGoFoundation/` with placeholder credentials — it will fail immediately.

**Getting credentials from a CCI-managed org (recommended):**

```bash
# From the Foundations directory:
cd "$RC_WORKSPACE/foundations"
cci org info <alias> --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'export SF_URL=\"{d[\"instance_url\"]}/\"')
print(f'export SF_USERNAME=\"{d[\"username\"]}\"')
# For session-based auth:
print(f'export SF_SESSION_ID=\"{d[\"access_token\"]}\"')
"
```

**Team credentials file (optional):**

The `features/RevenueGoFoundation/RevenueGoFoundationCreds.json` contains org connection details. You can add your own org key:

```json
{
  "MY_CCI_ORG": {
    "SF_URL": "https://your-org.my.salesforce.com/",
    "SF_USERNAME": "admin@your-org.com",
    "SF_PASSWORD": "your-password",
    "SF_TOKEN": ""
  }
}
```

### 3.3 Running Tests

All commands assume you are in the Aegis directory with the venv active:

```bash
cd "$RC_WORKSPACE/aegis"
source venv/bin/activate
```

**Run all RevenueGoFoundation tests:**

```bash
behave features/RevenueGoFoundation/
```

**Run a single feature file:**

```bash
# Initial Setup validation
behave features/RevenueGoFoundation/RevenueCloudInitialSetup.feature

# DRO scenarios
behave features/RevenueGoFoundation/DynamicRevenueOrchestrator.feature

# Quote scenarios
behave features/RevenueGoFoundation/Quotes.feature

# Order scenarios
behave features/RevenueGoFoundation/Orders.feature

# Pricing
behave features/RevenueGoFoundation/PriceManagement.feature

# Product Configurator
behave features/RevenueGoFoundation/ProductConfigurator.feature

# Asset Lifecycle Management
behave features/RevenueGoFoundation/AssetLifecycleManagement.feature
```

**Run a specific scenario by name:**

```bash
behave features/RevenueGoFoundation/RevenueCloudInitialSetup.feature \
  --name "Verify Revenue Cloud Initial Setup"
```

**Run with verbose output:**

```bash
behave features/RevenueGoFoundation/ --no-capture -v
```

**Run headless (CI-style):**

All `RevenueGoFoundation` feature files use the `@playwright` tag. Playwright runs headless by default. To see the browser during debugging:

```bash
export HEADLESS=false
behave features/RevenueGoFoundation/RevenueCloudInitialSetup.feature
```

### 3.4 RevenueGoFoundation Feature Files

All 7 files use `@playwright` and the session injection pattern (`Given login to Salesforce with sessionId`):

| Feature File | Scenarios | Tests |
|---|---|---|
| `RevenueCloudInitialSetup.feature` | Revenue Cloud Initial Setup validation | Guided setup, feature enablement |
| `DynamicRevenueOrchestrator.feature` | DRO setup and feature toggles | Redirections, setup page validation |
| `AssetLifecycleManagement.feature` | Asset Lifecycle Management | Setup, redirections, help links |
| `Quotes.feature` | Quote creation and management | Quote CRUD, line items |
| `Orders.feature` | Order placement | Order creation from quotes |
| `PriceManagement.feature` | Pricing configuration | Pricing setup, management |
| `ProductConfigurator.feature` | Product configuration | Bundle configuration, product setup |

### 3.5 Known Issues

- **Playwright `@playwright` tag is required** — all `RevenueGoFoundation` files use it. Removing the tag falls back to Selenium, which requires `chromedriver` via `webdriver-manager`.
- **Session injection vs. password auth:** The `Given login to Salesforce with sessionId` step uses `frontdoor.jsp` with an OAuth access token. The `Given Login to Salesforce` step uses username/password. Both work; session injection is preferred for CCI integration.
- **Session reuse per feature:** `ENABLE_SESSION_REUSE_PER_FEATURE = True` in `environment.py` means the browser session is shared across scenarios within a feature file. If one scenario corrupts state, subsequent scenarios in the same file may fail.
- **Org must be pre-provisioned:** Aegis cannot create orgs. Run `cci flow run prepare_rlm_org --org <alias>` first with the appropriate data shape and feature flags. For full RevenueGoFoundation coverage, the org needs: QB data (`qb: true`), DRO (`dro: true`), billing (`billing: true`), and pricing data.
- **`nest_asyncio` import:** The `environment.py` applies `nest_asyncio` at import time to handle Playwright/gRPC event loop conflicts. This is handled automatically.
- **git.soma.salesforce.com access:** The Aegis repo is on internal GHE. You must be on VPN or have SSH keys configured for `git.soma.salesforce.com`.

---

## 4. Post-Setup Validation

This section validates that each platform is operational **after** completing installation. Each subsection is independent — you can validate Distill without having an org for Aegis, and vice versa.

### 4.1 Distill Validation `[distill-only | both]`

Run these checks from the Distill directory:

```bash
cd "$RC_WORKSPACE/distill"
source .venv/bin/activate
```

| # | Check | Command | Expected |
|---|---|---|---|
| D1 | Python version correct | `python3 --version` | 3.12.x |
| D2 | Package installed | `python3 -c "import distill; print('OK')"` | `OK` |
| D3 | API server starts | `python serve_api.py &` then `curl -s http://localhost:8000/health` | 200 response |
| D4 | Swagger docs load | Open http://localhost:8000/docs | Renders UI |
| D5 | SQLite DB created | `ls -la output/distill.db output/central.db` | Both files exist |
| D6 | Dashboard loads | `./start-services-local.sh` | Browser opens, dashboard renders |
| D7 | Test user accessible | Dashboard shows logged-in user | User info visible |
| D8 | Unit tests pass | `pytest -m unit` | Exit code 0 |

### 4.2 Aegis Validation `[aegis-only | both]`

**Step 1 — Dry-run validation (no Salesforce org needed):**

This verifies that all step definitions are importable and Gherkin syntax is correct without connecting to any org:

```bash
cd "$RC_WORKSPACE/aegis"
source venv/bin/activate

# Dry-run parses features and validates step bindings
behave --dry-run features/RevenueGoFoundation/
```

Expected: All 7 feature files parsed, 0 undefined steps.

**Step 2 — Live validation (requires a provisioned Salesforce org):**

```bash
# Set org credentials (see Section 3.2 for CCI export method)
export SF_URL="https://your-org.my.salesforce.com/"
export SF_USERNAME="admin@your-org.com"
export SF_PASSWORD="your-password"
export SF_TOKEN=""

# Run the most basic scenario first
behave features/RevenueGoFoundation/RevenueCloudInitialSetup.feature

# If that passes, run the full suite
behave features/RevenueGoFoundation/
```

| # | Check | Command | Expected |
|---|---|---|---|
| A1 | Python version correct | `python3 --version` | 3.12.x |
| A2 | Behave installed | `behave --version` | `behave 1.2.6` |
| A3 | Playwright ready | `playwright install chromium` | Already installed |
| A4 | Step defs valid (dry-run) | `behave --dry-run features/RevenueGoFoundation/` | 0 undefined steps |
| A5 | Initial Setup passes | `behave features/RevenueGoFoundation/RevenueCloudInitialSetup.feature` | All scenarios pass |
| A6 | Full RGF suite passes | `behave features/RevenueGoFoundation/` | All 7 feature files pass |

### 4.3 Cross-Platform Validation `[both only]`

This end-to-end check validates that Aegis can run against a Foundations-provisioned org:

```bash
# 1. Provision an org via Foundations
cd "$RC_WORKSPACE/foundations"
cci flow run prepare_rlm_org --org dev

# 2. Export credentials
eval $(cci org info dev --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'export SF_URL=\"{d[\"instance_url\"]}/\"')
print(f'export SF_USERNAME=\"{d[\"username\"]}\"')
print(f'export SF_SESSION_ID=\"{d[\"access_token\"]}\"')
")

# 3. Run Aegis against the CCI-provisioned org
cd "$RC_WORKSPACE/aegis"
source venv/bin/activate
behave features/RevenueGoFoundation/RevenueCloudInitialSetup.feature
```

### 4.4 Relationship to Foundations `validate_setup`

Foundations has its own setup validation task:

```bash
cd "$RC_WORKSPACE/foundations"
cci task run validate_setup
```

This checks: Python, CumulusCI (4.0.0+), Node.js, Salesforce CLI (sf 2.x+), SFDMU (5.0.0+), Robot Framework, SeleniumLibrary, webdriver-manager, Chrome/ChromeDriver, and urllib3. It can auto-fix SFDMU, Robot deps, and urllib3.

**These two validations are complementary and do not overlap:**

| What | `validate_integration_prereqs.sh` | `cci task run validate_setup` |
|---|---|---|
| **Scope** | Distill + Aegis toolchain | Foundations toolchain |
| **Checks** | pyenv, Python 3.12, nvm, gcloud, cmake, Chrome, VPN, env vars | CCI, SF CLI, SFDMU, Robot, Selenium, urllib3 |
| **Requires CCI** | No (standalone bash) | Yes (runs as CCI task) |
| **Auto-fix** | `--fix` flag (Homebrew installs) | `auto_fix` option (SFDMU, Robot, urllib3) |
| **When to run** | Before cloning repos / setting up workspace | After Foundations is cloned and CCI is installed |

**Recommended order:**
1. `./scripts/validate_integration_prereqs.sh` — fix all FAIL items
2. `cci task run validate_setup` — fix any Foundations-specific issues
3. Proceed with Sections 2 and 3 of this guide

---

## 5. Directory Reference

```
$RC_WORKSPACE/
├── foundations/                                # Revenue Cloud Foundations
│   ├── cumulusci.yml                          # 58+ flags, 30+ flows
│   ├── tasks/                                 # 30+ Python task modules
│   ├── scripts/validate_integration_prereqs.sh # Integration prereqs validator
│   └── docs/integration/                      # This guide + integration plans
│
├── distill/                                   # Distill (AI migration)
│   ├── .python-version                        # → 3.12 (pyenv local)
│   ├── .env.example → .env.local              # Configuration template
│   ├── ./distill                              # Launcher script (auto-venv)
│   ├── ./start-services-local.sh              # All-in-one local startup
│   ├── serve_api.py                           # API server
│   ├── src/distill/dashboard/app.py           # Flask dashboard
│   └── tests/                                 # pytest suite
│
└── aegis/                                     # Aegis (Automated-Remote-Org-Test)
    ├── .python-version                        # → 3.12 (pyenv local)
    ├── requirements.txt                       # pip dependencies
    ├── behave.ini                             # Behave configuration
    ├── features/RevenueGoFoundation/          # 7 feature files (all @playwright)
    ├── features/environment.py                # Test lifecycle hooks
    └── shared/                                # Shared steps, utils, data
```

---

## 6. Repository URLs

| Repository | URL | Access |
|---|---|---|
| Revenue Cloud Foundations | `https://github.com/salesforce-internal/revenue-cloud-foundations.git` | GitHub (salesforce-internal) |
| Distill | `https://github.com/sf-industries/distill.git` | GitHub (sf-industries) |
| Aegis | `https://git.soma.salesforce.com/industries/Automated-Remote-Org-Test.git` | GHE (git.soma — requires VPN) |
