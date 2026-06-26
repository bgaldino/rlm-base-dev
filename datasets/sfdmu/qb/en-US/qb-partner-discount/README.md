# qb-partner-discount Data Plan

SFDMU data plan for QuantumBit (QB) Partner Discount tier records. Loads three baseline `RLM_Partner_Discount__c` records — one per partner tier (Basic, Elite, Premier) — used by partner pricing scenarios.

## CCI Integration

### Task

This plan is run via a single insert task. It is **not** wired into any flow today; run it manually after the metadata for `RLM_Partner_Discount__c` is deployed (it lives in `force-app/main/default/objects/RLM_Partner_Discount__c/` and ships at step 5 of `prepare_rlm_org`).

```bash
cci task run insert_qb_partner_discount_data --org <alias>
```

### Task Definition

```yaml
insert_qb_partner_discount_data:
  group: Revenue Lifecycle Management
  description: Insert QuantumBit Partner Discount tier data (Basic / Elite / Premier).
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-partner-discount"
```

## Data Plan Overview

The plan uses a **single SFDMU pass** with one Upsert object. `excludeIdsFromCSVFiles: "true"` for cross-org portability.

```text
Single Pass (SFDMU)
───────────────────────────────────
Upsert RLM_Partner_Discount__c
(3 records: Basic + Elite + Premier)
```

### Objects

| # | Object                    | Operation | External ID | Records |
|---|---------------------------|-----------|-------------|---------|
| 1 | RLM_Partner_Discount__c   | Upsert    | `Name`      | 3       |

### Records

| Name                                  | RLM_Partner_Tier__c | RLM_Adjustment_Type__c | RLM_Adjustment__c |
|---------------------------------------|---------------------|------------------------|-------------------|
| Partner Price Basic - 5% Discount     | Basic               | Percentage             | 5                 |
| Partner Price Elite - 15% Discount    | Elite               | Percentage             | 15                |
| Partner Price Premier - 25% Discount  | Premier             | Percentage             | 25                |

`RLM_Adjustment__c` stores the positive percentage; the discount semantic is conveyed by the record `Name` plus `RLM_Adjustment_Type__c=Percentage`. Downstream pricing logic (when added) interprets these values as discount percentages.

## Portability

- **External ID**: `Name` — direct, human-readable Text field; portable across orgs.
- No auto-numbered fields, no composite keys, no `$$` columns, no relationship traversals.
- `Name` uniqueness is enforced by data convention (the three values above), not by schema (`Name` is not unique).

## Dependencies

**Upstream:**

- `force-app` deploy (step 5 of `prepare_rlm_org`) — provides the `RLM_Partner_Discount__c` object and its three custom fields.

**Downstream:**

- None today. Future partner pricing flows / decision tables may reference these records by `Name` or `RLM_Partner_Tier__c`.

## File Structure

```text
qb-partner-discount/
├── export.json                          # SFDMU data plan (single pass, 1 object)
├── README.md                            # This file
├── RLM_Partner_Discount__c.csv          # 3 records (Upsert)
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
└── target/                              # SFDMU-generated target snapshots
```

## Idempotency

Uses `Upsert` with `Name` as the external ID. Re-runs match the existing three records by `Name` and update them in place; no duplicates are created. The CSV defines the canonical content — drift in the org is overwritten on the next run.

## SFDMU v5 Compliance

- `externalId`: single direct field (`Name`) — no relationship traversals, so Bugs 1/2/3/5 do not apply.
- No `$$` composite key columns — Bug 4 does not apply.
- `excluded: false` — CSV has data rows, so destructive-delete safety guard is not triggered.
- `operation: Upsert` is safe and preferred per the v5 Operation Selection Guide (direct unique field).
