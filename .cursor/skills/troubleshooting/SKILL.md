# Troubleshooting & Common Errors

Use this skill when diagnosing failures in the rlm-base-dev build pipeline,
data loading, metadata deployment, or local environment setup.

## Quick Rules

1. Run `cci task run validate_setup` first — it checks everything.
2. CCI alias `beta` ≠ SF CLI alias `rlm-base__beta`. Never mix them.
3. SFDMU load fails → check stdout for specific object error.
4. Duplicates on re-run → missing `$$` composite key column in CSV.
5. Rating errors → always delete rates before rating (FK constraint).
6. Deploy fails → check for missing fields or wrong deploy order.
7. Source tracking corrupt → `rm -rf .sf/orgs/<org-id>/localSourceTracking`
8. Active billing records → can NEVER be deleted (platform constraint).

---

## Quick Diagnosis: Which Step Failed?

The `prepare_rlm_org` flow runs 31 steps. Identify the failing step from
CCI output, then jump to the relevant section below.

| Step Range | Category | Section |
|-----------|----------|---------|
| 1 (prepare_core) | PSLs, PSGs, context defs, deploy_pre | [Permission & PSG Errors](#permission--psg-errors), [Context Definition Errors](#context-definition-errors) |
| 2–3 | Decision tables, expression sets | [Decision Table Errors](#decision-table-errors), [Expression Set Errors](#expression-set-errors) |
| 5 (deploy_full) | Metadata deploy (force-app) | [Metadata Deploy Errors](#metadata-deploy-errors) |
| 9–11 | Product/pricing data load | [SFDMU Data Loading Errors](#sfdmu-data-loading-errors) |
| 12 (prepare_docgen) | DocGen | [DocGen Errors](#docgen-errors) |
| 13 (prepare_dro) | DRO data load | [SFDMU Data Loading Errors](#sfdmu-data-loading-errors) |
| 14–15 | Tax/billing data + activation | [Billing & Tax Errors](#billing--tax-errors) |
| 18 (prepare_rating) | Rating/rates data + activation | [Rating & Rates Errors](#rating--rates-errors) |
| 22 (prepare_prm) | PRM community + data | [PRM & Community Errors](#prm--community-errors) |
| 24 (prepare_constraints) | Constraints + CML import | [Constraints / CML Errors](#constraints--cml-errors) |
| 29 (prepare_ux) | UX assembly + deploy | [UX Assembly Errors](#ux-assembly-errors) |
| 30 | Decision table refresh | [Decision Table Errors](#decision-table-errors) |

---

## Environment & Setup Errors

### `cci task run validate_setup` fails

Run this first — it checks everything:

| Check | Fix |
|-------|-----|
| Python < 3.8 | Install Python 3.12 or 3.13 via `pyenv` |
| CumulusCI not found | `pipx install cumulusci --python "$(pyenv prefix)/bin/python3"` |
| SF CLI < v2 | `npm install -g @salesforce/cli` (NOT `brew install sf`) |
| SFDMU plugin missing/outdated | Auto-fixed by default (`auto_fix=true`). Manual: `sf plugins install sfdmu` |
| Node.js not found | `nvm install --lts && nvm alias default lts/*` |
| Robot Framework deps missing | Auto-fixed by default. Manual: `pipx inject cumulusci --force -r robot/requirements.txt` |
| Chrome/ChromeDriver missing | Install Chrome; `pip install webdriver-manager` |
| urllib3 < 2.6.3 (CVE) | `pipx inject cumulusci urllib3>=2.6.3` |

### `sf` or `node` not found in IDE / CI

**Cause:** `~/.zshenv` is missing nvm/pyenv init blocks. Non-interactive
shells (IDE terminals, CI runners) don't source `~/.zshrc`.

**Fix:** Add both nvm and pyenv init to `~/.zshenv` AND `~/.zshrc`.

### "Org not found" or "auth failed" errors

CCI and `sf` CLI maintain **separate org registries** with different aliases.

| Tool | Alias Format | Example |
|------|-------------|---------|
| `cci` (`--org`) | Short alias | `beta` |
| `sf` (`--target-org`) | Project-prefixed | `rlm-base__beta` |
| Either | Username (always works) | `test-abc123@example.com` |

**Common mistakes:**
- Using CCI alias `beta` with `sf` CLI → **fails** (use `rlm-base__beta`)
- Using SF CLI alias `rlm-base__beta` with `cci` → **fails** (use `beta`)
- Using `org_config.access_token` as `--target-org` → **fails** + leaks secret

**In Python tasks:** Always use `self.org_config.username` for `sf` CLI
calls. Use `self.org_config.access_token` + `.instance_url` only for
direct REST API calls via `requests`.

```bash
# Find the right identifier
cci org list              # shows CCI aliases
sf org list               # shows sf aliases (rlm-base__* prefix)
cci org info beta         # shows username, instance URL
```

---

## SFDMU Data Loading Errors

### Load fails with non-zero exit code

Check the SFDMU stdout for the specific object and error. Common causes:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `has no mandatory external Id field definition` | All-multi-hop externalId (SFDMU v5 Bug 1) | Add a direct field to `externalId` |
| Invalid SOQL generated | 2-hop traversal column in Upsert (v5 Bug 2) | Switch to `Insert` + `deleteOldData: true` |
| Duplicates on every run | Relationship-traversal externalId in Upsert (v5 Bug 3) | Switch to `Insert` + `deleteOldData: true` |
| `REQUIRED_FIELD_MISSING` | Parent records not loaded yet | Check plan dependency order (PCM before pricing/billing) |
| `DUPLICATE_VALUE` | Composite key mismatch | Verify `$$` column in CSV matches `externalId` fields |

### Idempotency test fails (record count increased)

**Cause:** Missing or mismatched `$$` composite key column in the CSV. The
second load inserts instead of matching.

**Fix:** Verify that `$$` column header in CSV matches the `externalId`
fields exactly (e.g., `externalId: "Field1;Field2"` → CSV header
`$$Field1$Field2`). Run `python scripts/validate_sfdmu_v5_datasets.py` to
check all plans.

### Dynamic `AssignedTo` user lookup fails

**Cause:** `dynamic_assigned_to_user: true` queries the org for a user, but
the org auth is token-only (no username).

**Fix:** Use `cci org connect` instead of JWT-only auth, or set the username
in the org config.

---

## Metadata Deploy Errors

### Deploy fails with component errors

Check the deploy result for specific component names. Common causes:

| Component Type | Likely Cause | Fix |
|---------------|-------------|-----|
| FlexiPage | References object/field not yet deployed | Ensure the referenced metadata is in `force-app/` or deployed in an earlier step |
| Layout | References field that doesn't exist | Add the field to the pre-deploy bundle |
| Profile | Contains `layoutAssignment` in `force-app/` | **Never** add layout assignments to `force-app/` profiles — use `templates/profiles/` |
| ExpressionSet | `__ATTRIBUTEPasID__` not replaced | XPath transform query failed — check `PriceAdjustmentSchedule` records exist |

### Deploy timeout (600s for UX, 300s for stamp)

**Cause:** Slow org response or large deploy payload.

**Fix:** Retry. If persistent, check org health and reduce deploy size by
using `metadata_type` or `metadata_name` options on `assemble_and_deploy_ux`.

### Source tracking corruption

**Symptom:** Deploy succeeds but `sf project deploy` complains about
conflicts on subsequent runs.

**Fix:**
```bash
rm -rf .sf/orgs/<org-id>/localSourceTracking
```

---

## Permission & PSG Errors

### Permission Set Group stuck in "Outdated"

**Cause:** PSG needs recalculation after PSL changes or deploy.

**Fix:** The `recalculate_permission_set_groups` task handles this
automatically — it touches the PSG Description field to trigger recalc,
then polls. If it times out:
1. Check PSG status in Setup → Permission Set Groups
2. Manually trigger recalculation
3. Increase `timeout_seconds` option (default 300s)

### PSG recalculation fails with "Failed" status

**Cause:** Conflicting permissions in the PSG's member permission sets.

**Fix:** Check Setup → Permission Set Groups → the failing PSG for conflict
details. Remove conflicting permission set members.

---

## Context Definition Errors

### `INSUFFICIENT_ACCESS` on context plan apply

**Cause:** Connect API PATCH rejects relationship-traversal hydration rules.

**Fix:** This is handled automatically by the task — it falls back to
direct SObject REST API calls for `ContextAttributeMapping` and
`ContextAttrHydrationDetail` records. If it still fails, verify the running
user has the correct PSLs assigned.

### Context definition not found

**Cause:** `developer_name` doesn't match any existing context definition.

**Fix:** Context definitions are extended at runtime by `extend_context_*`
tasks in `prepare_core` (step 1). Ensure `prepare_core` ran successfully
before the failing step.

---

## Decision Table Errors

### Refresh timeout

**Cause:** Decision table refresh can be slow, especially for large tables
with many entries.

**Fix:** Retry. If persistent, try refreshing tables individually:
```bash
cci task run manage_decision_tables -o operation refresh -o developer_names "Table_Name" --org beta
```

### Active decision tables block deploy

**Cause:** Metadata API can't overwrite active decision tables.

**Fix:** The flow handles this via `exclude_active_decision_tables` before
deploy and `restore_decision_tables` after. If the exclusion step fails,
manually deactivate the blocking tables:
```bash
cci task run manage_decision_tables -o operation deactivate -o developer_names "Table_Name" --org beta
```

---

## Expression Set Errors

### Row lock during activation/deactivation

**Symptom:** `UNABLE_TO_LOCK_ROW` error.

**Cause:** Concurrent access to expression set version records.

**Fix:** Automatic — the task retries 3 times with linear backoff (2s, 4s,
6s). If it still fails, wait and retry manually.

### Expression set activated without Rank

**Symptom:** Expression set version can't be deactivated or edited.

**Fix:** The `updateExpressionSetVersions.apex` script sets Rank before
activating. If you hit this manually, use Tooling API to update the version's
Rank field first.

---

## Rating & Rates Errors

### PUR activation fails: "effective period overlaps"

**Cause:** Duplicate Draft PURs exist (from re-running the plan without
deleting first).

**Fix:**
1. Delete rates data first: `cci task run delete_qb_rates_data --org beta`
2. Delete rating data: `cci task run delete_qb_rating_data --org beta`
3. Re-load: `cci task run insert_qb_rating_data --org beta`

**Critical:** Always delete rates before rating (FK constraint).

### PUR deactivation ordering

**Cause:** Platform requires PURs to be deactivated in a specific order —
can't deactivate a PUR when related PURs on the same Product are still Active.

**Fix:** The `deleteQbRatingData.apex` script handles this with iterative
`Database.update(records, false)` (partial success) in a loop until all
are deactivated. If it hangs, check for PURs with unexpected relationships.

### Rate card entry deletion blocked

**Cause:** Can't delete rate adjustment records when related rate card entries
are inactive.

**Fix:** `deleteQbRatesData.apex` deletes in correct dependency order:
RateAdjustmentByTier → RateCardEntry → PriceBookRateCard → RateCard.

---

## Billing & Tax Errors

### Active billing records can't be deleted

**Cause:** Platform constraint — Active `BillingTreatment` and
`BillingTreatmentItem` records can never be deleted.

**Fix:** `deleteDraftBillingRecords.apex` only deletes Draft records. Active
billing records must be deactivated before deletion (if the platform allows),
or the org must be recreated.

### BillingTreatment missing BillingPolicyId

**Cause:** Data load ordering issue — BillingTreatment loaded before its
parent BillingPolicy.

**Fix:** Validate structure first:
```bash
cci task run validate_billing_structure --org beta
```
Then reload: delete billing data and re-run `insert_billing_data`.

---

## DocGen Errors

### DocumentTemplate binary mismatch

**Symptom:** All DocumentTemplates have the same binary content after deploy.

**Cause:** Salesforce Metadata API bug — all DocumentTemplates deployed in a
single batch receive the same ContentDocument binary (first alphabetically).

**Fix:** The `fix_document_template_binaries` task corrects this by uploading
the correct `.dt` binary for each template. Ensure it runs after
`deploy_post_docgen` + `activate_docgen_templates`.

### EmailTemplatePage deploy fails

**Cause:** `EmailTemplatePage` flexipages cannot be deployed via Metadata API
(permanent platform restriction).

**Fix:** These are in `.forceignore`. The templates are created at runtime by
`create_approval_email_templates` via the REST API. Do NOT add
`EmailTemplatePage` files to `templates/flexipages/`.

---

## UX Assembly Errors

### AppSwitcher deploy blocked

**Symptom:** AppSwitcher excluded from deploy; warning logged.

**Cause:** Org's AppMenu contains managed ConnectedApp or Network entries that
the Metadata API can't validate.

**Fix:** This is by design. The `reorder_app_launcher` task (step 2 of
`prepare_ux`) handles App Launcher ordering via Aura XHR. No action needed.

### Assembled UX has wrong content

**Cause:** Editing `unpackaged/post_ux/` directly instead of `templates/`.

**Fix:** Edit the source templates, then re-assemble:
```bash
cci task run assemble_and_deploy_ux -o deploy false --org dev-sb0
```
Inspect `unpackaged/post_ux/` to verify, then deploy.

---

## PRM & Community Errors

### Network deploy fails (emailSenderAddress)

**Cause:** The committed `rlm.network-meta.xml` uses a placeholder email.
The `patch_network_email_for_deploy` task replaces it with the org's actual
email before deploy.

**Fix:** If the patch task fails, the Network's email is immutable after
creation. Verify the Network exists with:
```bash
sf data query -q "SELECT Id, Name, UrlPathPrefix FROM Network" --target-org rlm-base__beta
```

### Placeholder email committed to repo

**Cause:** `revert_network_email_after_deploy` didn't run after deploy.

**Fix:** Run it manually:
```bash
cci task run revert_network_email_after_deploy --org beta
```
Or reset the file: `git checkout -- unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml`

---

## Constraints / CML Errors

### Unresolved ESC associations

**Cause:** Product catalog (qb-pcm) not loaded before constraint model
import.

**Fix:**
1. Load PCM data: `cci task run insert_quantumbit_pcm_data --org beta`
2. Retry import: `cci task run import_cml -o data_dir <path> --org beta`

---

## DRO Errors

### ProductFulfillmentDecompRule missing ExecuteOnRuleId

**Cause:** Salesforce 260 platform bug — `ExecuteOnRuleId` not created on
INSERT.

**Fix:** The `update_product_fulfillment_decomp_rules` task re-saves the
records to trigger ruleset generation. If it still fails, manually re-save
in Setup.

---

## Timeout Reference

| Operation | Default Timeout |
|-----------|----------------|
| Apex execution (`sf apex run`) | 300s (5 min) |
| UX metadata deploy | 600s (10 min) |
| Stamp commit deploy | 300s (5 min) |
| PSG recalculation (per attempt) | 300s |
| PSG retry delay between attempts | 120s |
| SFDMU record count query | 60s per object |
| Pricing schedule repair | 6 × 10s polls |
| Row-lock retry backoff | 2s, 4s, 6s |
| GitHub Actions workflow | 120 min total |

---

## Diagnostic Commands

```bash
# Validate local setup
cci task run validate_setup

# Check org build info
sf data query -q "SELECT DeveloperName, RLM_Commit_Hash__c, RLM_Branch__c, \
  RLM_Build_Timestamp__c, RLM_Feature_Flags__c FROM RLM_Build_Info__mdt" --target-org rlm-base__beta

# Validate SFDMU datasets
python scripts/validate_sfdmu_v5_datasets.py

# Check billing structure
cci task run validate_billing_structure --org beta

# Query billing state
cci task run query_billing_state --org beta

# List decision tables with status
cci task run manage_decision_tables -o operation list --org beta

# List expression sets
cci task run manage_expression_sets -o operation list --org beta

# UX dry-run (assemble without deploy)
cci task run assemble_and_deploy_ux -o deploy false --org dev-sb0

# Clear source tracking corruption
rm -rf .sf/orgs/<org-id>/localSourceTracking

# Validate CML constraint model
cci task run validate_cml -o data_dir datasets/constraints/qb/QuantumBitComplete --org beta
```
