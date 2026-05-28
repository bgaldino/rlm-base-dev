# qb-prm-pricing Data Plan

SFDMU data plan for QuantumBit PRM pricing overlay data. Runs after baseline
`qb-prm` so PRM pricing records can be deployed without duplicating or
replacing the original PRM dataset.

## CCI Integration

### Flow: `prepare_prm_pricing`

This plan is executed in `prepare_prm_pricing` when `prm=true`,
`prm_pricing=true`, and `qb=true`. It follows the same staged pattern as
`qb-prm`, with an additional pass for Account self-lookup assignment.

| Pass | Purpose |
| ---- | ------- |
| 1 | Upsert Accounts, ChannelProgram, and ChannelProgramLevel records |
| 2 | Update `Account.IsPartner` state and upsert ChannelProgramMember records |
| 3 | Update Account self-lookups (`RLM_Primary_Distributor__c`, `RLM_Primary_Reseller__c`) |

### Task Definitions

```yaml
insert_quantumbit_prm_pricing_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-prm-pricing"

delete_quantumbit_prm_pricing_data:
  class_path: tasks.rlm_sfdmu.DeleteSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-prm-pricing"
```

## Data Scope

- 3 Accounts (`Cloud Distributors`, `Apex Dynamics`, `Robot Resellers`)
- 2 Channel Programs (`Distributor Program`, `Reseller Program`)
- 8 Channel Program Levels (Distributor + Reseller tiers with unique names)
- 2 Channel Program Members

### Objects

| Pass | Object | Operation | External ID | Records |
| ---- | ------ | --------- | ----------- | ------- |
| 1 | `Account` | Upsert | `Name` | 3 |
| 1 | `ChannelProgram` | Upsert | `Name` | 2 |
| 1 | `ChannelProgramLevel` | Upsert | `Name;Rank` | 8 |
| 2 | `Account` | Update | `Name` | 3 |
| 2 | `ChannelProgramMember` | Upsert | `Partner.Name;Program.Name` | 2 |
| 3 | `Account` | Update | `Name` | 3 |

Pass 1 and pass 3 both read `Account.csv`. Pass 1 creates or updates the
partner/customer Account records; pass 3 is the authoritative self-lookup pass
for `RLM_Primary_Distributor__c` and `RLM_Primary_Reseller__c` after both sides
of the Account relationship exist.

## Idempotency

This plan is verified idempotent. Running it multiple times against the same org
produces no duplicate records and no count increases.

`ChannelProgramMember` uses traversal-based externalId
(`Partner.Name;Program.Name`). Despite SFDMU v5 Bug 5 guidance that
all-traversal keys may fail Upsert matching, this plan has been tested and
confirmed to match correctly without duplicates. Neither a direct external key
field nor `Insert` + `deleteOldData: true` is required.

The plan must not use `Insert` + `deleteOldData: true`; these records are
feature-owned seed data and broad deletion would be too destructive for
rerunnable PRM setup.

### Validation

```bash
cci task run test_qb_prm_pricing_idempotency --org <org>
```

Loads the plan twice and asserts that scoped record counts do not increase on
the second load.

Expected outcome:

| Object | Expected Result |
| ------ | --------------- |
| `Account` | No count increase |
| `ChannelProgram` | No count increase |
| `ChannelProgramLevel` | No count increase |
| `ChannelProgramMember` | No count increase |

## Extraction

```bash
cci task run extract_qb_prm_pricing_data --org <org>
```

## Full Validation

```bash
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb/en-US/qb-prm-pricing
cci task run test_qb_prm_pricing_idempotency --org <org>
```
