# Repository Audit Findings — 2026-04-01

Full audit of the rlm-base-dev repository against `AGENTS.md` rules,
`.cursor/skills/`, and `.cursor/rules/`. Findings ranked by priority.

---

## P0 — Security

### 1. `access_token` leaked via CLI and logs (`rlm_sfdmu.py`)

- **`LoadSFDMUData`** (line 336): falls back to `org_config.access_token` as
  `--targetusername` for non-scratch orgs. Token visible in `ps`, shell
  history, and logged at line 355 (`Executing command: ...`).
- **`ExtractSFDMUData`** (line 1092): same pattern — `access_token` used as
  `--sourceusername`.
- **Export.json logged in cleartext** (line 201): full `json.dumps` of
  export.json including the `accessToken` field.
- **Correct pattern exists** in `TestSFDMUIdempotency._get_org_for_cli()`
  (line 686) — uses `username`, raises error if unavailable.

**Fix:** Use `org_config.username` for CLI calls. Suppress or redact
`accessToken` from export.json log output.

### 2. Session token in Robot `log.html` (`SetupToggles.robot`)

- `Get Authenticated Setup Page Url` (line 16) runs `sf org open --url-only`
  without `Set Log Level NONE` wrapping.
- Affects all 5 setup test suites: `configure_revenue_settings`,
  `enable_analytics`, `enable_document_builder`,
  `enable_constraints_settings`, `reorder_app_launcher`.
- `E2ECommon.robot` does this correctly — use as reference.

**Fix:** Add `Set Log Level NONE` / `Set Log Level INFO` around
`Run Process sf org open` and the subsequent `Go To` call.

---

## P1 — Deploy Correctness

### 3. `Product2.object-meta.xml` still in `force-app/`

- `force-app/main/default/objects/Product2/Product2.object-meta.xml`
  contains **48 `<actionOverrides>`** and a `<compactLayoutAssignment>`.
- Per the strip-and-build rule, this should be in
  `templates/objects/base/Product2/` and deployed at step 29.
- All other 6 named objects (Asset, Quote, Order, OrderItem,
  QuoteLineItem, FulfillmentOrderLineItem) have been correctly moved.
- `.forceignore` needs an entry for this file.

**Fix:** Move to `templates/objects/base/Product2/`, add `.forceignore`
entry, update `rlm_ux_assembly.py` if needed.

### 4. SOQL in loop — `RLM_QuoteModelUtility.cls`

- Lines 18-24: two `[SELECT ...]` queries inside
  `for(QuoteLineItem ql : qls)` loop.
  - `QuoteLineItemAttribute WHERE QuoteLineItemId =: ql.Id`
  - `QuoteLineRelationship WHERE AssociatedQuoteLineId =: ql.Id`
- Risks hitting governor limits with large line item sets.

**Fix:** Bulk-query both objects before the loop using `IN :ids`, build
`Map<Id, List<...>>`, access from map inside loop.

---

## P2 — Reliability / Usability

### 5. Robot wrappers fall back to `org_config.name` (CCI alias)

6 files use `org_config.name` as fallback when `username` is None:
- `rlm_robot_e2e.py` (line 74)
- `rlm_reorder_app_launcher.py` (line 128)
- `rlm_analytics.py` (line 46)
- `rlm_enable_document_builder_toggle.py` (line 44)
- `rlm_enable_constraints_settings.py` (line 57)
- `rlm_configure_revenue_settings.py` (line 67)

The CCI alias (e.g., `beta`) won't resolve for `sf org open`. Should
raise an error instead of silently using a bad identifier.

**Fix:** Remove fallback; raise `TaskOptionsError` if `username` is None.

### 6. 25 tasks missing `group:` in `cumulusci.yml`

Mostly `deploy_*` tasks (lines 895-1299). These don't appear grouped in
`cci task list` output.

**Fix:** Add appropriate `group:` to each (most should be
`Revenue Lifecycle Management`).

### 7. `access_token` exposed as `task_options` entry

5 files allow `access_token` to be passed via CLI `-o access_token <TOKEN>`:
- `rlm_context_service.py`
- `rlm_extend_stdctx.py`
- `rlm_modify_context.py`
- `rlm_sync_pricing_data.py`
- `rlm_refresh_decision_table.py`

Token would be visible in `ps` output and shell history.

**Fix:** Remove `access_token` from `task_options`; use
`self.org_config.access_token` directly.

---

## P3 — Code Quality / Documentation

### 8. 28 flows missing `description:`

Only 7 of 35 flows have descriptions. Missing on major flows including
`prepare_rlm_org`, `prepare_core`, `prepare_billing`, etc.

**Fix:** Add `description:` to all flows.

### 9. Missing import guards (5 files)

These files import CCI modules without `try/except ImportError`:
- `rlm_context_service.py`
- `rlm_extend_stdctx.py`
- `rlm_modify_context.py`
- `rlm_sync_pricing_data.py`
- `rlm_refresh_decision_table.py`

`rlm_sfdmu.py` has an import guard but doesn't define fallback symbols
(commented out).

**Fix:** Add standard `try/except ImportError` with fallback symbols.

### 10. `composed: true` missing on form submit event

`E2ECommon.robot` line 856: `new Event('submit', {bubbles: true, cancelable: true})`
is missing `composed: true`. Low risk since the form and listener are
likely in the same shadow tree.

**Fix:** Add `composed: true` for consistency.

### 11. Duplicate `classAccesses` in Admin profile

`force-app/main/default/profiles/Admin.profile-meta.xml` has
`RLM_OrderItemContractingUtility` listed twice. May cause deploy warnings.

**Fix:** Remove the duplicate entry.

### 12. Undeclared `psg_debug` feature flag

Used in `when:` clauses at lines 2315 and 2342 of `cumulusci.yml` but
not declared in `project.custom`. These steps will never execute.

**Fix:** Either declare the flag (default `false`) or remove the steps.

### 13. `Input Text` on LWC inputs (`configure_revenue_settings.robot`)

Two uses of standard Selenium `Input Text` on Revenue Settings LWC
page (lines 278, 327). May not trigger LWC reactive change detection.
Currently works because `Press Keys CTRL+a DELETE` precedes the input.

**Investigate:** Verify these inputs are reliably saved. If not, switch
to the native setter pattern from `E2ECommon.robot` line 797.

### 14. Mixed `qb_` / `quantumbit_` naming prefixes

Older tasks use `insert_quantumbit_*_data`, newer use `insert_qb_*_data`.
Both patterns coexist. Not a functional issue but reduces discoverability.

**Consider:** Standardize on `qb_` prefix for all new tasks.

---

## Backlog — SFDMU v5 Bug 3 Violations

~80+ objects across 20 export.json files use `Upsert` with
relationship-traversal externalId. These will create duplicates on
re-run (v5 Bug 3). Changing to `Insert + deleteOldData: true` requires
explicit user approval per plan since it's destructive.

### Compliant plans (reference)

`qb-pricing`, `qb-rates`, `qb-guidedselling` — use
`Insert + deleteOldData: true` with `$comment` fields.

### Non-compliant plans

**Older QB plans (~15 objects):**
- `qb-pcm` (6 objects including ProductRelatedComponent, ProductCategoryProduct)
- `qb-billing` (3: PaymentTermItem, BillingTreatmentItem, GeneralLedgerAcctAsgntRule)
- `qb-dro` (1: FulfillmentWorkspaceItem)
- `qb-clm` (1: DocumentClauseSet)
- `qb-prm` (1: ChannelProgramMember)
- `qb-rating` (1: UsagePrdGrantBindingPolicy)

**Q3 family (~30 objects):**
- `q3-multicurrency` (21 objects — largest single file)
- `q3-rates` (3: PriceBookRateCard, RateCardEntry, RateAdjustmentByTier)
- `q3-rating` (2: ProductUsageGrant, UsagePrdGrantBindingPolicy)
- `q3-dro` (5: FulfillmentStepDefinition, etc.)
- `q3-billing` (5: PaymentTermItem, BillingTreatment, etc.)

**MFG family (~25 objects):**
- `mfg-multicurrency` (21 objects — mirrors q3-multicurrency)
- `mfg-constraints-p` (1: ExpressionSetConstraintObj)
- `mfg-constraints-prc` (1: ExpressionSetConstraintObj)
- `mfg-configflow` (1: ProductConfigFlowAssignment)

**Procedure plans (1 object):**
- `procedure-plans` (ProcedurePlanOption)

### Idempotency note

`qb-pricing` uses `Insert` without `deleteOldData: true` for 6 objects
(PriceAdjustmentTier, AttributeAdjustmentCondition, etc.). These avoid
the v5 bug crashes but are **not idempotent** — re-runs create duplicates.

---

## Passed Audits (No Action Needed)

| Area | Status |
|------|--------|
| PRM Network email placeholder | PASS — `rlm-network-sender@example.com` |
| Payments site username placeholder | PASS — `payments-site-admin@example.com` |
| .forceignore alignment | PASS — all 6 objects + flexipages/layouts/compactLayouts covered |
| UX template traceability | PASS — `assembly_manifest.json` with 86 items |
| No EmailTemplatePage in templates | PASS |
| AppSwitcher template exists | PASS |
| Force-app has no flexipages/layouts | PASS |
| SFDMU externalId delimiter format | PASS — all use `;` |
| SFDMU apiVersion | PASS — all `66.0` |
| SFDMU object ordering | PASS — parent → child |
| SFDMU empty CSV handling | PASS |
| Apex deactivation-before-deletion | PASS |
| Apex deletion ordering | PASS — child → parent |
| No `//` comments in Robot JS | PASS |
| Robot E2E auth wrapping | PASS |
| All CCI tasks have descriptions | PASS |
| All CCI flows have groups | PASS |
| All Python tasks have `_run_task()` | PASS |
