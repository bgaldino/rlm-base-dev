# Customer Demo DRO — Design & Onboarding Guide

Dynamic Revenue Orchestration (DRO) closes the loop between CPQ/quoting and post-sale execution. It is the answer to: **"What actually happens after the order is placed?"**

This document covers:
- What DRO does and why it matters
- When to include DRO in a customer demo (and when not to)
- Business model playbook — what DRO looks like for different verticals
- How it integrates into the `prepare_customer_demo_catalog` flow
- How to implement it step by step for a new customer

---

## What DRO Does

DRO is a three-layer engine:

### Layer 1 — Product Decomposition

A sales order line references a *sellable* product (e.g. `MCC-MBR-IND` — Individual Golf Membership). That commercial product does not map 1:1 to what operations does. `ProductFulfillmentDecompRule` (PFDR) rewrites it into *operational* sub-products:

- `MCC-MBR-IND` → `QB-DRO-BILL` (route to Finance team for invoicing)
- `MCC-GOLF-ACADEMY` → `QB-DRO-BILL` (Finance) + `QB-DRO-PROJ` (Services delivery)

This decomposition is invisible to the buyer — they ordered one thing; the back-office receives routed work items automatically.

### Layer 2 — Fulfillment Step Orchestration

`FulfillmentStepDefinition` defines process steps (Validate Order, Convert Order to Asset, Initiate Billing, Post Invoice, Provision Platform, etc.). These are grouped into phases (`FulfillmentStepDefinitionGroup`): Order Processing, Finance, Billing and Invoicing, Services, License Activation, Platform Provisioning, etc.

`FulfillmentStepDependencyDef` wires the graph — step B cannot start until step A is complete. The platform enforces sequencing at runtime.

`ProductFulfillmentScenario` (PFS) maps a specific *sellable product* to a specific step group + lifecycle action (Add, Amend, Renew, No Change, Cancel). One product can have multiple PFS rows:
- `MCC-MBR-IND` + Order Processing + Add = validate the order first
- `MCC-MBR-IND` + Finance + Add;Amend;Renew;Cancel = billing steps fire on every lifecycle event

### Layer 3 — Monitoring and Exception Handling

- **`FulfillmentStepJeopardyRule`** — SLA tracking. If a step exceeds its jeopardy threshold, it's flagged. Example: a ManualTask expected in 1 day is jeopardized at 20 hours.
- **`FulfillmentFalloutRule`** — retry and error handling. When a Callout or AutoTask fails, it defines retry count and policy.
- **`FulfillmentWorkspace`** — the UI where assigned users see their open steps, organized by step group.

### What It Demonstrates to Buyers

DRO creates a *living proof* that the platform handles the entire revenue lifecycle, not just the quote. Key demo moments:

1. **Order → Asset**: placing an order automatically triggers order processing and asset conversion — no manual handoff
2. **Billing initiation**: invoicing steps fire automatically on Add, and re-fire on Amend/Renew
3. **Mid-term change visibility**: amending a membership subscription triggers a distinct fulfillment plan, showing the platform tracks what changed and routes accordingly
4. **SLA accountability**: jeopardy alerts surface delayed steps in the workspace
5. **Exception recovery**: fallout rules show how the system handles integration failures with automatic retry

---

## When to Include DRO in a Customer Demo

### Include DRO when:

| Signal | Reason |
|---|---|
| Buyer has a post-sale operations or delivery team | They will recognize the fulfillment workspace and want to see what their team would work on |
| The deal involves subscriptions (annual/monthly recurring) | Amend/Renew lifecycle routing is where DRO shines most — shows that mid-term changes don't require manual re-routing |
| The vertical involves provisioning, onboarding, or service delivery | Decomposition from commercial → operational products maps directly to their reality |
| Buyer asks "how does this connect to our back-office?" | DRO is the direct answer |
| The org already has `dro: true` (QB DRO plan loaded) | Infrastructure cost is near zero — only customer-specific routing rules need to be added |
| The demo needs to show the full order-to-cash loop | DRO + billing together close the loop from quote to invoice |

### Do NOT include DRO when:

| Signal | Reason |
|---|---|
| The org does NOT have `dro: true` set and the QB DRO plan has not run | `prepare_dro` is a prerequisite — the fulfillment step groups, workspaces, and jeopardy rules that the customer DRO plan depends on come from `qb-dro`. Without them, the SFDMU load will fail on FK resolution for `ProductFulfillmentScenario`. |
| The demo is focused purely on CPQ / quoting | Adding DRO steps mid-demo shifts focus. If the buyer hasn't asked about fulfillment, save it for a follow-up. |
| Products are entirely one-time, no recurring motions | DRO's Amend/Renew routing story is lost on one-time-only catalogs. Basic Order Processing and Finance routing is still possible but the ROI of adding DRO is lower. |
| The org is a lightweight sandbox without the full RLM permission set stack | DRO requires `RLM_DRO` permission set assigned to the demo user. Verify before loading. |
| Time is the constraint and catalog/billing are not yet verified | Always run `customer_demo_verify_catalog` cleanly before adding DRO. DRO failures are harder to debug than PCM failures. |
| You are building a net-new customer template from scratch | Get PCM, billing, pricebook, and pricing loaded and verified first. DRO is step 11+ in the flow. |

---

## Business Model Playbook

### SaaS / Subscription Software

**DRO value:** Highest. The full decomposition story — commercial SKU to license activation + billing + provisioning — is native to SaaS. The QB DRO plan is already built for this model.

**Decomposition pattern:**
- Sellable platform product → Finance (billing initiation) + License Activation (key generation) + Platform Provisioning (tenant setup)
- Add-on feature products → Feature/License Provisioning + Activation
- Professional services → Services (project creation + resource assignment)

**PFS actions:** All five — Add;Amend;Renew;No Change;Cancel. Amend is critical (upgrades, seat expansion).

**Step groups to highlight:** Order Processing (validation), Finance (billing), License Activation, Platform Provisioning, Feature/License Provisioning + Activation

**PFDR destination products:** `QB-DRO-BILL`, `QB-DRO-QBD` (database/platform), `QB-DRO-PROJ` (services)

---

### Membership / Club / Association

**DRO value:** High. Annual memberships renew, have tiers, and involve both billing and back-office onboarding (access provisioning, welcome kits, facility access setup). The "Convert Order to Asset" step is compelling — it shows that a sold membership becomes a tracked entitlement automatically.

**Decomposition pattern:**
- Annual membership → Finance (billing initiation)
- Bundle membership → Finance (for the bundle as a whole)
- Amenity passes (racquet, gun club) → Finance
- Professional instruction packages (golf academy) → Finance + Services
- One-time events → Finance (Add only)
- Initiation fees → Finance (Add only)

**PFS actions:**
- Recurring tiers: Add;Amend;Renew;No Change;Cancel
- One-time items: Add only
- Services: Add;Amend (rescheduled sessions)

**Step groups to highlight:** Order Processing (new member validation), Finance (invoice routing), Services (instructor assignment for academy/events)

**PFDR destination products:** `QB-DRO-BILL`, `QB-DRO-PROJ`

**Rename step groups in the demo narrative:** "Order Processing" → "Member Enrollment Validation", "Finance" → "Billing & Dues Routing", "Services" → "Service Delivery". The step group names in the data stay generic; the narrative labels them.

---

### Manufacturing / Hardware / Equipment

**DRO value:** Medium-high. Physical product fulfillment has the most natural mapping to step-based orchestration — order validation, shipping, installation, billing. The "Convert Order to Asset" step is the most valuable: it shows that a delivered unit becomes a tracked asset for warranty and service.

**Decomposition pattern:**
- Hardware unit → Finance (billing) + Platform Provisioning (shipping/logistics proxy)
- Services/installation → Services
- Support contracts → Finance + License Activation (contract activation)

**PFS actions:** Add (primary) + Amend (for order modifications, upgrades) + Cancel

**Step groups to highlight:** Order Processing (order validation), Finance (billing), Asset Conversion (the order becomes an asset record)

**PFDR destination products:** `QB-DRO-BILL`, `QB-DRO-PROJ`, `QB-DRO-APIPLAT` (logistics proxy)

---

### Financial Services / Insurance

**DRO value:** High for compliance-conscious buyers. Step-based fulfillment with defined SLAs and jeopardy alerting maps directly to regulated processes (underwriting, KYC, policy issuance). The fallout rules (retry logic) map to integration failure handling between Salesforce and policy admin systems.

**Decomposition pattern:**
- Policy/product sold → Finance (premium billing) + License Activation (policy issuance proxy)
- Advisory engagement → Finance + Services

**PFS actions:** Add;Amend;Renew;Cancel

**Step groups to highlight:** Finance, License Activation (policy issuance), Jeopardy alerting (SLA compliance)

**PFDR destination products:** `QB-DRO-BILL`, `QB-DRO-QBD` (policy admin proxy)

---

### Professional Services / Consulting

**DRO value:** High. Service project creation and resource assignment are the core of the delivery model. The Services step group (`Create Project` → `Assign Resources` → `Start Project`) maps directly to their PM workflow.

**Decomposition pattern:**
- Statement of Work → Finance + Services
- Time-and-material engagements → Finance + Services
- Fixed-fee deliverables → Finance only

**PFS actions:** Add;Amend;No Change;Cancel (Renew rarely applies)

**Step groups to highlight:** Order Processing, Finance, Services (Create Project, Assign Resources, Start Project)

**PFDR destination products:** `QB-DRO-BILL`, `QB-DRO-PROJ`

---

### Usage-Metered / Telco / Platform

**DRO value:** Medium. DRO orchestrates the post-order setup (activate the usage plan, link the billing policy); metering and rating happen outside DRO (in the rating/rates plans). The most valuable DRO moment is showing usage product activation after the order is placed.

**Decomposition pattern:**
- Sellable usage pack → Finance (billing) + License Activation (usage plan activation proxy)

**PFS actions:** Add;Renew;Cancel

**Step groups to highlight:** Finance, License Activation (activating the usage meter)

**PFDR destination products:** `QB-DRO-BILL`, `QB-DRO-AEH` (usage/feature activation proxy)

---

## Data Model — What You're Populating

```
Product2 (Update: DecompositionScope, FulfillmentQtyCalcMethod)
  │
  └─ ProductFulfillmentDecompRule (PFDR)
       SourceProduct → DestinationProduct
       (customer sellable SKU → QB DRO routing product)
  │
  └─ ProductFulfillmentScenario (PFS)
       Product → FulfillmentStepDefinitionGroup
       (customer sellable SKU → which step group fires, and on which actions)

[QB DRO infrastructure already in org — DO NOT recreate in customer template]
FulfillmentStepDefinitionGroup (10 groups: Order Processing, Finance, Services, ...)
FulfillmentStepDefinition (17 steps with dependencies)
FulfillmentStepDependencyDef (13 dependency links)
FulfillmentWorkspace + FulfillmentWorkspaceItem
FulfillmentFalloutRule + FulfillmentStepJeopardyRule
```

The customer DRO plan only adds **PFDR** and **PFS** rows and updates **Product2.DecompositionScope**. All step group infrastructure is inherited from `qb-dro`. This keeps the plan small and prevents duplication.

---

## Prerequisite Checklist

Before running `insert_customer_demo_dro_data`:

- [ ] `prepare_dro` has run on this org (`dro: true` and `qb: true` must have been set)
- [ ] `FulfillmentStepDefinitionGroup` records exist (verify: `sf data query -q "SELECT Name FROM FulfillmentStepDefinitionGroup" --target-org <alias>`)
- [ ] `prepare_customer_demo_catalog` steps 1–10 have completed successfully (products exist and verify passes)
- [ ] `RLM_DRO` permission set is assigned to the demo user
- [ ] Target org user has been resolved by the dynamic user mechanism (the `__DRO_ASSIGNED_TO_USER__` in `User.csv` / `UserAndGroup.csv` is automatically replaced at load time by `dynamic_assigned_to_user: true`)

---

## Step-by-Step Implementation for a New Customer

### Step 1 — Set `Product2.DecompositionScope`

In `customer-template-dro/Product2.csv`, add one row per sellable SKU that will have a decomposition rule:

| Column | Value |
|---|---|
| `StockKeepingUnit` | The customer SKU (e.g. `MCC-MBR-IND`) |
| `Name` | The product name (must match exactly) |
| `DecompositionScope` | `OrderLineItem` for individual products; `Bundle` for bundle parent SKUs |
| `CustomDecompositionScope` | Leave blank (for future custom scoping) |
| `FulfillmentQtyCalcMethod` | Leave blank (defaults to system behavior) |

**Rules:**
- Do NOT include routing/delivery products (QB-DRO-*) — those already have DecompositionScope set by the QB DRO plan
- Bundle parent products (`Type=Bundle`): use `Bundle` scope
- All other sellable products: use `OrderLineItem`
- Products with NO decomposition rules: omit from this CSV (no Update needed)

### Step 2 — Create `ProductFulfillmentDecompRule` Rows

One row per source → destination routing pair. Each row routes a customer sellable SKU to a QB-DRO-* operational product.

| Column | Value |
|---|---|
| `Name` | Unique, human-readable: `<CustomerPrefix> <ProductName> to <Function>` (e.g. `MCC Individual Membership to Finance`) |
| `SourceProduct.StockKeepingUnit` | Customer sellable SKU |
| `DestinationProduct.StockKeepingUnit` | QB routing product (see table below) |
| `Priority` | Leave blank for default |
| `SourceIdentifier` / `SourceClassIdentifier` | Leave blank (only needed for classification-based decomp) |

**QB DRO routing products (reuse from existing QB plan):**

| Product SKU | Name | Use When |
|---|---|---|
| `QB-DRO-BILL` | Finance Service | Any product that generates a billing transaction (most products) |
| `QB-DRO-PROJ` | Project Service | Products with associated service delivery (professional services, training, academy sessions) |
| `QB-DRO-QBD` | QB Database to Provisioning | Software/platform products needing provisioning activation |
| `QB-DRO-AEH` | AEH API to Provisioning | API/feature products needing feature activation |
| `QB-DRO-APIPLAT` | API Platform to Provisioning | Platform infrastructure products |

For most non-SaaS customer demos, you will only need `QB-DRO-BILL` (billing) and `QB-DRO-PROJ` (services).

### Step 3 — Create `ProductFulfillmentScenario` Rows

One row per product × step group combination. This maps the customer SKU to the fulfillment workflow that fires when an order lifecycle event occurs.

| Column | Value |
|---|---|
| `Name` | Unique: `<CustomerPrefix> <ProductName> - <StepGroupName>` |
| `Product.StockKeepingUnit` | Customer sellable SKU |
| `FulfillmentStepDefnGroup.Name` | Step group name (must match exactly — from `FulfillmentStepDefinitionGroup.Name` in org) |
| `Action` | Semicolon-separated lifecycle triggers: `Add`, `Amend`, `Renew`, `No Change`, `Cancel` |
| `Type` | Leave blank |
| `FulfillmentProcess.Name` | Leave blank |

**Action selection by product type:**

| Product Type | Actions |
|---|---|
| Recurring subscription (annual, monthly) | `Add;Amend;Renew;No Change;Cancel` |
| One-time purchase | `Add` |
| Professional service with deliverable | `Add;Amend` (re-schedule/re-scope) |
| Bundle (parent) | `Add;Amend;Renew;No Change;Cancel` |

**Step group selection by function:**

| Step Group | Use For |
|---|---|
| `Order Processing` | All "new" orders (Add action) — shows order validation step |
| `Finance` | Any product generating an invoice — billing and payment steps |
| `Services` | Products with associated delivery work (projects, instruction) |
| `License Activation` | Software/digital products where entitlement is activated post-order |
| `Platform Provisioning` | SaaS products where a tenant/instance is provisioned |

**Pattern for a typical recurring membership:**
```
Row 1: <SKU> + Order Processing + Add
Row 2: <SKU> + Finance          + Add;Amend;Renew;No Change;Cancel
```

### Step 4 — Wire the `export.json`

The plan uses **two objectSets** to ensure FK resolution works after a delete+reinsert cycle:

**Set 1** — Readonly parents for FK map, then Upsert PFDR and PFS:
- `Product2` (Readonly — queries ALL products from org, gives SFDMU the full StockKeepingUnit → Id map including QB-DRO-* destinations)
- `FulfillmentStepDefinitionGroup` (Readonly — queries all groups for PFS FK resolution)
- `ProductFulfillmentDecompRule` (Upsert, externalId: `Name`)
- `ProductFulfillmentScenario` (Upsert, externalId: `Name`)

**Set 2** — Update Product2 DecompositionScope:
- `Product2` (Update, externalId: `StockKeepingUnit` — only customer SKUs in CSV)

**Why two sets?** PFDR and PFS both need Product2 FKs resolved. When the customer DRO delete script wipes PFDR and PFS before re-inserting, SFDMU's internal FK cache is empty. By listing Product2 and FSDG as Readonly in Set 1, SFDMU queries the TARGET org during STAGE 2 before processing PFDR/PFS, building a complete ID map from live org data.

**Why Product2 Update is in Set 2?** You cannot have two Product2 entries in the same objectSet. Separating Update (writes DecompositionScope) from Readonly (builds FK map) into separate sets avoids this collision.

### Step 5 — Add the Apex Delete Script

Create `scripts/apex/deleteCustomerDemoDROData.apex` with a name-scoped delete:

1. Delete `ProductFulfillmentScenario WHERE Name LIKE '<PREFIX>%'` — standalone delete, no cascade
2. Delete `ProductFulfillmentDecompRule WHERE Name LIKE '<PREFIX>%'` — standalone delete, no cascade
3. Do NOT reset `Product2.DecompositionScope` — leave it set; the Update in the SFDMU plan will overwrite on re-run

**Why scoped?** QB's PFDR and PFS records exist in the same org. Scoping to customer name prefix ensures QB data is unaffected.

**Why no cascade?** Unlike `AttributeAdjustmentCondition` (master-detail cascade from `AttributeBasedAdjRule`), PFDR and PFS are independent records — both can be deleted directly via DML.

### Step 6 — Wire CCI Tasks and Flow

Add to `cumulusci.yml`:

1. **Dataset anchor** in `project.custom`:
   ```yaml
   customer_demo_dro_dataset: &customer_demo_dro_dataset "datasets/sfdmu/customer-template/en-US/customer-template-dro"
   ```

2. **Tasks**:
   - `delete_customer_demo_dro_data` — runs `deleteCustomerDemoDROData.apex`
   - `insert_customer_demo_dro_data` — runs SFDMU plan with `dynamic_assigned_to_user: true`
   - `update_customer_demo_fulfillment_decomp_rules` — runs `updateProductFulfillmentDecompRules.apex` (re-save all PFDR records to trigger 260 `ExecuteOnRuleId` bug workaround)

3. **Flow steps** at the end of `prepare_customer_demo_catalog`, gated by `customer_demo_dro: true`:
   - Step N: `delete_customer_demo_dro_data`
   - Step N+1: `insert_customer_demo_dro_data`
   - Step N+2: `update_customer_demo_fulfillment_decomp_rules`

4. **Standalone flow** `prepare_customer_demo_dro` (mirrors `prepare_customer_demo_usage` pattern):
   ```yaml
   prepare_customer_demo_dro:
     steps:
       1: delete_customer_demo_dro_data
       2: insert_customer_demo_dro_data
       3: update_customer_demo_fulfillment_decomp_rules
   ```

---

## Known Constraints and Gotchas

### 260 Bug — `ExecuteOnRuleId` Not Set on INSERT

`ProductFulfillmentDecompRule` (and `ProductFulfillmentScenario`, `FulfillmentStepDefinition`) do not generate `ExecuteOnRuleId` (the ruleset reference) when created via INSERT. The field is only populated on UPDATE. Without it, decomposition fires but the orchestration plan may not pick it up correctly.

**Fix:** `update_customer_demo_fulfillment_decomp_rules` runs `updateProductFulfillmentDecompRules.apex` which does `update [SELECT Id FROM ProductFulfillmentDecompRule]` — re-saving all PFDR records triggers ruleset generation. This task runs as step N+2 in the flow automatically.

### Dynamic User Resolution

`FulfillmentStepDefinition` records have an `AssignedToId` pointing to a user. The QB DRO plan uses `__DRO_ASSIGNED_TO_USER__` as a placeholder, resolved at load time via `dynamic_assigned_to_user: true`. The customer DRO plan does NOT re-load `FulfillmentStepDefinition` — those records already exist from `prepare_dro`. No dynamic user resolution is needed in the customer DRO SFDMU plan.

The `User.csv` and `UserAndGroup.csv` files in the customer template are present only as empty Readonly references for SFDMU structural completeness. They do not need populated rows.

### PFDR `Name` Must Be Unique Across All Customers

`ProductFulfillmentDecompRule.Name` is not schema-enforced unique, but the SFDMU externalId is `Name`. If two customer PFDR records have the same Name (e.g. both use `Membership to Finance`), the second upsert will overwrite the first. Always prefix rule names with the customer code: `MCC Individual Membership to Finance`.

### QB Step Groups Must Already Exist

`ProductFulfillmentScenario.FulfillmentStepDefnGroup.Name` must match an existing `FulfillmentStepDefinitionGroup.Name` exactly. If the QB DRO plan has not run, these records don't exist and PFS inserts fail with missing-parent errors in `MissingParentRecordsReport.csv`.

Available step group names (from `qb-dro`):
`Order Processing`, `Finance`, `Billing and Invoicing`, `License Activation`, `Tenant Provisioning + Activation`, `Platform Provisioning`, `Platform`, `Services`, `Feature/License Provisioning + Activation`, `Asset Conversion`

### PFS `Action` Field Is Semicolon-Separated

Multiple actions use `;` as a separator within a single CSV cell: `Add;Amend;Renew;No Change;Cancel`. This is stored as a multi-select picklist by the platform. The platform validates that each action value is valid — confirm spelling exactly, including the space in `No Change`.

### Re-Running the Plan Is Safe (Idempotency)

PFDR and PFS use `operation: Upsert` with `externalId: Name`. Re-running the plan will update existing records, not create duplicates. The delete step before insert is retained for consistency with the usage+rates pattern, but is technically not required for Upsert objects.

---

## Current Template Implementation

The live template in `datasets/sfdmu/customer-template/en-US/customer-template-dro/` is populated with **Medinah Country Club** data (prefix `MCC-`). It serves as the reference implementation.

### PFDR Mapping (Medinah)

| Source SKU | Destination SKU | Routing Function |
|---|---|---|
| `MCC-MBR-IND` | `QB-DRO-BILL` | Finance — annual membership billing |
| `MCC-MBR-FAM` | `QB-DRO-BILL` | Finance |
| `MCC-MBR-JR` | `QB-DRO-BILL` | Finance |
| `MCC-MBR-SOC` | `QB-DRO-BILL` | Finance |
| `MCC-AMN-RACQUET` | `QB-DRO-BILL` | Finance — amenity pass billing |
| `MCC-AMN-GUNCLUB` | `QB-DRO-BILL` | Finance |
| `MCC-FEE-INIT-IND` | `QB-DRO-BILL` | Finance — one-time initiation fee |
| `MCC-FEE-INIT-FAM` | `QB-DRO-BILL` | Finance |
| `MCC-GOLF-PKG-GUEST` | `QB-DRO-BILL` | Finance — guest round billing |
| `MCC-GOLF-ACADEMY` | `QB-DRO-BILL` | Finance — instruction billing |
| `MCC-GOLF-ACADEMY` | `QB-DRO-PROJ` | Services — instructor assignment |
| `MCC-EVT-CORP` | `QB-DRO-BILL` | Finance — event billing |
| `MCC-EVT-CORP` | `QB-DRO-PROJ` | Services — event delivery |
| `MCC-EVT-PRES` | `QB-DRO-BILL` | Finance — VIP package billing |
| `MCC-PKG-ELITE` | `QB-DRO-BILL` | Finance — elite bundle billing |

### Product2 DecompositionScope (Medinah)

| SKU | DecompositionScope |
|---|---|
| `MCC-PKG-ELITE` | `Bundle` |
| All others | `OrderLineItem` |

### Demo Flow Steps

```
Step 11: delete_customer_demo_dro_data     (when: customer_demo_dro: true)
Step 12: insert_customer_demo_dro_data     (when: customer_demo_dro: true)
Step 13: update_customer_demo_fulfillment_decomp_rules  (when: customer_demo_dro: true)
```

Enable via `customer_demo_dro: true` in `cumulusci.yml` `project.custom` or org definition override.

---

## Adapting for a New Customer

1. Copy `datasets/sfdmu/customer-template/en-US/customer-template-dro/` to a customer-specific path (or update in place)
2. Replace all `MCC-` prefixes with the new customer prefix
3. Replace `MCC Individual Golf Membership to Finance` style names with customer product names
4. Review `Product2.csv` — update SKUs and names; adjust `DecompositionScope` (`Bundle` only for parent bundles)
5. Review `ProductFulfillmentScenario.csv` — update product SKUs and names; keep `FulfillmentStepDefnGroup.Name` values unchanged (they reference QB infrastructure)
6. Update `scripts/apex/deleteCustomerDemoDROData.apex` — change `LIKE 'MCC-%'` to the new customer prefix
7. Update `cumulusci.yml` task description to reflect the new customer prefix
8. Enable via `customer_demo_dro: true` and run `prepare_customer_demo_dro --org <alias>`

---

## Verification

```bash
# Verify PFDR records loaded
sf data query -q "SELECT Name, SourceProduct.StockKeepingUnit, DestinationProduct.StockKeepingUnit FROM ProductFulfillmentDecompRule WHERE Name LIKE 'MCC-%'" --target-org <alias>

# Verify PFS records loaded
sf data query -q "SELECT Name, Product.StockKeepingUnit, FulfillmentStepDefnGroup.Name, Action FROM ProductFulfillmentScenario WHERE Name LIKE 'MCC-%'" --target-org <alias>

# Verify Product2 DecompositionScope updated
sf data query -q "SELECT StockKeepingUnit, DecompositionScope FROM Product2 WHERE StockKeepingUnit LIKE 'MCC-%' AND DecompositionScope != null" --target-org <alias>

# Verify step groups exist (prerequisite check)
sf data query -q "SELECT Name FROM FulfillmentStepDefinitionGroup" --target-org <alias>
```

Expected for Medinah: 15 PFDR records, 22 PFS records (see plan), and 13 Product2 rows updated.
