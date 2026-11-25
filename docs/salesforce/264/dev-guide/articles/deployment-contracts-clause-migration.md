---
page_id: deployment-contracts-clause-migration
title: Clause Migration Considerations
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-contracts-clause-migration.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-contracts-additional-info
legacy_page_id: deployment_contracts_clause_migration.htm
fetched_at: 2026-11-25
---

# Clause Migration Considerations

Clause migration is a prerequisite for Microsoft 365 template migration. Review these considerations to understand how clause structure, versions, and relationships must exist in the target org before migrating document templates.

Clause migration prepares the target org with all required clause data so that template migration can resolve clause references correctly. Clause records don’t retain source org record IDs during migration. Instead, template migration resolves references based on clause attributes and relationships that already exist in the target org.

Clause migration requires careful sequencing and coordination because clause records enforce strict validation rules around status, hierarchy, and versioning.

Microsoft 365 template migration requires all clause records, clause categories, and related clause sets to exist in the target org. If a clause contains clause content tokens, template migration also requires that those tokens exist in the target org.

During template migration, clause references resolve in the target org by matching this combination of attributes. Make sure that the target org contains clauses with the exact attribute values referenced by the Microsoft 365 template.

- ClauseSetName

- ClauseName

- ClauseVersion

- ClauseLanguage

If a referenced clause or clause content token is missing in the target org, template migration stops to prevent broken references. This alignment helps maintain template integrity and reduces the need for manual corrections after migration.

Migrate clause-related objects separately by using a data migration tool, such as Data Loader.

Migrate the document clause objects in the required order.

- Clause Category Configuration

- Document Clause Set

- Document Clause

- Document Clause Content Token

**Important:**

Avoid modifying clause data in the target org after migration to prevent mismatches between source and target.

Avoid modifying clause data in the source org after exporting clause data and before Microsoft 365 template migration to prevent reference mismatches.

## Clause Category Configuration

Clause Category Configuration is a setup object that you migrate by using metadata deployment tools, such as Package Manager, and Salesforce CLI. Migrate all clause categories referenced by your clause sets.

## Clause Set

Clause sets must be migrated before you can migrate clauses. This needs to be either created explicitly on the target org or migrated from the source org by using data migration utilities. Resolve these clause category configuration references to IDs on the target org in your export set before you migrate.

- `CategoryReferenceId`—Replace with the mapped ID obtained from clause category migration

- `Category`—This is a 15-character ID of the clause category. Update CategoryReferenceId by removing the last three characters.

For iterative migrations, use upsert operation to update existing clause sets and insert newly created clause sets since the previous migration.

## Clause

Migrate clause category configuration and clause sets before initiating clause migration. Resolve the clause set references (DocumentClauseSet) to the IDs on the target in your export set before migrating.

**Important:**

All clauses are inserted only in Draft status, regardless of their source status. Run a subsequent migration that includes status mapping to update the clauses to the correct status. See [Clause Status Mapping During Migration](./deployment-contracts-clause-validation-migration-constraints.md#clause-status-mapping-during-migration).

## Clause Content Token

Each clause content token belongs to a parent clause (DocumentClause) record. Migrate clause content tokens after you migrate their parent clauses. Resolve the clause references to the IDs on the target org in your export set before you migrate.

If a clause contains clause content tokens, template migration requires that those tokens exist in the target org.

## First-Time Migration

Use this approach when migrating clause data for the first time from the source org to the destination org for Microsoft 365 template migration. Clauses enforce validation rules that affect insert and update operations during migration.

- Insert main clauses before alternate clauses.

- Clauses are inserted in Draft status. Run a subsequent migration to update the clause status. See [Clause Status Mapping During Migration](./deployment-contracts-clause-validation-migration-constraints.md#clause-status-mapping-during-migration) for details on how clause statuses are applied and updated.

## Iterative Migration

Use iterative migration when clause data exists in the target org and you must migrate updates or newly created clauses from the source org. Track the timestamp of the last successful export and migrate only records that were created or updated after that timestamp. This approach avoids validation failures when attempting to update unchanged clauses, especially clauses in Archived status.

- Migrate clause records that were modified after the last export timestamp and created on or before the last export timestamp. This step migrates only updated records and preserves the correct status for existing clauses before introducing new draft versions.

- Migrate main clause records that were created after the last export timestamp. Clauses are inserted in Draft status. Run a subsequent migration to update the clause status. See [Clause Status Mapping During Migration](./deployment-contracts-clause-validation-migration-constraints.md#clause-status-mapping-during-migration) for details on how clause statuses are applied and updated.

- Migrate alternate clause records that were created after the last export timestamp. Clauses are inserted in Draft status. Run a subsequent migration to update the status.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-contracts-clause-migration.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
