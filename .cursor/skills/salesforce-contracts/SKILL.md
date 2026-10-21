---
name: salesforce-contracts
description: >-
  Set up, configure, query, author, or troubleshoot Salesforce Contracts (CLM)
  in Revenue Cloud orgs and this Foundations repository. Use for contract types,
  lifecycle state models, clause libraries, document templates, Context Service,
  permissions, and CLM data migration. Read the release-matched Help and
  Contracts Developer Guide snapshots before asserting product behavior.
---

# Salesforce Contracts — Setup and Content Workflows

Use this skill for Salesforce Contracts, Salesforce's CLM capability. It covers
org setup, clause and template content, lifecycle configuration, and diagnosis
in Salesforce orgs and the Revenue Cloud Foundations repository.

## Quick Rules

1. Establish the target Salesforce release and org type before relying on a
   feature or field; a fresh 264 org and an upgraded org can differ.
2. Read the matching release's Contracts Help snapshot for admin behavior and
   Contracts developer-guide snapshot for APIs, deployment, and object details.
3. Use the Revenue Cloud data-model skill for known relationships, then describe
   objects in the target org before writing or running SOQL.
4. Treat setup prerequisites as a dependency chain: feature/license access,
   settings and permissions, contract type/state configuration, then content
   and workflow verification.
5. Keep clause category configuration, clause sets, and clause records aligned;
   migration order and lifecycle validations are significant.
6. Route document-template and ODT implementation details to
   `document-generation` and `odt-authoring`; use `context-service` for Context
   Definitions and mappings.
7. Distinguish Salesforce-documented behavior, what this repo deploys, and what
   a target org actually contains. Label any live verification with its org,
   release, and date.

## DO NOT

- Do not treat Revenue Cloud transaction-mgmt articles (`ind.qocal_*`) as the
  complete Salesforce Contracts Help corpus; CLM has its own `ind.sf_contracts_*`
  Help tree.
- Do not infer current availability or field legality from a different release's
  schema, permission sets, or org configuration.
- Do not invent field or relationship names. Run `sf sobject describe` against
  the target org and select only fields it reports.
- Do not change Active or Archived clause records as if they were ordinary
  mutable text. Follow documented clause lifecycle and version rules.
- Do not assume template metadata migration also migrates clause records or
  referenced files. Follow the target release's migration guide and validate
  dependencies first.
- Do not modify an org, activate content, send contracts for signature, or move
  lifecycle state unless the user requested that action.

## Entry Conditions

| Use this skill when… | Also read… |
|---|---|
| Enabling CLM or diagnosing missing setup | `setup-and-diagnostics.md` |
| Querying contract, state, clause, or template configuration | `data-model-and-queries.md` and `revenue-cloud-data-model` |
| Creating or changing clauses or templates | `content-and-migration.md` |
| Editing document templates, tokens, or ODTs | `document-generation` and/or `odt-authoring` |
| Changing Context Definitions or mappings | `context-service` |
| Loading or extracting the shipped sample plan | `sfdmu-data-plans` |
| Grounding release-specific product behavior | `revenue-cloud-docs` |
| Expanding or certifying fields and relationships in the repository ERD | `schema-validation` |

## Workflow

1. **Scope the request.** Record release/API version, org type, feature/license
   availability, and whether the request concerns core Revenue Cloud contracts,
   Salesforce Contracts CLM, or both.
2. **Inspect sources.** Search the snapshot indexes and manifests for the relevant
   Help topics and developer-guide pages. Read the article/page, not only its
   title. If missing, use `revenue-cloud-docs` to assess snapshot coverage before
   relying on an external source.
3. **Inspect the repo and org.** Follow relevant build/data configuration in
   `cumulusci.yml`, the CLM data plan, metadata, and the data-model skill. In an
   org, use `sf sobject list` and `sf sobject describe`; then issue read-only SOQL
   using only confirmed fields and relationships. For repository ERD changes,
   use the release-matched schema-validation workflow and its Core UDD checks;
   don't promote one org's field list directly into the canonical ERD.
4. **Work through dependencies.** Verify licenses, permissions, settings, sharing,
   contract types/record types, state models, context mappings, clause sets,
   clause content, and templates as applicable to the requested use case.
5. **Validate at the right level.** Check repository artifacts offline first.
   Confirm org-specific configuration and behavior in a compatible sandbox when
   the question depends on live state or the docs are inconclusive.
6. **Report evidence and gaps.** Cite snapshot paths and identify the release.
   Separate repository state from target-org state. State when missing access,
   licensing, or a thin/preview source prevents a conclusion.

## Examples

### Find guidance for a clause lifecycle question

Search `docs/salesforce/264/help/manifest.json` for clause topics, read the
matching article under `help/articles/`, and compare it with the relevant page in
`docs/salesforce/264/dev-guide-contracts/articles/`. Use the Help article for
admin steps and the Contracts developer guide for schema, migration, or API
details.

### Diagnose a missing clause or template

Confirm the object and fields exist in the target org, query the clause category,
set, clause, and template records, and check status/version and referenced file
relationships. Then compare the findings with the documented lifecycle and
template prerequisites. See `data-model-and-queries.md` for SOQL patterns.

### Trace what Foundations seeds

Inspect `datasets/sfdmu/qb/en-US/qb-clm/README.md` and `export.json`. The shipped
plan upserts clause category configurations, document clause sets, and state
model records; it does not provide complete clause bodies or document templates.
The `clm_data` flag is separate from the `clm` feature flag.

## Validation Checks

- Confirm every Salesforce product claim against a release-matched snapshot or
  clearly identify the external source and its date.
- Confirm each object, field, lookup, and relationship in the target org before
  using SOQL or recommending a data plan.
- Confirm clause category/set/clause migration order and clause lifecycle
  constraints before planning a content migration.
- Check CLM license and permission prerequisites against the target org, not only
  the permission-set group shipped in this repo.
- For repository changes, follow `doc-consistency` and the relevant document,
  Context Service, or SFDMU skill.

## Sub-files

- Read [`setup-and-diagnostics.md`](setup-and-diagnostics.md) for setup and
  troubleshooting paths.
- Read [`content-and-migration.md`](content-and-migration.md) for clause and
  template workflows.
- Read [`data-model-and-queries.md`](data-model-and-queries.md) for schema
  discovery and safe, reusable SOQL examples.
