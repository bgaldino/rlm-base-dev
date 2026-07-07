# qb-approvals Data Plan

SFDMU data plan for QuantumBit (QB) approval notifications. Resolves the
Lightning Email Templates created by `create_approval_email_templates`
(Readonly) and upserts `ApprovalAlertContentDef` records that link approval
flow/step notifications to those templates.

## CCI Integration

### Flow: `prepare_approvals`

This plan is executed as **step 4** of the `prepare_approvals` flow (when
`quantumbit=true` (`qb`) and `approvals=true`).

| Step | Task                              | When                          | Description                                                                 |
|------|------------------------------------|--------------------------------|-------------------------------------------------------------------------------|
| 1    | `deploy_post_approvals`            | qb + approvals                 | Deploys `unpackaged/post_approvals` (Flows, PathAssistant, quickAction, Apex, permission set) |
| 2    | `create_approval_email_templates`  | qb + approvals                 | Creates Lightning (SFX) EmailTemplate records from `EmailTemplate.csv`, links them to `ApprovalAlertContentDef` — required before step 4 |
| 3    | `assign_permission_sets`           | qb + approvals                 | Assigns approvals permission set(s)                                          |
| 4    | `insert_qb_approvals_data`         | qb + approvals                 | Runs this SFDMU plan                                                          |

### Task Definition

```yaml
insert_qb_approvals_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-approvals"
```

Also wired: `extract_qb_approvals_data` (`ExtractSFDMUData`) and
`test_qb_approvals_idempotency` (`TestSFDMUIdempotency`, no extraction
roundtrip).

## Data Plan Overview

Two objectSets, 2 objects total:

| # | Object                    | Operation | External ID | Records |
|---|---------------------------|-----------|--------------|---------|
| 1 | EmailTemplate             | Readonly  | (none — Readonly, no externalId needed) | 2 |
| 2 | ApprovalAlertContentDef   | Upsert    | `Name`       | 2       |

`EmailTemplate` is resolved `Readonly` (filtered `WHERE Name LIKE 'RLM%'`) so
that `ApprovalAlertContentDef.EmailTemplate.Name` can look up the templates
created upstream by `create_approval_email_templates` — this plan does not
create or modify EmailTemplate records itself.

## externalId / $$ Notes

- `ApprovalAlertContentDef` keys on `Name` (direct field, human-readable —
  e.g. "RLM Quote Discount Approval Alert"). No `$$` composite column is
  used; the CSV header is a plain field list including the
  `EmailTemplate.Name` traversal column for lookup resolution.
- `EmailTemplate` has no externalId (Readonly pass does not match/write).

## File Structure

```
qb-approvals/
├── export.json                          # SFDMU data plan (2 objects: EmailTemplate Readonly, ApprovalAlertContentDef Upsert)
├── README.md                            # This file
├── EmailTemplate.csv                    # 2 records (reference only — Readonly)
└── ApprovalAlertContentDef.csv          # 2 records
```
