# CLM Content and Migration

Read current-release Help articles for authoring steps and the dedicated
Contracts Developer Guide for CLM object/API details. For Release 264, start
with the [Clause Library overview](../../../docs/salesforce/264/help/articles/ind.sf_contracts_document_clause.htm.md),
the [`clm_developer_guide` index](../../../docs/salesforce/264/dev-guide-contracts/index.md),
and its [DocumentClause object](../../../docs/salesforce/264/dev-guide-contracts/articles/sforce_api_objects_documentclause.htm.md)
and [DocumentTemplate object](../../../docs/salesforce/264/dev-guide-contracts/articles/sforce_api_objects_documenttemplate.htm.md)
pages.

The Release 264 clause migration walkthrough and validation constraints are in
the separate Revenue Lifecycle Management Developer Guide deliverable:
[Clause Migration Considerations](../../../docs/salesforce/264/dev-guide/articles/deployment_contracts_clause_migration.htm.md)
and [Clause Validations and Migration Constraints](../../../docs/salesforce/264/dev-guide/articles/deployment_contracts_clause_validation_migration_constraints.htm.md).
Keep those corpora distinct. The migration pages carry a preview-release caveat;
check current Salesforce availability and release guidance before applying them.

## Clause library

The library has three configuration/content levels: clause category
configuration, document clause set, and document clause. Verify names,
language, version, status, main/alternate hierarchy, and file/content references
before building a plan. Do not treat a clause as ordinary mutable text:

- New clauses are created in Draft; imports also require Draft status.
- Active and Archived clause changes are constrained. Check the release guide's
  exact status and version rules before proposing an update.
- A clause set must exist before its clauses. Preserve the one-main-clause and
  alternate-clause constraints documented for the target release.
- Salesforce's migration sequence is category configuration, clause set, then
  clause. Category configuration is deployed as metadata; clause sets and clause
  records are data.
- Microsoft 365 template migration resolves clause references by clause-set
  name, clause name, version, and language rather than carrying source record
  IDs. Ensure exact matching target records exist before migrating templates.
- Keep source and target clause data stable between clause export and template
  migration. Follow the release-matched migration guide if the docs change.

## Document templates

Confirm the template-generation mechanism before editing: Salesforce Contracts
Microsoft Word templates, Design Document Templates, and this repository's
DocumentTemplate/ODT generation each have different tooling and metadata. Do not
apply ODT token or metadata instructions to Microsoft 365 CLM templates without
evidence that the target template uses that mechanism.

For repo-managed document generation, use `document-generation` for `.docx`
assets and the DocumentTemplate lifecycle, and `odt-authoring` for Extract and
Transform definitions. Check template status/version, related ContentDocument,
tokens, record access, and the source context before generation. For Microsoft
365 integration, use the applicable Salesforce Help setup and migration articles
for Azure, SharePoint, Named Credentials, external document storage, and the Word
add-in.

## Migration checklist

1. Inventory source/target release, enabled feature, org-specific configuration,
   clause sets, clauses, templates, files, and integration requirements.
2. Compare fields and relationships using target-org describes; don't assume IDs
   or field-level schema align across orgs/releases.
3. Migrate clause category configuration, then sets, then clauses. Preserve
   versions, languages, status rules, hierarchy, and content/file access.
4. Verify clause identity attributes used by the target template before moving
   template data. Resolve missing or mismatched clauses before template migration.
5. Migrate and validate templates and related files using the template's actual
   mechanism. Generate a representative document in a sandbox and inspect output.
6. Report what was verified and what still needs a live-org or business-owner
   check. Do not migrate sensitive contract text into the public repository.
