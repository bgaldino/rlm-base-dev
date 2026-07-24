# qb-approvals Data Plan

SFDMU data plan for QuantumBit Advanced Approvals notification records. It
loads `ApprovalAlertContentDef` rows that link approval workflow steps to
Lightning email templates created by `create_approval_email_templates`.

## CCI Integration

### Flow: `prepare_approvals`

This plan runs as step 4 of `prepare_approvals` after the approval metadata is
deployed and the Lightning email templates are created.

| Step | Task                              | Description                                                        |
| ---- | --------------------------------- | ------------------------------------------------------------------ |
| 1    | `deploy_post_approvals`           | Deploys approval metadata                                          |
| 2    | `create_approval_email_templates` | Creates Lightning `EmailTemplate` records from `EmailTemplate.csv` |
| 3    | `assign_permission_sets`          | Assigns `RLM_Approvals`                                            |
| 4    | `insert_qb_approvals_data`        | Upserts alert content definitions                                  |

`EmailTemplate` rows are marked `Readonly` in `export.json` because Lightning
email templates are created through the REST API task instead of Metadata API or
SFDMU DML.

## Data Plan Overview

The plan uses two object sets:

| # | Object                  | Operation | External ID | Records |
| - | ----------------------- | --------- | ----------- | ------- |
| 1 | EmailTemplate           | Readonly  | --          | 2       |
| 2 | ApprovalAlertContentDef | Upsert    | `Name`      | 2       |

`ApprovalAlertContentDef` uses a direct-field external ID (`Name`), so it stays
idempotent with `operation: Upsert`. Do not change this plan to
`Insert` + `deleteOldData: true`.

## Notification Rows

Current notifications:

| Alert                                 | Flow                       | Step               | Template                                  |
| ------------------------------------- | -------------------------- | ------------------ | ----------------------------------------- |
| RLM Quote Discount Approval Alert     | `RLM_Quote_Smart_Approval` | `Manager_Approver` | RLM Quote Discount Approval Template      |
| RLM Quote Payment Term Approval Alert | `RLM_Quote_Smart_Approval` | `Payment_Terms`    | RLM Quote Payment Terms Approval Template |

## Adding A New Approval Step Family

To add notification coverage for a new approval dimension:

1. Add one row to `EmailTemplate.csv`.
2. Add one row to `ApprovalAlertContentDef.csv`.
3. Set `ApprovalFlowApiName` to `RLM_Quote_Smart_Approval`.
4. Set `ApprovalStepApiName` to the exact `stageSteps/name` value in the flow.
5. Set `NotificationReason` to the reason used by the approval step, normally
   `ApprovalStepAssignment`.
6. Set `EmailTemplate.Name` to the template `Name` from `EmailTemplate.csv`.

The Python task is CSV-driven and processes all template and alert rows. No code
change is required for a normal new step family.

## Validation

After changing this plan, run:

```bash
python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/qb/en-US/qb-approvals
python scripts/validate_sfdmu_v5_datasets.py
```
