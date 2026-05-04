# customer-template-dro Data Plan

Customer-specific DRO (Dynamic Revenue Orchestration) overlay for the customer demo catalog. Maps customer sellable SKUs to fulfillment routing and step groups using the QB DRO infrastructure already in the org.

---

## What This Plan Does

This plan adds three things on top of the QB DRO infrastructure:

1. **`ProductFulfillmentDecompRule`** — routes each customer sellable SKU to a QB operational sub-product (`QB-DRO-BILL` for Finance, `QB-DRO-PROJ` for Services)
2. **`ProductFulfillmentScenario`** — maps each customer SKU to a fulfillment step group for each lifecycle action (Add, Amend, Renew, Cancel)
3. **`Product2` (Update)** — sets `DecompositionScope` on the customer products (`Bundle` for bundle parent SKUs, `OrderLineItem` for all others)

This plan does **NOT** create new step groups, step definitions, workspaces, or jeopardy/fallout rules — those are QB DRO infrastructure and must already exist from `prepare_dro`.

---

## Prerequisites

- `prepare_dro` has run on the org (`dro: true`, `qb: true`)
- `prepare_customer_demo_catalog` steps 1–10 have completed and verified
- QB routing products `QB-DRO-BILL` and `QB-DRO-PROJ` exist in the org

Verify prerequisites:
```bash
sf data query -q "SELECT Name FROM FulfillmentStepDefinitionGroup" --target-org <alias>
sf data query -q "SELECT StockKeepingUnit FROM Product2 WHERE StockKeepingUnit IN ('QB-DRO-BILL','QB-DRO-PROJ')" --target-org <alias>
```

---

## CCI Tasks

```bash
# Delete existing customer DRO records (scoped to MCC-* prefix)
cci task run delete_customer_demo_dro_data --org <alias>

# Load PFDR + PFS + Product2 DecompositionScope update
cci task run insert_customer_demo_dro_data --org <alias>

# Trigger 260 bug workaround — re-save PFDR to generate ExecuteOnRuleId
cci task run update_customer_demo_fulfillment_decomp_rules --org <alias>

# Run all three as a standalone flow (after catalog steps 1-10)
cci flow run prepare_customer_demo_dro --org <alias>

# Or enable as part of full catalog flow:
# Set customer_demo_dro: true in cumulusci.yml project.custom, then:
cci flow run prepare_customer_demo_catalog --org <alias>
```

---

## Objects

| Object | Operation | Records | ExternalId |
|---|---|---|---|
| `Product2` | Readonly (Set 1) | — | `StockKeepingUnit` |
| `FulfillmentStepDefinitionGroup` | Readonly (Set 1) | — | `Name` |
| `ProductFulfillmentDecompRule` | Upsert (Set 1) | 15 | `Name` |
| `ProductFulfillmentScenario` | Upsert (Set 1) | 22 | `Name` |
| `Product2` | Update (Set 2) | 13 | `StockKeepingUnit` |

**Why two objectSets?** PFDR and PFS need Product2 FKs resolved from the full org (including QB-DRO-* routing products), but the Product2 Update in Set 2 only touches customer SKUs. Separating Readonly (FK map building) from Update (field write) into different sets avoids having two Product2 entries in the same objectSet.

---

## CSV Data

`ProductFulfillmentDecompRule.csv` and `ProductFulfillmentScenario.csv` are populated per customer. See `datasets/sfdmu/_archived/` for reference examples from previous customers. When building the PFS CSV, use the verified group names from the target org (see pitfall above) — not assumed names like "Order Processing".

---

## Critical — FulfillmentStepDefinitionGroup Names Are Org-Specific

`FulfillmentStepDefinitionGroup.Name` values in `ProductFulfillmentScenario.csv` **must match the groups that exist in the target org**. These groups are created by `prepare_dro` and can vary by org.

**Always verify available groups before populating the CSV:**
```bash
sf data query -q "SELECT Id, Name FROM FulfillmentStepDefinitionGroup" --target-org <alias>
```

**Common mismatch:** The CSV may reference `Order Processing` but the org uses `Provisioning & Activation` instead. When SFDMU cannot resolve the group name, it silently sets `FulfillmentStepDefnGroupId = null` — no error, but the scenario is broken and the Fulfillment tab stays empty.

If scenarios are loaded with null group IDs, fix them in Apex:
```apex
FulfillmentStepDefinitionGroup g = [SELECT Id FROM FulfillmentStepDefinitionGroup WHERE Name = 'Provisioning & Activation' LIMIT 1];
List<ProductFulfillmentScenario> broken = [SELECT Id FROM ProductFulfillmentScenario WHERE Name LIKE '<PREFIX>%' AND FulfillmentStepDefnGroupId = null];
for (ProductFulfillmentScenario s : broken) s.FulfillmentStepDefnGroupId = g.Id;
if (!broken.isEmpty()) update broken;
```

Typical group mapping (verify per org):
| Scenario purpose | Group name to use |
|---|---|
| Finance / billing routing | `Finance` |
| Professional services delivery | `Services` |
| Subscription activation / provisioning | `Provisioning & Activation` |
| Platform-level provisioning | `Platform` |
| Usage metering activation | `Usage Provisioning & Activation` |

---

## Manual vs Automatic DRO Triggering

DRO decomposition does **not necessarily fire automatically** on order activation. Many orgs use manual triggering — the user must click **"Submit Orchestration Request"** (or equivalent button) in the order's Fulfillment tab after activation.

If the Fulfillment tab shows "After you submit the orchestration request, you'll find the decomposed line items here", that is the expected state after activation — look for the Submit button on the tab. If no button is visible, check that the order's products all have matching PFDR records and that no PFS records have a null `FulfillmentStepDefnGroupId`.

---

## ExecuteOnRuleId and ScenarioRuleId

These fields are null for all PFDR and PFS records in most orgs — that is normal and not an indicator of misconfiguration. The `update_customer_demo_fulfillment_decomp_rules` task (re-save all PFDRs) was added to address a Spring '26 INSERT bug, but in practice `ExecuteOnRuleId = null` does not block DRO from working in current orgs. The task is retained as a safety measure but the root cause of missing fulfillment is almost always a null `FulfillmentStepDefnGroupId` on PFS records (wrong group name) or the order needing a manual orchestration submit.

---

## Idempotency

Both PFDR and PFS use `operation: Upsert` with `externalId: Name`. Re-running the plan is safe — existing records are updated in place, no duplicates are created. The pre-delete step is included for consistency with other demo plans but is not strictly required for idempotency on Upsert objects.

---

## Adapting for a New Customer

1. **Verify available step groups first** — query `SELECT Id, Name FROM FulfillmentStepDefinitionGroup` on the target org and note the exact names. Use those names in `ProductFulfillmentScenario.csv`, not assumed names like "Order Processing".
2. Replace all customer-specific SKU prefixes in all three CSVs with the new customer prefix
3. Replace rule/scenario names with new customer product names, keeping the `<Prefix> <ProductName> to/- <Function>` naming convention
4. Update `Product2.csv` — add/remove rows to match the new customer's sellable SKUs; set `Bundle` on bundle parent SKUs, `OrderLineItem` on all others
5. Update `scripts/apex/deleteCustomerDemoDROData.apex` — change the `LIKE` scope to the new customer prefix
6. See `docs/features/customer-demo-dro.md` for the full business model playbook and implementation reference
