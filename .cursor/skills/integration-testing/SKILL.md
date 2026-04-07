# Integration Testing — Distill & Aegis with Foundations

Use this skill when setting up, configuring, or troubleshooting the
multi-repo integration workspace that runs Distill and Aegis alongside
Revenue Cloud Foundations.

## Quick Rules

1. **Python 3.12** for Distill and Aegis. **Never** use 3.13+ for Distill — `torch`/`sentence-transformers` break.
2. **pyenv local** pins versions per repo. Never set `.python-version` in the Foundations directory — CCI/pipx manage their own Python.
3. **Run `--scan` first** before installing anything: `./scripts/validate_integration_prereqs.sh --scan`
4. **Two separate validators** — `validate_integration_prereqs.sh` for Distill/Aegis toolchain, `cci task run validate_setup` for Foundations. They do not overlap.
5. **Aegis needs VPN** — `git.soma.salesforce.com` is only reachable on the Salesforce VPN.
6. **Aegis cannot create orgs** — always provision via `cci flow run prepare_rlm_org --org <alias>` first, then export credentials to Aegis.
7. **Distill `.env.local`** is never committed. Copy from `.env.example` and customise per environment.
8. **Session injection** (`frontdoor.jsp`) is the preferred auth method for Aegis against CCI-managed orgs — use `SF_SESSION_ID` from `cci org info`.

## DO NOT

- **DO NOT** install Distill dependencies with Python 3.13+ — the build will fail
- **DO NOT** set `pyenv local` in the Foundations directory — this breaks CCI/pipx
- **DO NOT** run `validate_integration_prereqs.sh --fix` before `--scan` — scan first to detect conflicts
- **DO NOT** commit `.python-version` files — they are local-only (gitignored)
- **DO NOT** commit `.env.local` or any file containing credentials/API keys
- **DO NOT** point pipx at a pyenv-managed Python — if pyenv global changes, CCI breaks
- **DO NOT** mix CCI org aliases with SF CLI aliases when exporting credentials for Aegis

---

## Version Compatibility Matrix

| Tool | Foundations | Distill | Aegis |
|------|-----------|---------|-------|
| Python | 3.8+ (via CCI/pipx) | **3.10–3.12 only** | 3.8+ |
| Node.js | LTS 18+ (sf CLI) | Not required | Not required |
| cmake | Not required | **Required** | Not required |
| gcloud | Not required | **Required** | Not required |
| Chrome | Required (Robot) | Not required | Required (Playwright) |
| VPN | Not required | Not required | **Required for clone** |

---

## Workspace Layout

```
$RC_WORKSPACE/
├── foundations/          # Revenue Cloud Foundations (rlm-base-dev)
│   └── (no .python-version)
├── distill/             # Distill (AI migration)
│   └── .python-version  # → 3.12
└── aegis/               # Aegis (Automated-Remote-Org-Test)
    └── .python-version  # → 3.12
```

---

## Setup Workflow

Follow `docs/integration/isolated-testing-setup.md` for full steps. Summary:

### 1. Prerequisites

```bash
./scripts/validate_integration_prereqs.sh --scan     # inventory + conflicts
./scripts/validate_integration_prereqs.sh             # validate
./scripts/validate_integration_prereqs.sh --fix       # auto-install missing
```

### 2. Clone and pin

```bash
export RC_WORKSPACE=~/workspace/revenue-cloud
mkdir -p "$RC_WORKSPACE" && cd "$RC_WORKSPACE"

git clone <foundations-url> foundations
git clone <distill-url> distill
git clone <aegis-url> aegis          # requires VPN

cd distill && pyenv local 3.12 && cd ..
cd aegis   && pyenv local 3.12 && cd ..
```

### 3. Distill setup

```bash
cd "$RC_WORKSPACE/distill"
cp .env.example .env.local
./distill start                      # auto-creates .venv, installs deps
```

### 4. Aegis setup

```bash
cd "$RC_WORKSPACE/aegis"
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 5. Validate

```bash
# Distill
cd "$RC_WORKSPACE/distill" && pytest -m unit

# Aegis (dry-run — no org needed)
cd "$RC_WORKSPACE/aegis" && source venv/bin/activate
behave --dry-run features/RevenueGoFoundation/

# Cross-platform (provision org, export creds, run Aegis)
cd "$RC_WORKSPACE/foundations"
cci flow run prepare_rlm_org --org dev
```

---

## Common Conflicts

| Conflict | Detection | Resolution |
|----------|----------|------------|
| System Python 3.13+ / no pyenv 3.12 | `[CONFLICT]` in scan | `pyenv install 3.12` |
| Homebrew Python shadows pyenv | `[WARN]` in scan | `brew unlink python@3` or fix PATH order |
| Venv built with wrong Python | `[CONFLICT]` in scan | Delete venv, recreate with `python3 -m venv` |
| `.python-version` → missing version | `[CONFLICT]` in scan | `pyenv install <version>` |
| `.python-version` in Foundations | `[CONFLICT]` in scan | `rm foundations/.python-version` |
| pipx uses pyenv Python | `[WARN]` in scan | `PIPX_DEFAULT_PYTHON=/usr/bin/python3 pipx reinstall-all` |
| Homebrew Node shadows nvm | `[WARN]` in scan | `brew unlink node` |

---

## Credential Export (CCI → Aegis)

```bash
cd "$RC_WORKSPACE/foundations"
eval $(cci org info <alias> --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'export SF_URL=\"{d[\"instance_url\"]}/\"')
print(f'export SF_USERNAME=\"{d[\"username\"]}\"')
print(f'export SF_SESSION_ID=\"{d[\"access_token\"]}\"')
")
```

---

## Key Files

| File | Purpose |
|------|---------|
| `docs/integration/isolated-testing-setup.md` | Full setup guide (Sections 0–6) |
| `scripts/validate_integration_prereqs.sh` | Prerequisites validator (--scan/--fix) |
| `docs/integration/distill-integration.md` | Distill integration planning |
| `docs/integration/aegis-integration.md` | Aegis integration planning |
| `docs/integration/revenue-cloud-platform.md` | Platform overview (all 3 repos) |
| `docs/integration/project-analysis.md` | Deep technical analysis |
| `docs/integration/datasets-reorganization.md` | Data plan restructuring |

---

## Repository URLs

| Repository | URL | Access |
|-----------|-----|--------|
| Foundations | `https://github.com/salesforce-internal/revenue-cloud-foundations.git` | GitHub |
| Distill | `https://github.com/sf-industries/distill.git` | GitHub |
| Aegis | `https://git.soma.salesforce.com/industries/Automated-Remote-Org-Test.git` | GHE (VPN) |
