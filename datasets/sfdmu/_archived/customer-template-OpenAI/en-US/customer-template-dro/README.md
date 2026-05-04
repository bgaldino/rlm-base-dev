# customer-template-dro Data Plan

Customer-specific DRO (Dynamic Revenue Orchestration) overlay for the customer demo catalog. Maps customer sellable SKUs to fulfillment routing and step groups using the QB DRO infrastructure already in the org.

**Current customer:** Medinah Country Club (prefix `MCC-`)

---

## What This Plan Does

This plan adds three things on top of the QB DRO infrastructure:

1. **`ProductFulfillmentDecompRule`** (15 records) — routes each Medinah sellable SKU to a QB operational sub-product (`QB-DRO-BILL` for Finance, `QB-DRO-PROJ` for Services)
2. **`ProductFulfillmentScenario`** (22 records) — maps each Medinah SKU to a fulfillment step group for each lifecycle action (Add, Amend, Renew, Cancel)
3. **`Product2` (Update)** — sets `DecompositionScope` on the 13 Medinah products (`Bundle` for `MCC-PKG-ELITE`, `OrderLineItem` for all others)

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

## Decomposition Rules (PFDR)

| Source SKU | Destination | Function |
|---|---|---|
| `MCC-MBR-IND` | `QB-DRO-BILL` | Finance routing |
| `MCC-MBR-FAM` | `QB-DRO-BILL` | Finance routing |
| `MCC-MBR-JR` | `QB-DRO-BILL` | Finance routing |
| `MCC-MBR-SOC` | `QB-DRO-BILL` | Finance routing |
| `MCC-AMN-RACQUET` | `QB-DRO-BILL` | Finance routing |
| `MCC-AMN-GUNCLUB` | `QB-DRO-BILL` | Finance routing |
| `MCC-FEE-INIT-IND` | `QB-DRO-BILL` | Finance routing (one-time fee) |
| `MCC-FEE-INIT-FAM` | `QB-DRO-BILL` | Finance routing (one-time fee) |
| `MCC-GOLF-PKG-GUEST` | `QB-DRO-BILL` | Finance routing |
| `MCC-GOLF-ACADEMY` | `QB-DRO-BILL` | Finance routing |
| `MCC-GOLF-ACADEMY` | `QB-DRO-PROJ` | Services — instructor assignment |
| `MCC-EVT-CORP` | `QB-DRO-BILL` | Finance routing |
| `MCC-EVT-CORP` | `QB-DRO-PROJ` | Services — event delivery |
| `MCC-EVT-PRES` | `QB-DRO-BILL` | Finance routing |
| `MCC-PKG-ELITE` | `QB-DRO-BILL` | Finance routing (bundle) |

---

## Fulfillment Scenarios (PFS)

| SKU | Step Group | Actions |
|---|---|---|
| `MCC-MBR-IND` | Order Processing | Add |
| `MCC-MBR-IND` | Finance | Add;Amend;Renew;No Change;Cancel |
| `MCC-MBR-FAM` | Order Processing | Add |
| `MCC-MBR-FAM` | Finance | Add;Amend;Renew;No Change;Cancel |
| `MCC-MBR-JR` | Order Processing | Add |
| `MCC-MBR-JR` | Finance | Add;Amend;Renew;No Change;Cancel |
| `MCC-MBR-SOC` | Order Processing | Add |
| `MCC-MBR-SOC` | Finance | Add;Amend;Renew;No Change;Cancel |
| `MCC-AMN-RACQUET` | Order Processing | Add |
| `MCC-AMN-RACQUET` | Finance | Add;Amend;Renew;No Change;Cancel |
| `MCC-AMN-GUNCLUB` | Order Processing | Add |
| `MCC-AMN-GUNCLUB` | Finance | Add;Amend;Renew;No Change;Cancel |
| `MCC-FEE-INIT-IND` | Finance | Add |
| `MCC-FEE-INIT-FAM` | Finance | Add |
| `MCC-GOLF-PKG-GUEST` | Finance | Add |
| `MCC-GOLF-ACADEMY` | Finance | Add |
| `MCC-GOLF-ACADEMY` | Services | Add;Amend |
| `MCC-EVT-CORP` | Finance | Add |
| `MCC-EVT-CORP` | Services | Add;Amend |
| `MCC-EVT-PRES` | Finance | Add |
| `MCC-PKG-ELITE` | Order Processing | Add |
| `MCC-PKG-ELITE` | Finance | Add;Amend;Renew;No Change;Cancel |

---

## 260 Bug — ExecuteOnRuleId

`ProductFulfillmentDecompRule` does not generate `ExecuteOnRuleId` on INSERT — only on UPDATE. The `update_customer_demo_fulfillment_decomp_rules` task runs `scripts/apex/updateProductFulfillmentDecompRules.apex` which re-saves all PFDR records to trigger ruleset generation. This is step 3 of `prepare_customer_demo_dro` and step 13 of `prepare_customer_demo_catalog` when `customer_demo_dro: true`.

---

## Idempotency

Both PFDR and PFS use `operation: Upsert` with `externalId: Name`. Re-running the plan is safe — existing records are updated in place, no duplicates are created. The pre-delete step is included for consistency with other demo plans but is not strictly required for idempotency on Upsert objects.

---

## Adapting for a New Customer

1. Replace all `MCC-` SKU prefixes with the new customer prefix in all three CSVs
2. Replace rule/scenario names (`MCC Individual Membership to Finance` etc.) with new customer product names, keeping the `<Prefix> <ProductName> to/- <Function>` naming convention
3. Update `Product2.csv` — add/remove rows to match the new customer's sellable SKUs; set `Bundle` on bundle parent SKUs, `OrderLineItem` on all others
4. Update `scripts/apex/deleteCustomerDemoDROData.apex` — change `LIKE 'MCC-%'` scope to the new customer prefix
5. See `docs/features/customer-demo-dro.md` for the full business model playbook and implementation reference
