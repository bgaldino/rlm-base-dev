# CLAUDE.md — Revenue Cloud Base Foundations

> This file guides Claude Code when reviewing or working with this repository.

## Project Overview

**Revenue Cloud Base Foundations** automates creation and configuration of Salesforce environments for Revenue Lifecycle Management (RLM). It targets Salesforce Release 260 (Spring '26, API v66.0).

Key technology stack:
- **CumulusCI (CCI)** — orchestration engine for tasks and flows
- **SFDMU v5** — data import/export (`sf sfdmu run`). **v5.0.0+ required; v4 is not supported.**
- **Salesforce DX / `sf` CLI** — metadata deployment and org management
- **Python** — custom CCI task classes in `tasks/`
- **Apex** — post-load activation scripts in `scripts/apex/`

---

## Repository Layout

```
cumulusci.yml               # Project configuration, task/flow definitions, feature flags
tasks/                      # Custom Python CCI task classes
  rlm_sfdmu.py              # SFDMU load, extract, delete, idempotency tasks
  rlm_apex_file.py          # Run Apex from file
  rlm_manage_decision_tables.py
  rlm_manage_expression_sets.py
  ... (other custom tasks)
datasets/sfdmu/             # SFDMU data plans
  qb/en-US/                 # QuantumBit (QB) product data plans
    qb-pcm/                 # Product catalog master
    qb-pricing/             # Price books, adjustments, tiers
    qb-billing/             # Billing policies, treatments, payment terms
    qb-tax/                 # Tax policies and treatments
    qb-rating/              # Usage-based rating (PUR, PURP, PUG)
    qb-rates/               # Rate cards, rate card entries, adjustment tiers
    qb-clm/                 # Contract lifecycle management
    qb-dro/                 # Dynamic revenue orchestration
    qb-guidedselling/       # Guided selling
    qb-transactionprocessingtypes/
  mfg/en-US/                # Manufacturing product data plans
  q3/en-US/                 # Q3 product data plans
scripts/apex/               # Apex activation and maintenance scripts
scripts/post_process_extraction.py  # Adds $$ composite key columns after extraction
scripts/validate_sfdmu_v5_datasets.py  # Validates/fixes SFDMU v5 compliance
scripts/sync_appmenu_from_user.py  # Retrieve running user's App Launcher order into post_tso_appmenu (no deploy)
unpackaged/post_tso_appmenu/ # App Launcher (AppSwitcher) order; deployed only when tso=true (deploy_post_tso_app_menu)
force-app/                  # Salesforce metadata (SFDX format)
docs/                       # Technical documentation
  sfdmu_composite_key_optimizations.md  # SFDMU v5 migration notes (READ THIS)
```

---

## SFDMU v5 — Critical Rules

SFDMU v5 introduced breaking changes. All data plans **must** comply with the following.

### externalId Format

- **Use `;` delimiters** — `Field1;Field2` (NOT `$$Field1$Field2`, which is v4 syntax)
- **Composite `$$` columns in CSVs** are still valid for Upsert target-record matching; the `$$` column name convention is correct at the CSV level

### The Three Confirmed v5 Bugs

> See `docs/sfdmu_composite_key_optimizations.md` for full details.

**Bug 1 — All-multi-hop externalId fails validation**
Objects whose `externalId` contains ONLY relationship-traversal components (2+ hops) get:
`{Object} has no mandatory external Id field definition`
**Fix:** Use at least one direct field as the `externalId`.

**Bug 2 — 2-hop traversal columns cause SOQL injection in Upsert**
SFDMU strips the first-hop prefix from 2-hop CSV columns when building the Upsert TARGET SELECT,
producing invalid SOQL (e.g. `Product.StockKeepingUnit` instead of `ProductUsageResource.Product.StockKeepingUnit`).
**Fix:** Use `operation: Insert` + `deleteOldData: true` — Insert skips the TARGET SELECT phase.

**Bug 3 — Upsert with relationship-traversal externalId never matches; always inserts**
Even 1-hop relationship traversals in `externalId` (e.g. `Product.StockKeepingUnit;UsageResource.Code`)
cause Upsert to always insert instead of matching, creating duplicates on every run.
**Fix:** Use `operation: Insert` + `deleteOldData: true` for all such objects.
*Upstream issue: [forcedotcom/SFDX-Data-Move-Utility#781](https://github.com/forcedotcom/SFDX-Data-Move-Utility/issues/781)*

### Safe Patterns for export.json

| Situation | Pattern |
|-----------|---------|
| Object has a direct unique field (e.g. `Name`, `ExternalId__c`) | `operation: Upsert`, `externalId: Name` |
| Composite uniqueness, all fields are direct | `operation: Upsert`, `externalId: Field1;Field2`, `$$Field1$Field2` column in CSV |
| externalId uses any relationship traversal | `operation: Insert`, `deleteOldData: true` |
| Auto-number `Name`, all-relationship externalId | `operation: Insert`, `deleteOldData: true` |
| Empty CSV (no records yet) | `excluded: true` — prevents destructive delete-on-load |

### deleteOldData Deletion Order

SFDMU deletes `deleteOldData: true` objects in **reverse array order** (last object in `objects` array
is deleted first). Always order objects **parent → child** in the array; deletions will naturally
run **child → parent**, satisfying FK constraints.

### Extraction Roundtrip Caveat

SFDMU v5 does **not** write `$$` composite key columns during extraction. The
`scripts/post_process_extraction.py` script adds these columns from the extracted relationship
columns, making outputs re-import-ready. Always use processed extraction output for re-import.

---

## Python Task Classes (`tasks/rlm_sfdmu.py`)

### `LoadSFDMUData`
Wraps `sf sfdmu run --sourceusername CSVFILE`. Key option: `pathtoexportjson` (directory).

### Deleting data plans

Deletes are implemented as Apex scripts (not a Python task class). Each plan has a dedicated
`delete_qb_<plan>_data` CCI task that runs an Apex script to deactivate and delete records in
dependency order. Key scripts:
- `scripts/apex/deleteQbRatingData.apex` — deactivates then deletes PUG → PURP → PUR
- `scripts/apex/deleteQbRatesData.apex` — deletes rate card data (must run before deleteQbRatingData; rates FK to PURs)

Always run `delete_qb_rates_data` before `delete_qb_rating_data` to satisfy FK constraints.

### `TestSFDMUIdempotency`
Runs an SFDMU load twice and asserts record counts don't increase. Supports `use_extraction_roundtrip`
(extract + post-process + re-import between runs).

### `ExtractSFDMUData`
Wraps `sf sfdmu run --targetusername CSVFILE`. Runs `post_process_extraction.py` automatically.

---

## CumulusCI Conventions

### Task Definitions
```yaml
tasks:
  my_task_name:
    group: Data Maintenance           # Required — groups tasks in `cci task list`
    description: >
      One or two sentence description. Be specific about which objects/SObjects are affected.
    class_path: tasks.rlm_sfdmu.LoadSFDMUData
    options:
      pathtoexportjson: datasets/sfdmu/qb/en-US/qb-pricing
```

### Naming Conventions
- `insert_qb_<plan>_data` — loads data plan
- `delete_qb_<plan>_data` or `delete_quantumbit_<plan>_data` — deletes plan data
- `extract_qb_<plan>_data` — extracts from org
- `test_qb_<plan>_idempotency` — idempotency test
- `activate_<thing>` — runs an Apex activation script

### Feature Flags
Controlled via `project → custom` in `cumulusci.yml`. Boolean flags like `qb`, `rating`, `rates`,
`billing`, `tax`, `dro` gate which flows and tasks run. Check `when:` conditions in flows.

---

## App Launcher (TSO) and PRM Network Email

### App Launcher (AppSwitcher)
- **Repo:** `unpackaged/post_tso_appmenu/appMenus/AppSwitcher.appMenu-meta.xml` holds the desired org-default App Launcher order. Use a non–personally identifiable source; the repo should not store org-specific emails.
- **Capture user order:** Run `python scripts/sync_appmenu_from_user.py` with the default org set to the org where the user has customized the App Launcher. The script queries `UserAppMenuCustomization` and `AppMenuItem`, writes the order to the file. No deploy.
- **Deploy:** Task `deploy_post_tso_app_menu` deploys that path; it runs only when `tso=true` (step 5 of `prepare_tso`, after `deploy_post_tso`). New users get the org default; existing users who personalized may need "Reset to default" in the App Launcher.

### PRM Network emailSenderAddress
- **Repo:** `unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml` uses a **placeholder** `emailSenderAddress` (e.g. `rlm-network-sender@example.com`) so the repo never stores a real email.
- **Deploy time:** Task `patch_network_email_for_deploy` (before `deploy_post_prm`) replaces the placeholder with the **target org running user's email** so the metadata deploy succeeds. Task `revert_network_email_after_deploy` (after `deploy_post_prm`) restores the placeholder so the repo is never left with the org email. Both tasks are in `tasks/rlm_community.py`.

---

## Apex Scripts (`scripts/apex/`)

- `activateRatingRecords.apex` — 7-step PUR/PUG activation (complex platform ordering)
- `deleteQbRatingData.apex` — deactivates then deletes PUG → PURP → PUR
- `deleteQbRatesData.apex` — deletes rates data (must run before deleteQbRatingData; rates FK to PURs)
- Activation scripts generally: query records, set `Status = 'Active'` (or equivalent), update

**Review checklist for Apex:**
- No SOQL in loops
- Bulk-safe (use `update records;` not `update record;` in a loop)
- Deactivation before deletion where platform requires it (PUR, PUG, rate card entries)

---

## Data Plan Review Checklist

When reviewing `export.json` changes:

- [ ] externalId uses `;` delimiters (not `$$`)
- [ ] No 2-hop traversal fields in externalId without `operation: Insert` + `deleteOldData: true`
- [ ] ORDER BY fields are present in the SELECT clause
- [ ] Relationship traversal columns in SOQL match what CSV headers expect
- [ ] Empty CSVs have `excluded: true` (prevents destructive wipe when records are added later)
- [ ] Objects ordered parent → child (deleteOldData reverse-order safety)
- [ ] `$$` composite key columns in CSV headers match the `externalId` fields exactly

---

## Environment Setup (macOS)

See `## macOS Environment Setup (Homebrew + pyenv + nvm)` section in README.md for the authoritative step-by-step guide. Key notes for AI agents assisting new users:

- **nvm** via `brew install nvm` is the recommended Node.js version manager — prevents conflicts with system Node. Use `nvm install --lts` and `nvm alias default lts/*`. **LTS versions only** (even-numbered: v20, v22, v24). Odd-numbered releases (v21, v23, v25) are not supported by sf CLI (see forcedotcom/cli#3460).
- **sf CLI** must be installed via `npm install -g @salesforce/cli` (NOT `brew install sf` or `brew install --cask sf`). The Homebrew formula/cask bundles its own Node and is deprecated; the npm install uses the nvm-managed Node.
- **pyenv** via `brew install pyenv` is the recommended Python version manager; **Python 3.13 recommended for CCI** (3.14 has known dependency issues; 3.12 is also supported). Install the latest stable 3.13.x patch: `PYTHON_VERSION=$(pyenv install --list | grep -E "^[[:space:]]*3\.13\.[0-9]+$" | tail -1 | tr -d '[:space:]') && pyenv install "$PYTHON_VERSION" && pyenv global "$PYTHON_VERSION"`.
- **pipx** is preferred for CumulusCI: install pipx via pyenv (`$(pyenv prefix)/bin/python3 -m pip install --user pipx`), NOT `brew install pipx` (Homebrew pipx uses its own bundled Python, not pyenv). Then: `pipx install cumulusci --python "$(pyenv prefix)/bin/python3"` and `pipx inject cumulusci "setuptools<71"`. Ensure `pyenv global` is set to a supported Python (3.12 or 3.13; 3.13 recommended) before running. The setuptools pin is required — CCI 4.x depends on `pyfilesystem2` which needs `pkg_resources` removed in setuptools 71+.
- **~/.zshenv** must include nvm and pyenv init for non-interactive shells (IDE tools, CI, Claude Code). Without it, `sf` and `node` are not found in those contexts. Add both blocks to `~/.zshenv` AND `~/.zshrc`.
- **venv** should be created at repo root (`.venv/`) for running `scripts/` and `tasks/` outside CCI
- **validate_setup** (`cci task run validate_setup`) is the built-in environment checker — checks Python, CCI, sf CLI, SFDMU, Node.js, Robot deps. Runs without an org. Auto-fixes outdated SFDMU by default.
- Robot Framework deps (for headless tasks) are defined in `robot/requirements.txt`. Install/update via `pipx inject cumulusci -r robot/requirements.txt`, or run `cci task run validate_setup` — `auto_fix_robot=true` (default) auto-installs them when missing

---

## Common Workflows

```bash
# Load a data plan
cci task run insert_quantumbit_pricing_data --org beta

# Delete a data plan (before re-loading to avoid duplicates)
cci task run delete_quantumbit_pricing_data --org beta

# Extract from org
cci task run extract_qb_pricing_data --org beta

# Test idempotency
cci task run test_qb_pricing_idempotency --org beta

# Activate records after load
cci task run activate_rating_records --org beta

# Full QB setup flow
cci flow run prepare_rlm_org --org beta

# Validate SFDMU v5 dataset compliance
python scripts/validate_sfdmu_v5_datasets.py
python scripts/validate_sfdmu_v5_datasets.py --fix-all --dry-run

# Capture running user's App Launcher order into repo (no deploy)
python scripts/sync_appmenu_from_user.py
# Deploy App Launcher (when tso=true the flow runs deploy_post_tso_app_menu automatically)
cci task run deploy_post_tso_app_menu --org <alias>
```

---

## PR Review Focus Areas

1. **SFDMU v5 compliance** — externalId format, operation + deleteOldData choices (see above)
2. **Idempotency safety** — can the plan be run twice without creating duplicates?
3. **`DeleteSFDMUData` task correctness** — pagination guard, object_sets normalization, HTTP status handling
4. **cumulusci.yml** — task group, description accuracy (don't list excluded objects), feature flag conditions
5. **README accuracy** — object tables, operation columns, deletion order footnotes
6. **Apex bulk safety** — no SOQL in loops, no single-record DML in loops
7. **CSV header alignment** — `$$` columns must match externalId fields; empty header files need blank first line
8. **PRM Network email** — repo must use placeholder only; patch/revert tasks must run in correct order (patch before deploy_post_prm, revert after). No real email in committed rlm.network-meta.xml.
9. **App Launcher** — post_tso_appmenu deployed only when tso=true; sync_appmenu_from_user.py retrieves user order only (no deploy).
