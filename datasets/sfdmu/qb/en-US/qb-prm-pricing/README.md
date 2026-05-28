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

- 3 Accounts (`Cloud Distributors`, `Apex Dynamics`, `Robot Resellers`)
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

- `ChannelProgramMember` uses traversal-based externalId
  (`Partner.Name;Program.Name`) to stay aligned with `qb-prm`.
- This is a narrow, org-verified exception to the general SFDMU v5
  relationship-traversal Upsert guidance. The overlay has been validated
  against target environments and does not require an external key field.
- The plan must not use `Insert` + `deleteOldData: true`; these records are
  feature-owned seed data, but broad deletion would still be too destructive for
  rerunnable PRM setup.
- Rerun validation remains part of the PR checklist for any change that touches
  this plan or its `ChannelProgramMember` records.

### Idempotency Validation

Run the org-backed idempotency task against a prepared PRM org:

```bash
cci task run test_qb_prm_pricing_idempotency --org <org>
```

The validation loads the plan twice and asserts that scoped record counts do not
increase on the second load.

Expected outcome:

| Object | Expected Result |
| ------ | --------------- |
| `Account` | No count increase |
| `ChannelProgram` | No count increase |
| `ChannelProgramLevel` | No count increase |
| `ChannelProgramMember` | No count increase; remains at the 2 feature-owned PRM pricing members |

Additional SOQL spot checks should confirm the two PRM pricing members remain
the expected records:

| Partner | Program | Level | Discount Rate |
| ------- | ------- | ----- | ------------- |
| Cloud Distributors | Distributor Program | Gold - Distributor | 10 |
| Robot Resellers | Reseller Program | Silver - Reseller | 5 |

Conclusion: the current `Partner.Name;Program.Name` traversal external ID did
not create duplicate `ChannelProgramMember` rows in the validated org. No direct
`RLM_PRM_Pricing_Key__c` field or destructive `deleteOldData` strategy is
required based on this validation.

## Extraction

```bash
cci task run extract_qb_prm_pricing_data --org <org>
```

## Validation

```bash
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb/en-US/qb-prm-pricing
cci task run test_qb_prm_pricing_idempotency --org <org>
```
