# Distill & Aegis: Isolated Testing Setup Guide

> **Purpose:** Stand up Distill and Aegis locally for independent validation before beginning integration work with Revenue Cloud Foundations.
> **Last Updated:** 2026-04-07
> **Part of:** [Revenue Cloud Engineering Platform](revenue-cloud-platform.md)
>
> **Prerequisite:** A Foundations-provisioned Salesforce org (via `cci flow run prepare_rlm_org --org <alias>`) for Aegis testing. Distill can be tested independently.

---

## 0. Workspace Setup

Choose a workspace root directory. All three repositories will be cloned as siblings under this root.

```bash
# Pick any workspace location — examples:
#   ~/workspace/revenue-cloud
#   ~/projects/rlm
#   ~/dev/rc-integration
export RC_WORKSPACE=~/workspace/revenue-cloud
mkdir -p "$RC_WORKSPACE"
cd "$RC_WORKSPACE"
```

### Clone All Three Repositories

```bash
# Revenue Cloud Foundations (primary — this repo)
git clone https://github.com/salesforce-internal/revenue-cloud-foundations.git foundations
cd foundations && git checkout feat/distill-aegis-integration && cd ..

# Distill (AI-powered customization migration)
git clone https://github.com/sf-industries/distill.git distill

# Aegis (BDD test automation)
git clone https://git.soma.salesforce.com/industries/Automated-Remote-Org-Test.git aegis
```

After cloning, your workspace looks like:

```
$RC_WORKSPACE/
├── foundations/     # Revenue Cloud Foundations (rlm-base-dev)
├── distill/         # Distill
└── aegis/           # Aegis (Automated-Remote-Org-Test)
```

> **Note:** If you already have these repos cloned elsewhere, you can symlink them or adjust `RC_WORKSPACE` accordingly. The guide uses `$RC_WORKSPACE/distill` and `$RC_WORKSPACE/aegis` throughout.

---

## 1. Distill — Local Setup

**Repository:** `sf-industries/distill`
**What it does:** AI-powered Salesforce customization migration using Claude Agent SDK.
**Why test it:** Validate that the Insights pipeline, DataMapper, and API server work before wiring them into CCI tasks.

### 1.1 Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10 – 3.12 | **Not** 3.13+ (incompatible with several deps including `torch`) |
| Google Cloud CLI | Latest | macOS: `brew install google-cloud-sdk`; Linux: see [gcloud docs](https://cloud.google.com/sdk/docs/install) |
| cmake | Latest | macOS: `brew install cmake`; Linux: `apt install cmake` — required by `sentence-transformers` build |
| GCP Project | — | Create on [Embark](https://embark.sfdcbt.net/) for Vertex AI access |
| Gemini API Key | — | Create at [GCP Console > APIs & Credentials](https://console.cloud.google.com/apis/credentials) |

**Verify Python version:**

```bash
python3 --version  # Must be 3.10.x, 3.11.x, or 3.12.x
```

If your default `python3` is 3.13+, install a compatible version:

```bash
# macOS
brew install python@3.12

# Or use pyenv
pyenv install 3.12
pyenv local 3.12
```

**Claude Code cleanup (if previously used AWS Bedrock):**
- Remove BEDROCK/AWS properties from `/Library/Application Support/ClaudeCode/managed-settings.json`
- Remove BEDROCK/AWS properties from `~/.claude/settings.json`

### 1.2 Installation

```bash
cd "$RC_WORKSPACE/distill"

# Option A: Automatic (recommended) — handles venv, deps, and startup
cp .env.example .env.local
./distill start

# Option B: Manual
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

The `./distill` launcher auto-creates `.venv`, installs all dependencies, and runs the requested command.

### 1.3 Configuration

Create `.env.local` from the example template:

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

### 1.4 Database Initialization

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

### 1.5 Running Distill

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

### 1.6 Running Tests

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

### 1.7 Smoke Test Checklist

| # | Test | How to Verify |
|---|---|---|
| 1 | Dashboard loads | `./start-services-local.sh` → browser opens → dashboard renders |
| 2 | API server responds | `curl http://localhost:8000/health` returns 200 |
| 3 | Swagger docs load | Navigate to http://localhost:8000/docs |
| 4 | SQLite DB created | `ls -la output/distill.db output/central.db` |
| 5 | Test user accessible | Dashboard shows logged-in user info |
| 6 | Unit tests pass | `pytest -m unit` exits 0 |

### 1.8 Known Issues

- **Python 3.13+** is not supported — `torch` and `sentence-transformers` fail to build.
- **VPC restrictions** prevent direct PostgreSQL access from local machines — the `APIAdapter` routes through the deployed API endpoint.
- **`run_file_migration` is hardcoded to Gemini** — `GEMINI_API_KEY` is required even if using Einstein LLM for other operations.
- **Einstein LLM Gateway** requires OAuth credentials from Falcon Vault — not available locally without `LLM_GATEWAY_MODE=prod` and vault-mounted secrets. Set `LLM_GATEWAY_MODE=test` for local development.

---

## 2. Aegis — Local Setup

**Repository:** `industries/Automated-Remote-Org-Test`
**What it does:** BDD test automation for Revenue Cloud using Behave + Playwright/Selenium.
**Why test it:** Validate that `RevenueGoFoundation` scenarios pass against a Foundations-provisioned org before wiring Aegis into CCI flows.

### 2.1 Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.8+ | Standard Python — no version ceiling issues |
| Chrome | Latest | Playwright manages its own browser binaries |
| A Salesforce org | — | Provisioned via `cci flow run prepare_rlm_org` with QB data loaded |

### 2.2 Installation

```bash
cd "$RC_WORKSPACE/aegis"

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

### 2.3 Configuration

**Environment variables — set before running tests:**

```bash
# Required — Salesforce org credentials
export SF_URL="https://your-org.my.salesforce.com/"
export SF_USERNAME="admin@your-org.com"
export SF_PASSWORD="your-password"
export SF_TOKEN=""  # Leave empty if IP-restricted or using session injection
```

**Getting credentials from a CCI-managed org:**

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

### 2.4 Running Tests

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

### 2.5 RevenueGoFoundation Feature Files

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

### 2.6 Smoke Test Checklist

| # | Test | How to Verify |
|---|---|---|
| 1 | Dependencies installed | `pip list \| grep behave` shows `1.2.6` |
| 2 | Playwright browsers ready | `playwright install chromium` completes successfully |
| 3 | Org connectivity | `python -c "from simple_salesforce import Salesforce; sf = Salesforce(username='$SF_USERNAME', password='$SF_PASSWORD', security_token='$SF_TOKEN', domain='test'); print(sf.describe()['encoding'])"` |
| 4 | Initial Setup test passes | `behave features/RevenueGoFoundation/RevenueCloudInitialSetup.feature` |
| 5 | Full suite passes | `behave features/RevenueGoFoundation/` |

### 2.7 Known Issues

- **Playwright `@playwright` tag is required** — all `RevenueGoFoundation` files use it. Removing the tag falls back to Selenium, which requires `chromedriver` via `webdriver-manager`.
- **Session injection vs. password auth:** The `Given login to Salesforce with sessionId` step uses `frontdoor.jsp` with an OAuth access token. The `Given Login to Salesforce` step uses username/password. Both work; session injection is preferred for CCI integration.
- **Session reuse per feature:** `ENABLE_SESSION_REUSE_PER_FEATURE = True` in `environment.py` means the browser session is shared across scenarios within a feature file. If one scenario corrupts state, subsequent scenarios in the same file may fail.
- **Org must be pre-provisioned:** Aegis cannot create orgs. Run `cci flow run prepare_rlm_org --org <alias>` first with the appropriate data shape and feature flags. For full RevenueGoFoundation coverage, the org needs: QB data (`qb: true`), DRO (`dro: true`), billing (`billing: true`), and pricing data.
- **`nest_asyncio` import:** The `environment.py` applies `nest_asyncio` at import time to handle Playwright/gRPC event loop conflicts. This is handled automatically.
- **git.soma.salesforce.com access:** The Aegis repo is on internal GHE. You must be on VPN or have SSH keys configured for `git.soma.salesforce.com`.

---

## 3. Validation Matrix

Before starting integration work, confirm the following passes on each platform:

| Platform | Validation | Command | Expected |
|---|---|---|---|
| **Foundations** | Org provisions successfully | `cd $RC_WORKSPACE/foundations && cci flow run prepare_rlm_org --org dev` | All 30+ steps pass |
| **Distill** | Dashboard + API start | `cd $RC_WORKSPACE/distill && ./start-services-local.sh` | Ports 5000/8000 respond |
| **Distill** | Unit tests pass | `cd $RC_WORKSPACE/distill && source .venv/bin/activate && pytest -m unit` | Exit code 0 |
| **Aegis** | Initial Setup test | `cd $RC_WORKSPACE/aegis && source venv/bin/activate && behave features/RevenueGoFoundation/RevenueCloudInitialSetup.feature` | All scenarios pass |
| **Aegis** | Full RGF suite | `cd $RC_WORKSPACE/aegis && source venv/bin/activate && behave features/RevenueGoFoundation/` | All 7 feature files pass |
| **Cross-platform** | Aegis against CCI org | Provision with CCI, export creds, run Aegis | Aegis scenarios pass against CCI-provisioned org |

---

## 4. Directory Reference

```
$RC_WORKSPACE/
├── foundations/                                # Revenue Cloud Foundations
│   ├── cumulusci.yml                          # 58+ flags, 30+ flows
│   ├── tasks/                                 # 30+ Python task modules
│   └── docs/integration/                      # This guide + integration plans
│
├── distill/                                   # Distill (AI migration)
│   ├── .env.example → .env.local              # Configuration template
│   ├── ./distill                              # Launcher script (auto-venv)
│   ├── ./start-services-local.sh              # All-in-one local startup
│   ├── serve_api.py                           # API server
│   ├── src/distill/dashboard/app.py           # Flask dashboard
│   └── tests/                                 # pytest suite
│
└── aegis/                                     # Aegis (Automated-Remote-Org-Test)
    ├── requirements.txt                       # pip dependencies
    ├── behave.ini                             # Behave configuration
    ├── features/RevenueGoFoundation/          # 7 feature files (all @playwright)
    ├── features/environment.py                # Test lifecycle hooks
    └── shared/                                # Shared steps, utils, data
```

---

## 5. Repository URLs

| Repository | URL | Access |
|---|---|---|
| Revenue Cloud Foundations | `https://github.com/salesforce-internal/revenue-cloud-foundations.git` | GitHub (salesforce-internal) |
| Distill | `https://github.com/sf-industries/distill.git` | GitHub (sf-industries) |
| Aegis | `https://git.soma.salesforce.com/industries/Automated-Remote-Org-Test.git` | GHE (git.soma — requires VPN) |
