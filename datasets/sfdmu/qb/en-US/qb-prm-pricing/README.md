# qb-prm-pricing Data Plan

SFDMU data plan for QuantumBit PRM pricing overlay data. This plan is sourced from
`chrisRossPRM_may2026` and is designed to run after baseline `qb-prm` so PRM pricing
records can be deployed without duplicating or replacing the original PRM dataset.

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
```

## Data Scope

This overlay includes:

- 3 Accounts (`Cloud Distributors`, `Infinitech`, `Robot Resellers`)
- 2 Channel Programs (`Distributor Program`, `Reseller Program`)
- 8 Channel Program Levels (Distributor + Reseller tiers with unique names)
- 2 Channel Program Members

The scope matches the PRM pricing seed records requested from the source org while
remaining compatible with baseline `qb-prm` deployment behavior.

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

## Idempotency and SFDMU Notes

- `ChannelProgramMember` uses traversal-based externalId (`Partner.Name;Program.Name`) to
  stay aligned with `qb-prm`.
- As with `qb-prm`, this is subject to SFDMU v5 traversal externalId behavior.
  The dataset is intended for controlled overlay usage behind `prm_pricing` and
  currently validates cleanly with `scripts/validate_sfdmu_v5_datasets.py`.
- Unlike baseline `qb-prm`, this overlay does not set `skipExistingRecords` on
  `ChannelProgramMember`. The two records are feature-owned seed data, and the
  org-backed idempotency task should be run before merge to confirm the current
  traversal-key behavior does not create duplicate memberships.

## Extraction

```bash
cci task run extract_qb_prm_pricing_data --org <org>
```

## Validation

```bash
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb/en-US/qb-prm-pricing
cci task run test_qb_prm_pricing_idempotency --org <org>
```
