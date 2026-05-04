# Dynamic UX Assembly

> Implemented in: `tasks/rlm_ux_assembly.py`, `tasks/rlm_writeback_ux.py`,
> `tasks/rlm_retrieve_ux.py`, `tasks/rlm_diff_ux.py`
> Shared utilities: `tasks/rlm_ux_utils.py` (feature flags, standalone order, source resolver)
> Flows: `prepare_ux`, `prepare_mfg_ux`, `capture_ux_drift`, `apply_ux_drift`
> Template root: `templates/`
> Output: `unpackaged/post_ux/` (git-tracked), `unpackaged/post_manufacturing_ux/` (git-tracked, Badger only)

---

## Overview

Dynamic UX Assembly replaces the previous approach of maintaining duplicate, hand-edited
UX metadata files scattered across every `unpackaged/post_*` feature directory. Instead, a
single late-stage CCI task (`assemble_and_deploy_ux`) builds the correct version of every
UX artifact from composable templates and feature-flag-driven logic, then deploys them all
in one `sf project deploy start` call at **step 29** of `prepare_rlm_org` (immediately
before `prepare_badger_flow` at step 30 and `refresh_all_decision_tables` at step 31).

### Two-phase UX on Badger orgs

On Badger (Manufacturing Cloud) orgs, UX assembly runs twice:

1. **Step 29 — `prepare_ux`** → assembles and deploys `unpackaged/post_ux/` (base + all
   non-manufacturing features). Manufacturing content is **excluded** (`manufacturing=false`)
   because the `SalesAgreement` object, `Order.SalesAgreementId` field,
   `Contract.Create_Sales_Agreement` quick action, and `QuoteProposal` OmniScript do not
   exist until `prepare_badger_flow` runs. Base versions of shared pages (e.g.
   `RLM_Order_Record_Page`) are deployed here as a foundation.

2. **Step 30 → step 19 — `prepare_mfg_ux`** (inside `prepare_badger_flow`) → assembles and
   deploys `unpackaged/post_manufacturing_ux/` using `manufacturing=true`. Because this runs
   **after** `post_ux`, it correctly overrides shared pages (e.g. `RLM_Order_Record_Page`,
   `RLM_Quote_Record_Page`) with their manufacturing variants, and adds manufacturing-only
   pages (`MFG_RLM_*`, `Sales_Agreement_Record_Page`), manufacturing layouts, and the
   manufacturing `RLM_Revenue_Cloud` app variant.

### Problems it solves

| Before | After |
|--------|-------|
| 19+ copies of `RLM_Quote_Record_Page.flexipage-meta.xml` across `post_*` directories, each needing manual sync | One base template + per-feature YAML patch files; assembly is automatic |
| Layouts deployed at step 5 via `deploy_full`, causing Admin profile failures on fresh orgs | Layouts, compact layouts, and list views deployed at step 29 after all objects exist |
| `Admin.profile-meta.xml` deploying stale layout assignments every time `deploy_full` ran | Profile stripped to class-accesses-only at step 5; full profile assembled at step 29 |
| No gate — UX always deployed even during isolated feature testing | `ux: true` feature flag in `cumulusci.yml`; set `ux: false` to bypass entirely |
| Compact layouts and list views in feature `unpackaged/post_*` dirs, not conditionally assembled | Moved to `templates/objects/`; assembled with feature-conditional copy order |

---

## Feature Flag

```yaml
# cumulusci.yml → project.custom
ux: true   # Set false to skip prepare_ux entirely (useful for isolated feature testing)
```

`prepare_ux` runs only when `ux=true`:

```yaml
# prepare_rlm_org step 29
29:
  flow: prepare_ux
  when: project_config.project__custom__ux
```

To skip UX during testing, pass `ux=false` to the flow or set it in your org definition file.

---

## Template Directory Layout

```
templates/
├── flexipages/
│   ├── base/                           # Base flexipages (source of truth for non-manufacturing orgs)
│   │   ├── RLM_Quote_Record_Page.flexipage-meta.xml
│   │   └── ... (others)
│   ├── standalone/                     # Feature-specific pages (new pages or non-additive overrides)
│   │   ├── approvals/                  # RLM_Quote_Discount_Approval_Template, RLM_Quote_Payment_Terms_Approval_Template
│   │   ├── billing/                    # RLM_Invoice_Record_Page (billing-specific override)
│   │   ├── billing_ui/                 # Billing UI overrides
│   │   ├── collections/                # 4 collections flexipages
│   │   ├── constraints/                # RLM_Asset_Action_Source_Record_Page
│   │   ├── docgen/                     # RLM_QuantumBit_Quote (ServiceDocument type)
│   │   ├── manufacturing/              # 7 Manufacturing (Badger) pages — MFG_RLM_Contract/Order/Quote/
│   │   │                               #   Sales_Agreement_Record_Page, RLM_Order/Quote_Record_Page overrides
│   │   │                               #   (included only when manufacturing=true, i.e. prepare_mfg_ux)
│   │   ├── payments/                   # RLM_Account_Record_Page (payments override) + 1 other
│   │   ├── quantumbit/                 # QB-specific pages (billing schedules, usage, etc.)
│   │   ├── tso/                        # TSO-specific overrides
│   │   └── utils/                      # RLM_Home_Page_Default
│   └── patches/                        # YAML patch files for additive/positional changes
│       ├── approvals/
│       │   └── RLM_Quote_Record_Page.yml
│       ├── billing_ui/
│       │   └── RLM_Order_Record_Page.yml
│       ├── docgen/
│       │   └── RLM_Quote_Record_Page.yml
│       ├── manufacturing/              # (empty placeholder — manufacturing pages are standalone, not patched)
│       ├── ramp_builder/
│       │   └── RLM_Quote_Record_Page.yml
│       └── utils/
│           └── RLM_Account_Record_Page.yml
├── layouts/
│   ├── base/                           # Base layouts
│   ├── billing/                        # Billing-specific layouts
│   ├── constraints/                    # Constraints overrides (OrderItem, QuoteLineItem)
│   └── manufacturing/                  # Manufacturing layouts — SalesAgreement-MFG RCA Sales Agreement Layout
│                                       # (included only when manufacturing=true, i.e. prepare_mfg_ux)
├── applications/
│   ├── base/                           # RLM_Revenue_Cloud.app-meta.xml (core/minimal)
│   ├── manufacturing/                  # RLM_Revenue_Cloud Manufacturing variant — includes SalesAgreement
│   │                                   # action overrides and tab (selected when badger=true, manufacturing=true)
│   ├── quantumbit/                     # RLM_Revenue_Cloud QB variant (selected when qb=true)
│   ├── tso/                            # RLM_Revenue_Cloud TSO variant (selected when tso=true)
│   ├── patches/                        # Feature-conditional actionOverride patches
│   │   ├── billing/
│   │   ├── ramps/
│   │   └── rates/
│   └── conditional/
│       ├── billing/                    # standard__BillingConsole (active when billing=true)
│       ├── billing_ui/                 # Billing UI app (active when billing_ui=true)
│       ├── collections/                # CollectionConsole + Receivables Management (active when collections=true)
│       └── manufacturing/              # Manufacturing-specific standalone apps (active when badger=true)
├── appMenus/
│   └── base/                           # App launcher menu (not deployed via Metadata API;
│                                       # ordering is handled at runtime by reorder_app_launcher)
├── objects/
│   ├── base/                           # Compact layouts and list views from force-app
│   │   ├── Asset/
│   │   │   ├── compactLayouts/RLM_Asset_Compact_Layout.compactLayout-meta.xml
│   │   │   └── listViews/All_Assets.listView-meta.xml
│   │   ├── Product2/listViews/All_Products.listView-meta.xml
│   │   └── Quote/compactLayouts/RLM_Quote_Compact_Layout.compactLayout-meta.xml
│   ├── billing/                        # Billing-specific (active when billing=true)
│   │   ├── Account/compactLayouts/RLM_Billing_Account_Compact_Layout.compactLayout-meta.xml
│   │   ├── BillingScheduleGroup/listViews/RLM_All_Billing_Schedule_Groups.listView-meta.xml
│   │   ├── Invoice/listViews/RLM_Failed_Invoices.listView-meta.xml
│   │   └── TransactionJournal/compactLayouts/RLM_Transaction_Journal_Compact_Layout.compactLayout-meta.xml
│   └── collections/                    # Collections (active when collections=true, WIP)
│       ├── Collection_Plan_Activity__c/listViews/All.listView-meta.xml
│       └── CollectionPlan__c/listViews/RLM_All_Collection_Plans.listView-meta.xml
└── profiles/
    ├── base/                           # Full canonical profiles with all layout assignments
    │   ├── Admin.profile-meta.xml
    │   └── RLM Custom Partner Community User.profile-meta.xml
    └── patches/
        ├── billing/Admin.yml           # Adds billing layout assignments (billing=true)
        ├── constraints/Admin.yml       # No-op (layout content changes, names unchanged)
        └── prm/
            └── RLM Custom Partner Community User.yml   # Adds PRM layout assignments (prm=true)
```

---

## Metadata Types and Assembly Logic

### Flexipages

**Source resolution** (last write wins):
1. Base pages from `templates/flexipages/base/`
2. Feature standalone overrides applied in deploy order:
   `payments → billing → billing_ui → quantumbit → tso → constraints → utils → docgen → approvals → collections`
   When `manufacturing=true` (i.e. `prepare_mfg_ux`), `manufacturing` is appended:
   `... → collections → manufacturing`
   *(Canonical order defined in `tasks/rlm_ux_utils._STANDALONE_ORDER`; all three tasks — assembly, retrieve, writeback — use this shared constant)*

**Patch application** (additive, in deploy order):
`quantumbit → utils → billing → billing_ui → payments → approvals → docgen → tso → constraints → ramp_builder → collections`

**Skip rule**: `EmailTemplatePage` type flexipages cannot be deployed via Metadata API
(platform restriction). During assembly, these pages are skipped, each skip is logged as a
warning, and the skipped file is recorded (with reason `non_deployable_metadata`) in
`assembly_manifest.json` so CI logs and reviewers can see that these templates were
intentionally omitted. The approval email template pages
(`RLM_Quote_Discount_Approval_Template`, `RLM_Quote_Payment_Terms_Approval_Template`) are
created at runtime by `create_approval_email_templates`.

#### YAML Patch Format

```yaml
feature: approvals          # Informational label
feature_flag: qb            # Controls whether this patch group is active (checked at CCI level, not in YAML)
patches:
  - type: insert_action
    after: "Quote.RLM_CreateContract"   # Insert after this action value; omit to append
    actions:
      - "Quote.RLM_Submit_for_Approval"

  - type: remove_action
    action: "Quote.RLM_Create_Proposal"  # Remove action before reinserting at new position
    ignore_missing: true                 # Don't fail if not found

  - type: add_display_field
    field: "QuoteLineItem.RLM_Approval__c"   # Adds to the displayedFields component

  - type: add_facet_field
    facet: "Quote Information"           # Label of the target facet region
    after: "Description"                 # Insert after this field; omit to append
    fields:
      - "RLM_Approval_Status__c"
      - "RLM_Payment_Terms__c"

  - type: add_component
    region: "main"
    component: "c:myLWCComponent"
    properties:
      - key: "recordId"
        value: "{!recordId}"
```

**Patch idempotency**: All patch operations deduplicate before inserting. An action or field
that already exists (from a previous patch in the same run, or from the base file) will not
be added again.

### Layouts

**Copy order** (last write wins for the same layout name):
1. `templates/layouts/base/` — always
2. `templates/layouts/billing/` — when `billing=true`
3. `templates/layouts/constraints/` — when `constraints=true` (overrides `OrderItem` and `QuoteLineItem`)
4. `templates/layouts/manufacturing/` — when `badger=true` **and** `manufacturing=true` (i.e. `prepare_mfg_ux` only)
   Adds `SalesAgreement-MFG RCA Sales Agreement Layout`. Not included in `prepare_ux` because the
   `SalesAgreement` object does not exist until `prepare_badger_flow` has run.

No patching — layouts are copied as-is.

**Spring '26 note**: `AssetStatePeriod-RLM Asset State Period Layout` requires four new fields
(`SegmentName`, `SegmentType`, `RampIdentifier`, `SegmentIdentifier`) as of API v66.

### Applications

**Versioned selection** for `RLM_Revenue_Cloud.app-meta.xml` (highest-priority active flag wins):
- `tso=true` → `templates/applications/tso/`
- `badger=true` **and** `manufacturing=true` → `templates/applications/manufacturing/`
  (includes `SalesAgreement` action overrides and tab; only selected in `prepare_mfg_ux`)
- `qb=true` → `templates/applications/quantumbit/`
- fallback → `templates/applications/base/`

**Conditional standalone apps** (copied when their flag is active):
- `standard__BillingConsole` — when `billing=true`
- `standard__CollectionConsole`, `RLM_Receivables_Management` — when `collections=true`

### Profiles

**Strip-and-build approach**:
- Early-stage profiles in `force-app/main/default/profiles/` and `unpackaged/post_*/profiles/`
  are **stripped** of `layoutAssignment` and `applicationVisibilities` elements. They deploy
  at step 5 with only `classAccesses` (and other non-personalization grants).
- At step 29, `_assemble_profiles` reads the **base template** (full layout assignments +
  app visibility) from `templates/profiles/base/` and applies feature patches:

| Patch file | Activates when | Effect |
|---|---|---|
| `patches/billing/Admin.yml` | `billing=true` | Adds `GeneralLedgerAccount`, `InvoiceLine`, `UsageResource` layout assignments |
| `patches/constraints/Admin.yml` | `constraints=true` | No-op (layout names unchanged; only content differs) |
| `patches/prm/RLM Custom Partner Community User.yml` | `prm=true` | Adds 12 PRM object layout assignments |

### Compact Layouts and List Views (`objects`)

Simple feature-conditional copy from `templates/objects/{feature}/` into
`post_ux/objects/{ObjectName}/{subtype}/`. No patching.

Copy order: `base` (always) → `billing` → `tso` → `collections`

> **Collections note**: The `CollectionPlan__c` list view path (`objects/listViews/`) in the
> original `unpackaged/post_collections/` was missing the object name directory and has been
> moved to `templates/objects/collections/CollectionPlan__c/listViews/` pending verification
> of the correct object API name.

---

## CCI Task Reference

### `assemble_and_deploy_ux`

```
cci task run assemble_and_deploy_ux [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `-o metadata_type` | `all` | `all`, `flexipages`, `layouts`, `applications`, `profiles`, `objects` |
| `-o metadata_name` | (none) | Full source filename to generate one item, e.g. `RLM_Quote_Record_Page.flexipage-meta.xml`. Type is inferred from suffix. |
| `-o deploy` | `true` | Set `false` to assemble without deploying (inspect output directory) |
| `-o output_path` | `unpackaged/post_ux` | Override output directory |
| `-o manufacturing` | `false` | Include manufacturing standalone flexipages, manufacturing layouts, and the manufacturing `RLM_Revenue_Cloud` app variant. Set to `true` only via `prepare_mfg_ux` — these resources require the `SalesAgreement` object and other manufacturing metadata to already be deployed. |

**Examples:**

```bash
# Assemble and deploy everything (production use via prepare_ux flow)
cci task run assemble_and_deploy_ux --org dev-sb0

# Dry-run: assemble only, no deploy
cci task run assemble_and_deploy_ux -o deploy false --org dev-sb0

# Regenerate a single flexipage
cci task run assemble_and_deploy_ux \
    -o metadata_name RLM_Quote_Record_Page.flexipage-meta.xml \
    --org dev-sb0

# Regenerate and inspect a profile without deploying
cci task run assemble_and_deploy_ux \
    -o metadata_name Admin.profile-meta.xml \
    -o deploy false --org dev-sb0

# Assemble only layouts
cci task run assemble_and_deploy_ux \
    -o metadata_type layouts -o deploy false --org dev-sb0

# Assemble manufacturing UX (dry-run) — requires manufacturing metadata to be deployed first
cci task run assemble_and_deploy_ux \
    -o output_path unpackaged/post_manufacturing_ux \
    -o manufacturing true \
    -o deploy false --org dev-sb0
```

### `prepare_ux` flow

```bash
cci flow run prepare_ux --org dev-sb0
```

Two-step flow: runs `assemble_and_deploy_ux` (full assembly + deploy, `manufacturing=false`)
then `reorder_app_launcher`. Runs as **step 29** of `prepare_rlm_org` when `ux=true`.
Deliberately excludes manufacturing content even on Badger orgs — manufacturing UX is
deployed separately by `prepare_mfg_ux` after all manufacturing metadata exists.

### `prepare_mfg_ux` flow

```bash
cci flow run prepare_mfg_ux --org dev-sb0
```

Assembles and deploys manufacturing UX metadata to `unpackaged/post_manufacturing_ux/`
with `manufacturing=true`. Runs as **step 19 of `prepare_badger_flow`** (step 30 of
`prepare_rlm_org`), after all manufacturing metadata (`SalesAgreement` object, layouts,
quick actions, OmniScripts) is in place.

Can be run independently to iterate on manufacturing UX changes without running the full
`prepare_rlm_org` flow, provided manufacturing metadata is already deployed.

---

## Drift Capture and Writeback

When UX changes are made directly in the org (e.g. rearranging components on a
Lightning page), the templates need to be updated to match. The drift capture and
writeback workflow automates this.

### Workflow

```
1. capture_ux_drift  — retrieve org state, diff against templates
2. (review drift_report.json)
3. apply_ux_drift    — writeback to templates, re-assemble, verify zero drift
```

### `capture_ux_drift` flow

```bash
cci flow run capture_ux_drift --org dev-sb0
```

Steps:
1. `retrieve_ux_from_org` — retrieves live flexipages from the org into `unpackaged/post_ux/`
2. `diff_ux_templates` — compares retrieved state against assembled output, writes `drift_report.json`

### `apply_ux_drift` flow

```bash
cci flow run apply_ux_drift --org dev-sb0
```

Steps:
1. `writeback_ux_templates` (dry_run=false) — reverse-applies patches to compute new base templates
2. `assemble_and_deploy_ux` (deploy=false) — re-assembles from updated templates
3. `diff_ux_templates` — verifies zero drift between assembled output and org state

### `writeback_ux_templates` task

```bash
# Dry-run (default) — shows what would change without modifying templates
cci task run writeback_ux_templates --org dev-sb0

# Execute writeback
cci task run writeback_ux_templates -o dry_run false --org dev-sb0

# Single page
cci task run writeback_ux_templates \
    -o metadata_name RLM_Order_Record_Page.flexipage-meta.xml \
    -o dry_run false --org dev-sb0
```

| Option | Default | Description |
|--------|---------|-------------|
| `-o dry_run` | `true` | Set `false` to actually write back templates |
| `-o metadata_name` | (none) | Process a single file |
| `-o metadata_type` | `all` | `all`, `flexipages`, or `layouts` |

### Writeback Algorithm

The assembler invariant is: `base + patches = deployed state`.
Writeback computes: `new_base = org_state - reverse(patches)`.

For flexipages with active patches:
1. Parse org-retrieved XML from `unpackaged/post_ux/`
2. Reverse-apply each patch operation (remove inserted actions, fields, components,
   and `insert_after_xml` content)
3. Write the result as the new base template
4. Extract updated patch content from the org state and update YAML patch files

For standalone flexipages (no patches): copy org file directly to the standalone
template directory.

For layouts: resolve tier ownership (base → billing → constraints, last-wins) and
copy the org file to the correct template directory.

Profile writeback is not automated — profile changes require manual review and
are applied with oversight.

### Patch YAML Auto-Update

During writeback, the task also updates YAML patch files to reflect the current
org state. For `insert_after_xml` patches, it uses a sync marker algorithm to
locate where base content resumes after inserted patch content, then extracts
the current patch XML from the org. Patches whose content no longer exists in
the org are removed from the YAML file.

### XML Serialization

The assembler preserves `&quot;` entity encoding in `<value>` elements that
contain HTML (`&lt;`) or JSON (`[{`, `{"`). For unpatched flexipages (no active
patches), the assembler bypasses ElementTree entirely and uses a direct file
copy to avoid any serialization artifacts.

---

## Output: `unpackaged/post_ux/`

This directory is **git-tracked** by design. Committing the assembled output:
- Makes UX changes reviewable in PRs
- Allows debugging discrepancies between expected and actual assembly
- Provides a reproducible artifact for org comparison

The directory is fully regenerated on every task run (all type subdirectories are cleaned
before assembly). Do not hand-edit files here; edit the templates instead.

```
unpackaged/post_ux/
├── assembly_manifest.json     # Assembly run metadata: timestamp, flags, all items
├── drift_report.json          # Drift analysis output (git-ignored)
├── flexipages/                # ~53 assembled flexipages (EmailTemplatePage types excluded)
├── layouts/                   # 19 assembled layouts (17 base + 2–3 feature variants)
├── applications/              # 1–3 app files depending on active features
├── objects/                   # compactLayouts + listViews organized by object
└── profiles/                  # 2 assembled profiles
```

### assembly_manifest.json

Written on every run. Contains:
- `assembled_at`: ISO 8601 UTC timestamp
- `feature_flags`: snapshot of all custom project flags at assembly time
- `assembled`: list of all items with `type`, `name`, `dest`, `source`/`patches`

---

## `.forceignore` Entries

The following paths are excluded from feature-package deploys. The files are preserved for
reference but are deployed exclusively via `prepare_ux`:

```
# Flexipages
unpackaged/post_billing/flexipages
unpackaged/post_constraints/flexipages
unpackaged/post_payments/flexipages
unpackaged/post_utils/flexipages
unpackaged/post_ramp_builder/flexipages
unpackaged/post_tso/flexipages
unpackaged/post_docgen/flexipages
unpackaged/post_quantumbit/flexipages
unpackaged/post_collections/flexipages

# Layouts
unpackaged/post_billing/layouts
unpackaged/post_constraints/layouts

# Applications
unpackaged/post_billing/applications
unpackaged/post_tso/applications
unpackaged/post_quantumbit/applications
unpackaged/post_collections/applications

# Profiles
unpackaged/post_quantumbit/profiles

# Compact layouts and list views (moved to templates/objects/)
unpackaged/post_billing/objects/Account/compactLayouts
unpackaged/post_billing/objects/TransactionJournal/compactLayouts
unpackaged/post_billing/objects/BillingScheduleGroup
unpackaged/post_billing/objects/Invoice/listViews
unpackaged/post_collections/objects/Collection_Plan_Activity__c/listViews
unpackaged/post_collections/objects/listViews
```

---

## Known Limitations and TODOs

### EmailTemplatePage flexipages

`RLM_Quote_Discount_Approval_Template` and `RLM_Quote_Payment_Terms_Approval_Template` are
`EmailTemplatePage` type and **cannot be deployed via Metadata API**. The assembly task
detects this type and silently skips them. These pages are created at runtime by
`create_approval_email_templates` via SFDMU + REST API.

### Collections objects path

`RLM_All_Collection_Plans.listView-meta.xml` was stored in `post_collections/objects/listViews/`
(missing the object name directory). It has been moved to
`templates/objects/collections/CollectionPlan__c/listViews/`. The correct object API name
must be verified and the file path corrected before `collections=true` deployments.

### tso=true not yet validated

The `tso` flexipage standalone overrides and `RLM_Revenue_Cloud` TSO application variant have
been moved to `templates/` but have not yet been tested in a live TSO org. See the test plan
below.

---

## Test Plan

### Phase 1 — Baseline (tso=false) ✅ Completed

| Test | Org | Result |
|------|-----|--------|
| `assemble_and_deploy_ux -o deploy false` (dry run, all types) | dev-sb0 | 71 items assembled; EmailTemplatePage pages correctly skipped |
| `assemble_and_deploy_ux` (full deploy) | dev-sb0 | 69 components deployed; `status=Succeeded` |
| Single-item generation: `RLM_Quote_Record_Page.flexipage-meta.xml` | dev-sb0 | 14 patches applied; action order matches `post_ramp_builder` reference |
| PRM profile patches (12 layout assignments) | dev-sb0 | Confirmed via assembly log |

**Active flags during Phase 1:**
`qb, billing, tax, rating, rates, clm, dro, ramps, prm, docgen, payments, constraints, analytics, procedureplans`

---

### Phase 2 — ux=false gate test

Verify that setting `ux=false` completely skips `prepare_ux` with no side effects:

1. In org definition or flow invocation, set `ux=false`
2. Run `prepare_rlm_org` (or just `prepare_ux` directly)
3. **Expected**: `prepare_ux` step is skipped; no UX metadata deployed; org functional
4. Confirm `unpackaged/post_ux/` is unchanged after the run

---

### Phase 3 — tso=true test (pending)

TSO introduces:
- `RLM_Revenue_Cloud.app-meta.xml` from `templates/applications/tso/` (different tab set,
  custom branding)
- 6 standalone TSO flexipage overrides from `templates/flexipages/standalone/tso/`
- TSO-specific profile app visibility differences
- App Launcher ordering handled dynamically by `reorder_app_launcher` (no static appMenu)

**Test steps:**

1. Prepare a TSO-capable org (or set `tso=true` in the org definition)
2. Run dry-run to inspect output:
   ```bash
   cci task run assemble_and_deploy_ux -o deploy false --org <tso-org>
   ```
3. Verify:
   - `unpackaged/post_ux/applications/RLM_Revenue_Cloud.app-meta.xml` comes from
     `templates/applications/tso/` (not quantumbit variant)
   - All 6 TSO flexipage variants are selected over their quantumbit counterparts
   - Assembly manifest shows `tso: true` in `feature_flags`
4. Deploy and verify in the org UI:
   - TSO-specific Lightning pages load without component errors
   - All record pages function correctly with TSO field/component additions

**TSO flexipages to validate** (from `templates/flexipages/standalone/tso/`):
Review each against the previous `unpackaged/post_tso/flexipages/` reference to ensure
content parity.

---

### Phase 4 — Full `prepare_rlm_org` regression

After Phases 2 and 3 pass independently:

1. Run `cci flow run prepare_rlm_org --org <fresh-org>` end-to-end
2. Confirm all UX deploys succeed at step 29
3. Spot-check record pages in the org UI:
   - Quote Record Page: all actions present in correct order
   - Profile layout assignments: Admin profile can open all expected record pages
   - PRM profile: Partner Community User can access PRM objects
4. Run `cci task run assemble_and_deploy_ux` a second time (idempotency check): should
   succeed with same deployed count

---

## Debugging

### Inspect the assembled output before deploying

```bash
cci task run assemble_and_deploy_ux -o deploy false --org dev-sb0
```
Review `unpackaged/post_ux/` and `unpackaged/post_ux/assembly_manifest.json`.

### Regenerate a single item

```bash
# Single flexipage (also deploys it)
cci task run assemble_and_deploy_ux \
    -o metadata_name RLM_Quote_Record_Page.flexipage-meta.xml \
    --org dev-sb0

# Single layout, no deploy
cci task run assemble_and_deploy_ux \
    -o metadata_name "Quote-RLM Quote Layout.layout-meta.xml" \
    -o deploy false --org dev-sb0
```

### Check what feature flags were active for a past assembly

```bash
cat unpackaged/post_ux/assembly_manifest.json | python3 -m json.tool | grep -A 20 '"feature_flags"'
```

### Source tracking conflicts

If `sf project deploy start` fails with `SourceConflictError`, clear the local tracking:
```bash
# Find the org ID
sf org display --target-org <alias> --json | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['result']['id'])"
# Delete tracking index
rm -rf .sf/orgs/<org-id>/localSourceTracking
```

### Capture and apply org drift

```bash
# Step 1: Capture drift (retrieve + diff)
cci flow run capture_ux_drift --org dev-sb0

# Step 2: Review the drift report
cat unpackaged/post_ux/drift_report.json | python3 -m json.tool

# Step 3: Apply drift to templates (writeback + reassemble + verify)
cci flow run apply_ux_drift --org dev-sb0

# Step 4: Verify zero drift
# The apply_ux_drift flow re-runs diff_ux_templates as its final step.
# If the drift report shows no differences, the writeback succeeded.
```

### Adding a new patch type or flexipage

1. Add or edit the YAML patch file in `templates/flexipages/patches/{feature}/`
2. Run `cci task run assemble_and_deploy_ux -o metadata_name <pagename>.flexipage-meta.xml -o deploy false --org <org>`
3. Inspect the output file and compare to the reference in `unpackaged/post_*/flexipages/`
4. When satisfied, run without `-o deploy false` to deploy
