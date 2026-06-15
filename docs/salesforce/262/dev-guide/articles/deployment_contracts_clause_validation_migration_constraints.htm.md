---
page_id: deployment_contracts_clause_validation_migration_constraints.htm
title: Clause Validations and Migration Constraints
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_contracts_clause_validation_migration_constraints.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_contracts_additional_info.htm
fetched_at: 2026-06-09
---

# Clause Validations and Migration Constraints

Validation rules, data model constraints, and known migration behaviors that affect
clause records during migration. Review this reference to understand sequencing, status
handling, and dependency requirements that can impact migration success.

## Clause Migration Validations

These validations apply during insert, update, and delete operations on clause records.
Operations fail when a validation is violated.

| Operation | Validation | Description |
| --- | --- | --- |
| Insert | Draft-only creation | Allows only Draft clauses during initial insert operations. |
| Insert | Version conflict prevention | Prevents inserting a clause when a Draft version exists for the same clause. |
| Insert | Clause set requirement | Requires each clause to reference a valid DocumentClauseSet that exists in the target org. |
| Insert | Main and alternate clause hierarchy | - Requires an existing main clause before inserting alternate clauses and allows   only one main clause per clause group. - Allows only one main clause per language within a clause set, and allows   multiple alternate clauses for the same language. |
| Update | Restricted fields | Prevents updating the DocumentClauseSet, Language, IsAlternateClause, and Version fields after clause creation. |
| Update | Status transition rules | Allows changing an Active clause only to Draft (without modifying other fields) or to Archived. |
| Update | Archived clause immutability | Prevents updates to Archived clauses. |
| Update | Content requirement for activation | Requires clause content before changing status to Active. |
| Delete | Status-based deletion | Allows deletion of Draft and Archived clauses only. |
| Delete | Main clause protection | Prevents deleting a main clause while alternate clauses still exist. |

## Clause Status Mapping During Migration

Clauses insert only in Draft status, regardless of their source status. Run a subsequent
migration with status mapping to update the clause statuses. For example, a clause in the
source org has three versions: Version 1 is Archived, Version 2 is Active, and Version 3 is
Draft. When the clause is inserted, all three versions are created in Draft status in the
target org. Perform a follow-up upsert migration with status mapping to align each clause
version with its source org status.

| Source Org Status (Pre-Migration) | Guidance |
| --- | --- |
| Archived | Archived clauses insert as Draft. Run a subsequent migration with status mapping to restore the Archived status. After a clause is archived, you can’t change its status. |
| Active | Active clauses insert as Draft. Run a subsequent migration with status mapping to restore the Active status. |
| Draft | Draft clauses insert as Draft, so no status change is required. |
| In Approval | You must not migrate In Approval clauses because their workflows don’t migrate. However, if In Approval clauses are migrated, they’re inserted in Draft status, and the approval process must be reinitiated from the UI. |

## Clause Migration Constraints

These constraints describe behavioral rules, sequencing requirements, and tooling
limitations that affect clause migration, especially during iterative and incremental
migrations.

| Category | Constraint | Description |
| --- | --- | --- |
| Tooling | No automated migration | Requires that you use supported data migration tools, such as Data Loader, because no automated clause migration utility exists. |
| Tooling | Authentication requirements for Data Loader | Requires OAuth-based authentication. Enforcing OAuth, Proof Key for Code Exchange (PKCE), or IP restrictions requires completing additional connected app and access configuration. |
| Data Model | Clause category limitations | Prevents adding custom fields to Clause Category Configuration because it’s a setup object. |
| Data Model | Manual ID creation | Creation of an external ID field in the target org to store source org IDs for upsert operations on clause sets and clause records. |
| Data Model | Manual ID mapping | Requires manually mapping clause category IDs between source and target orgs. |
| Data Dependency | Clause set dependency | Requires clause sets and clause category configuration to exist in the target org before importing clauses. |
| Iterative Migration | Migration order dependency | Requires that you update existing clauses before you insert newly created clauses. Also, insert main clauses before alternate clauses. |
| Template Dependency | Missing clause references | Prevents template migration when referenced clauses, versions, or languages don’t exist in the target org. |
| Template Dependency | Duplicate clauses | Can cause clause reference mismatches during template migration when duplicate clauses exist in the target org. |
| Template Dependency | Office Open XML failures | Can cause template migration to fail when Office Open XML updates fail during document import. |
