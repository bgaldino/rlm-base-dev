# qb-approvals (QuantumBit)

SFDMU plan for Advanced Approvals notification content and related setup data used with QuantumBit.

## Objects

| Object | Operation | Notes |
|--------|-----------|-------|
| `EmailTemplate` | Readonly | Resolves Lightning email templates named `RLM%` for `ApprovalAlertContentDef` lookups. |
| `Group` | Readonly | Resolves **Director**, **Manager**, and **VP** public groups (`Type = Regular`) deployed from `force-app/main/default/groups/`. |
| `User` | Readonly | Resolves active users whose `UserRole.DeveloperName` is `CEO` (by `Username`). |
| `GroupMember` | Upsert + `skipExistingRecords` | Adds each resolved CEO user to all three groups. Polymorphic column `UserOrGroupId$User.Username` in SOQL; composite `externalId`: `Group.Name;Group.Type;UserOrGroupId$User.Username`. |
| `ApprovalAlertContentDef` | Upsert (`Name`) | Discount and payment-term approval alert definitions. |

## Runtime CSV materialization (`insert_qb_approvals_data`)

`User.csv` and `GroupMember.csv` in git are **placeholders** (headers only). Before each SFDMU run, **`LoadSFDMUData`** (when `dynamic_qb_approvals_group_members` is true, the default for this task) copies the plan to a temp directory and **rewrites** those CSVs from the **target org**:

1. Query active users with `UserRole.DeveloperName = 'CEO'`.
2. If none: fall back to the **running user** (the org user whose credentials run the task), matching the previous Apex sandbox behavior.
3. Emit one `GroupMember` row per **(CEO user × group)** for Director, Manager, and VP.

`Group.csv` stays version-controlled with the three group rows (`Name;Type` composite).

This avoids hard-coding usernames in git while keeping `excludeIdsFromCSVFiles: true` for portability.

## SFDMU v5 / idempotency notes

- Composite `$$` column on `GroupMember` matches `externalId` field list exactly.
- `externalId` on `GroupMember` includes relationship / polymorphic-style components; SFDMU v5 Upsert matching can be imperfect (see AGENTS.md Bug 3). **`skipExistingRecords: true`** is set to reduce overwrite risk on re-runs; re-run `test_qb_approvals_idempotency` after material changes.
- **`TestSFDMUIdempotency`** calls the same `materialize_qb_approvals_group_member_plan` helper before each `sf sfdmu run` so counts include `GroupMember` correctly.

## Prerequisites

- `deploy_full` (or equivalent) must have deployed public groups **Manager**, **Director**, and **VP** from `force-app/main/default/groups/`.
- For CEO resolution: a **`UserRole` with `DeveloperName` `CEO`** and at least one active user in that role, **or** the integration user running the load must exist in the org (fallback).
- `prepare_approvals` runs only when `quantumbit`, `approvals`, and `qb` feature flags are enabled.
