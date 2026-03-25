# qb-prm Data Plan

SFDMU data plan for QuantumBit (QB) Partner Relationship Management (PRM). Creates the channel program structure with partner accounts, program levels (tiers), and program memberships with partner-specific discount rates.

## CCI Integration

### Flow: `prepare_prm`

This plan is executed as **step 9** of the `prepare_prm` flow (when `prm=true` and `qb=true`).

| Step | Task                              | Description                                                |
|------|-----------------------------------|------------------------------------------------------------|
| 1    | `create_partner_central`          | Create Partner Central community                           |
| 2    | `patch_network_email_for_deploy`  | Replace placeholder email in rlm.network-meta.xml with Network's actual EmailSenderAddress (immutable) |
| 3    | `setup_prm_org_email`             | Create org-wide email address for PRM                      |
| 4    | `deploy_post_prm`                 | Deploy PRM Experience Bundle metadata                      |
| 5    | `revert_network_email_after_deploy` | Restore placeholder email in rlm.network-meta.xml        |
| 6    | `publish_community`               | Publish the Partner Central community                      |
| 7    | `deploy_sharing_rules`            | Deploy sharing rules for PRM                               |
| 8    | `assign_permission_sets`         | Assign `RLM_PRM` permission set                            |
| 9    | `insert_quantumbit_prm_data`      | Runs this SFDMU plan (2-pass)                              |

### Task Definition

```yaml
insert_quantumbit_prm_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-prm"
```

## Data Plan Overview

The plan uses a **2-pass SFDMU plan** via `objectSets` (same pattern as qb-billing). Pass 1 creates the Account and program structure. Pass 2 enables `IsPartner` on the Account (not createable via API, only updateable) and links ChannelProgramMember to the partner-enabled Account.

```
Pass 1 — Upsert Accounts and Channel Programs
---------------------------------------------
Account (Upsert) → ChannelProgram (Upsert) →
ChannelProgramLevel (Upsert)

Pass 2 — Enable Partner Accounts and Link Members
--------------------------------------------------
Account (Update IsPartner=true) →
ChannelProgramMember (Upsert)
```

### Objects

| Pass | Object                | Operation | External ID                  | Records |
|------|-----------------------|-----------|------------------------------|---------|
| 1    | Account               | Upsert    | `Name`                       | 1       |
| 1    | ChannelProgram        | Upsert    | `Name`                       | 1       |
| 1    | ChannelProgramLevel   | Upsert    | `Name;Rank`                  | 4       |
| 2    | Account               | Update    | `Name`                       | 1       |
| 2    | ChannelProgramMember  | Upsert    | `Partner.Name;Program.Name`  | 1       |

## Key Design Decisions

### Account — 2-pass IsPartner enablement

`Account.IsPartner` is `createable: false, updateable: true`. On a fresh org, pass 1 inserts the Account (IsPartner is ignored), then pass 2 updates it to `IsPartner=true`. This ensures the Account is partner-enabled before `ChannelProgramMember` links to it via `PartnerId`.

### ChannelProgramLevel (Pass 1)

Uses composite externalId `Name;Rank` — both are direct fields on the object, which ensures SFDMU Upsert correctly matches existing records (avoids SFDMU v5 Bug 3 with relationship-traversal externalIds). Includes custom fields for partner discount management:
- `RLM_Deal_Expiration_Days__c` — deal registration expiration
- `RLM_Discount_Rate__c` — discount percentage for the tier
- `RLM_Minimum_Deal_Size__c` — minimum deal size threshold

### ChannelProgramMember (Pass 2)

Auto-numbered `Name` field (`00000003` format) — not used as externalId. Uses `Partner.Name;Program.Name` composite key instead (a partner can only be enrolled in a program once). Uses `Upsert` with `skipExistingRecords: true` to preserve any existing members not in this plan.

Custom fields carry partner-specific pricing adjustments:
- `RLM_Adjustment_Type__c` — adjustment type (e.g., "Percentage")
- `RLM_Adjustment_Value__c` — adjustment amount
- `RLM_Discount_Rate__c` — partner discount rate

#### Known Constraint: SFDMU v5 Bug 3

ChannelProgramMember's `externalId` (`Partner.Name;Program.Name`) uses relationship-traversal fields, which are subject to [SFDMU v5 Bug 3](https://github.com/forcedotcom/SFDX-Data-Move-Utility/issues/781) — Upsert with relationship-traversal externalIds never matches existing records and always inserts. This means re-running the plan may create duplicate members.

Currently mitigated by `skipExistingRecords: true`, but this is not a reliable fix because SFDMU cannot identify existing records when matching fails. The plan passes idempotency testing with the current single-member dataset, but could produce duplicates at scale.

**Potential future fixes (in order of preference):**

1. **Custom External ID field** — Add an `RLM_External_Id__c` (Text, External ID) field on `ChannelProgramMember`. Populate with a composite value like `"Robot Resellers:Reseller Program"` in the CSV. SFDMU Upsert matches correctly on direct fields. Requires adding the field metadata, updating the `RLM_PRM` permission set, and deploying before the data load.

2. **`Insert` + `deleteOldData: true`** — Switch the operation to Insert with `deleteOldData: true`. SFDMU deletes all existing ChannelProgramMember records first, then re-inserts from CSV. Simple but destructive — any members created outside this plan (e.g., manually or by other processes) would be deleted on every run.

3. **Use direct fields for externalId** — ChannelProgramMember has no direct unique or external ID fields beyond the auto-numbered `Name`. `PartnerId` and `ProgramId` are reference fields (only accessible via relationship traversal). There are no other direct field candidates for a composite key without creating a custom field (see option 1).

## Custom Fields and Permission Set

### Custom Field Metadata

Custom fields are packaged under `force-app/main/default/objects/`:

| Object                | Field                          | Type          | Label                |
|-----------------------|--------------------------------|---------------|----------------------|
| ChannelProgramLevel   | `RLM_Deal_Expiration_Days__c`  | Number(18,0)  | Deal Expiration Days |
| ChannelProgramLevel   | `RLM_Discount_Rate__c`         | Percent(18,0) | Discount Rate        |
| ChannelProgramLevel   | `RLM_Minimum_Deal_Size__c`     | Currency(18,0)| Minimum Deal Size    |
| ChannelProgramMember  | `RLM_Adjustment_Type__c`       | Text(255)     | Adjustment Type      |
| ChannelProgramMember  | `RLM_Adjustment_Value__c`      | Number(18,2)  | Adjustment Value     |
| ChannelProgramMember  | `RLM_Discount_Rate__c`         | Number(18,2)  | Discount Rate        |

### Permission Set: `RLM_PRM`

Grants full read/edit access to all 6 custom fields above. Assigned in step 8 of the `prepare_prm` flow before the data load, ensuring SFDMU can write to the custom fields.

## Composite External IDs

| Object                | Composite Key             | CSV `$$` Column   | Bug 3 Risk |
|-----------------------|---------------------------|--------------------|------------|
| ChannelProgramLevel   | `Name;Rank`               | `$$Name$Rank`      | No — direct fields |
| ChannelProgramMember  | `Partner.Name;Program.Name` | `$$Partner.Name$Program.Name` | **Yes** — relationship traversals |

## Portability

All external IDs use portable, human-readable fields:
- **Account.Name**: "Robot Resellers" — descriptive, stable
- **ChannelProgram.Name**: "Reseller Program" — descriptive, stable
- **ChannelProgramLevel**: `Name` + `Rank` — descriptive, stable
- **ChannelProgramMember**: Identified by parent traversals (Partner.Name + Program.Name)

No auto-numbered Name fields are used as external IDs.

## Dependencies

This plan has **no upstream data plan dependencies** — it creates its own Account records.

This plan is independent of the product catalog (qb-pcm) and can be loaded in any order relative to other QB plans. However, the `prepare_prm` flow runs metadata deployment, community setup, and permission assignment (steps 1-8) before this data load (step 9).

## File Structure

```
qb-prm/
├── export.json                   # SFDMU data plan (2-pass objectSets, 5 object configs)
├── README.md                     # This file
│
│  Source CSVs
├── Account.csv                   # 1 record (Robot Resellers)
├── ChannelProgram.csv            # 1 record (Reseller Program)
├── ChannelProgramLevel.csv       # 4 records (Platinum, Gold, Silver, Bronze)
├── ChannelProgramMember.csv      # 1 record (Robot Resellers @ Gold)
│
│  SFDMU Runtime (gitignored)
├── source/
└── target/
```

## Extraction

```bash
cci task run extract_qb_prm_data --org <your-org>
```

## Idempotency

```bash
cci task run test_qb_prm_idempotency --org <your-org>
```

Account, ChannelProgram, and ChannelProgramLevel are fully idempotent via Upsert on direct fields. ChannelProgramMember passes idempotency testing with the current dataset but is subject to SFDMU v5 Bug 3 — see [Known Constraint](#known-constraint-sfdmu-v5-bug-3) above.
