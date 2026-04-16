# Approvals Domain

1 core object for managing approval workflow submissions.

## Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `ApprovalSubmission` | Tracks an approval request | RelatedRecordId (self-ref/polymorphic) |

## Supporting Objects (from data plans)

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `ApprovalAlertContentDef` | Alert content definition for approval notifications | Name, EmailTemplateId |
| `EmailTemplate` | Email template used for approval alerts | Name (read-only reference) |

## Notes

- ApprovalSubmission is a self-referencing object (RelatedRecordId can point to another ApprovalSubmission or the record being approved)
- Approval email templates are `EmailTemplatePage` flexipages — these cannot be deployed via Metadata API and are created at runtime by `create_approval_email_templates` via the REST API
- The `qb-approvals` data plan loads `ApprovalAlertContentDef` records linking to pre-existing `EmailTemplate` rows, and **SFDMU** loads **`GroupMember`** rows so **active CEO-role users** are members of the **Manager**, **Director**, and **VP** public groups (metadata in `force-app/main/default/groups/`). `insert_qb_approvals_data` materializes `User.csv` / `GroupMember.csv` at runtime from the target org (`dynamic_qb_approvals_group_members` on `LoadSFDMUData`).

## SFDMU Data Plan: `qb-approvals`

2 objects across 2 objectSets. EmailTemplate is ReadOnly; ApprovalAlertContentDef uses Upsert on Name.
