# CLM Data Model and Query Recipes

Use the [Revenue Cloud data-model skill](../revenue-cloud-data-model/SKILL.md)
for the core transaction graph and `scripts/ai/query_erd.py` for supported ERD
queries. The standard ERD is not a complete CLM schema catalog. Salesforce
Contracts objects and fields vary by release, org configuration, and assigned
licenses; verify them directly before running each SOQL query.

When extending the canonical ERD, follow
[`schema-validation`](../schema-validation/SKILL.md): the repository has built
release snapshots from `sf sobject describe` in release-matched prepared orgs,
compared those snapshots across releases, and checked canonical field status
against Core UDD source. The `sf sobject list` command is the object inventory;
individual `describe` responses provide fields, types, and lookup targets.
Release-matched Help and developer-guide snapshots explain behavior and
semantics, while this repo's SFDMU plan and metadata show which CLM records and
definitions Foundations ships. A connected customer org is useful to describe
that org's actual shape, but it is not by itself canonical ERD evidence.

The [interactive ERD viewer](../../../docs/erds/revenue-cloud-erd.html) now
includes a separate [Contracts CLM extension](../../../docs/erds/contracts-erd-data.json)
alongside the canonical Revenue Cloud graph. It adds 40 nodes, 446 fields, and
55 incremental relationship edges; `scripts/ai/query_erd.py` reads both datasets.
Its source inventory is the [264 CLM schema snapshot](../../../scripts/erd/schema_diff/264-clm-schema.json),
cross-checked against four API v68.0 prepared Enterprise orgs. This is a useful
release-specific model, not proof that every org exposes every feature: `ContractType`
and `DocumentTemplate` were unavailable in one of the four orgs each. Four
additional Developer Guide object pages were absent from the primary org's
object inventory and failed direct describe in all four. Two included generation status-event
objects are marked not SOQL-queryable. The snapshot records these limits and
keeps the CLM extension separate from the Revenue Cloud release-diff baseline.

## Discover before querying

Use the Salesforce CLI alias (not the CCI alias):

```bash
sf sobject list --sobject all --target-org <sf_alias>
sf sobject describe --sobject ContractType --target-org <sf_alias> --json
sf sobject describe --sobject DocumentClause --target-org <sf_alias> --json
sf sobject describe --sobject DocumentTemplate --target-org <sf_alias> --json
sf sobject describe --sobject ObjectStateDefinition --target-org <sf_alias> --json
```

`sf sobject list` identifies objects visible to the current connection. For each
object, inspect queryability, field names, types, and relationship names in the
describe response. If an object is missing, check release, feature/license
availability, API visibility, and permissions before concluding it is unsupported.

## Inventory queries

The state and clause-set fields below are present in the repository's Release
264 schema/data plan. The base Revenue Cloud snapshot does not carry full field
inventories for `DocumentClause`, `DocumentTemplate`, or `ContractType`; the new
supplemental `264-clm-schema.json` does, based on prepared-org describes. Always
re-describe the target org before querying because feature visibility differs.

### Connected-org schema observation

A read-only `sf sobject describe` against `rlm-base__ent_1002` on 2026-10-13
confirmed the following org-specific shape. This is a live-org observation,
not a replacement for the release-matched canonical ERD or a promise that other
orgs expose the same schema:

| Object | Queryable | Relationships observed |
|---|---:|---|
| `Contract` | Yes | `AccountId` → `Account`, `RecordTypeId` → `RecordType`, `ContractDocumentVersionId` → `ContractDocumentVersion` |
| `ContractType` | Yes | Exposes `MasterLabel`, `DeveloperName`, `SubTypes`, and `IsDefault` in this org; the 264 Developer Guide documents `Name` instead, so verify before selecting a label field. |
| `ContractTypeConfig` | Yes | `ContractTypeId` → `ContractType` |
| `DocumentClauseSet` | Yes | `CategoryReferenceId` → `ClauseCatgConfiguration` (relationship name `CategoryReference`) |
| `DocumentClause` | Yes | `DocumentClauseSetId` → `DocumentClauseSet`; `Content` is present but should not be copied into diagnostic output. |
| `DocumentTemplateSection` | Yes | `DocumentTemplateId` → `DocumentTemplate`, `EmbeddedDocumentTemplateId` → `DocumentTemplate`, `DocumentTemplateClauseId` → `DocumentClause` |
| `ObjectStateDefinition` | Yes | `Name`, `ReferenceObject`, `ReferenceField`, `AdditionalField`, `AppUsageType`, `VersionNumber`, `IsActive` are available. |
| `ObjectStateValue` | Yes | `ObjectStateDefinitionId` is available. |
| `ObjectStateTransition` | Yes | `ObjectStateDefinitionId` → `ObjectStateDefinition`, `FromStateId` → `ObjectStateValue` (`FromState`), `ToStateId` → `ObjectStateValue` (`ToState`). |
| `ObjectStateTransitionAction` | Yes | `ObjectStateDefinitionId` → `ObjectStateDefinition`, `ObjectStateTransitionId` → `ObjectStateTransition`, `ObjectStateActionDefinitionId` → `ObjectStateActionDefinition`. |
| `ContextDefinition` | Yes | `DeveloperName`, `MasterLabel` are available. |
| `ContextDefinitionVersion` | Yes | `ContextDefinitionId` → `ContextDefinition`; `IsActive` is available. |
| `ContextMapping` | Yes | `ContextDefinitionVersionId` → `ContextDefinitionVersion`. |
| `ContextNode` | Yes | `ContextDefinitionVersionId` → `ContextDefinitionVersion`, `CanonicalNodeId` → `ContextNode`. |
| `ContextNodeMapping` | Yes | `ContextMappingId` → `ContextMapping`, `ContextNodeId` → `ContextNode`. |
| `ContextUseCaseMapping` | Yes | Record type lookups `ReferenceObjectRecordTypeId` and `TargetObjectRecordTypeId`; `MappingType` is available. |

The observation came from describe calls only; it contains no retrieved
contract, clause, or customer record content. Context Service definitions and
mappings are queryable in this org, but other orgs can expose a different API
surface.

## Relationships represented in the repository ERD

The generated 264 schema at `scripts/erd/schema_diff/264-schema.json` confirms
these relationships for the repository schema snapshot:

| Object | Confirmed relationship fields | What they connect |
|---|---|---|
| `DocumentClauseSet` | `CategoryReferenceId` → `CategoryReference` | A clause set references its `ClauseCatgConfiguration` category. |
| `ObjectStateValue` | `ObjectStateDefinitionId` → `ObjectStateDefinition` | A state value belongs to a state definition. |
| `ObjectStateTransition` | `ObjectStateDefinitionId`, `FromStateId` → `FromState`, `ToStateId` → `ToState` | A transition belongs to a model and connects its source and destination values. |
| `ObjectStateTransitionAction` | `ObjectStateDefinitionId`, `ObjectStateTransitionId` → `ObjectStateTransition`, `ObjectStateActionDefinitionId` → `ObjectStateActionDefinition` | An action is associated with a model and transition. |
| `Contract` | `AccountId` → `Account`, `RecordTypeId` → `RecordType`, `ContractDocumentVersionId` → `ContractDocumentVersion` | Standard contract context plus its CLM document-version lookup. |

The original Revenue Cloud dataset does not describe `ContractType`,
`ContractTypeConfig`, `DocumentClause`, or `DocumentTemplate`; these are now in
the separate Contracts CLM viewer extension. Their absence from the base
dataset was not evidence that an org lacked the objects. The `qb-clm` SFDMU
plan supplies additional field and relationship evidence for the state-model
seed, but it is repository configuration rather than a full org schema contract.

The separate 264 Contracts Developer Guide does document these CLM objects and
their API fields. Use its object pages as release-specific candidates when
choosing what to describe:

| Object | Documented inventory fields | Relationship or access note |
|---|---|---|
| [`ContractType`](../../../docs/salesforce/264/dev-guide-contracts/articles/sforce_api_objects_contracttype.htm.md) | `Name`, `IsDefault`, `SubTypes` | Contract-type configuration object. |
| [`ContractTypeConfig`](../../../docs/salesforce/264/dev-guide-contracts/articles/sforce_api_objects_contracttypeconfig.htm.md) | `ConfigType`, `ConfigValue`, `ContractTypeId`, `UsageType` | `ContractTypeId` relates to `ContractType`. |
| [`DocumentClauseSet`](../../../docs/salesforce/264/dev-guide-contracts/articles/sforce_api_objects_documentclauseset.htm.md) | `Name`, `Status`, `Category`, `CategoryReferenceId`, `DefaultLanguage` | `CategoryReferenceId` relates to `ClauseCatgConfiguration`. |
| [`DocumentClause`](../../../docs/salesforce/264/dev-guide-contracts/articles/sforce_api_objects_documentclause.htm.md) | `Name`, `Status`, `Language`, `Version`, `IsAlternateClause`, `DocumentClauseSetId` | `DocumentClauseSetId` relates to `DocumentClauseSet`; access requires the documented ClauseManagement entitlement. |
| [`DocumentTemplate`](../../../docs/salesforce/264/dev-guide-contracts/articles/sforce_api_objects_documenttemplate.htm.md) | `Name`, `Status`, `IsActive`, `Type`, `UsageType`, `VersionNumber`, `TokenMappingType` | Template records do not prove that related files and generation mappings work. |
| [`ClauseCatgConfiguration`](../../../docs/salesforce/264/dev-guide-contracts/articles/sforce_api_objects_clausecatgconfiguration.htm.md) | `MasterLabel`, `UsageType`, `Description` | Also documented as a Metadata API type; it may need metadata retrieval/deployment rather than SOQL. |

These pages document the 264 API surface, not the target org's effective
permissions, enabled licenses, or API version. Confirm queryability and fields
with the target org's describe before running SOQL.

```bash
# Contract records and their core transaction relationship
sf data query --target-org <sf_alias> --query \
  "SELECT Id, AccountId, Status, StartDate, ContractTerm, IsAssociatedWithClm, ContractDocumentVersionId FROM Contract LIMIT 50"

# Contract types and their per-type settings
sf data query --target-org <sf_alias> --query \
  "SELECT Id, MasterLabel, DeveloperName, IsDefault, SubTypes FROM ContractType LIMIT 50"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, ContractType.Name, ConfigType, ConfigValue, UsageType FROM ContractTypeConfig LIMIT 200"

# Shipped state-model seed records and their transitions
sf data query --target-org <sf_alias> --query \
  "SELECT Id, Name, IsActive, AppUsageType, VersionNumber FROM ObjectStateDefinition LIMIT 50"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, Name, ObjectStateDefinitionId FROM ObjectStateValue LIMIT 100"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, Name, ObjectStateDefinition.Name, FromState.Name, ToState.Name FROM ObjectStateTransition LIMIT 100"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, Name, ObjectStateDefinition.Name, ObjectStateTransition.Name, ObjectStateActionDefinition.Name, DisplaySequence, IsActive FROM ObjectStateTransitionAction LIMIT 100"

# Clause library inventory (describe DocumentClause fields first)
sf data query --target-org <sf_alias> --query \
  "SELECT Id, Name, Status, Category, CategoryReference.DeveloperName, DefaultLanguage FROM DocumentClauseSet LIMIT 100"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, Name, Status, Language, Version, IsAlternateClause, DocumentClauseSet.Name FROM DocumentClause LIMIT 100"

# Template inventory (select only fields returned by describe)
sf data query --target-org <sf_alias> --query \
  "SELECT Id, Name, Status, IsActive, Type, UsageType, VersionNumber, TokenMappingType FROM DocumentTemplate LIMIT 100"

# Context Service shape confirmed in rlm-base__ent_1002; re-describe first
sf data query --target-org <sf_alias> --query \
  "SELECT Id, DeveloperName, MasterLabel FROM ContextDefinition LIMIT 100"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, ContextDefinitionId, IsActive FROM ContextDefinitionVersion LIMIT 100"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, ContextDefinitionVersionId FROM ContextMapping LIMIT 100"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, ContextDefinitionVersionId, CanonicalNodeId FROM ContextNode LIMIT 100"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, ContextMappingId, ContextNodeId FROM ContextNodeMapping LIMIT 100"
sf data query --target-org <sf_alias> --query \
  "SELECT Id, DeveloperName, MasterLabel, MappingType, ReferenceObjectRecordTypeId, TargetObjectRecordTypeId FROM ContextUseCaseMapping LIMIT 100"
```

The 264 schema and Developer Guide confirm the candidate fields shown above,
while the `qb-clm` plan confirms the seeded state and clause-set records. These
sources don't establish that every field is enabled or queryable in every org or
API version. Relationship traversal is appropriate only when the target org's
describe exposes it.

For contract types, settings, context mappings, transition actions, template
sections/tokens, or clause content tokens, describe the corresponding objects
first, then build a narrow `SELECT Id, Name, <verified fields>` query. Start with
the release snapshot and repo metadata to identify relevant API names; do not
guess names from UI labels.

For Context Service, first inspect the repo's context plans and extensions
(`datasets/context_plans/` and the `extend_context_*` / `apply_context_*` tasks in
`cumulusci.yml`). `docs/references/context-definitions/` holds only reference-only,
pre-264 MDAPI snapshots: read them for the old shape, never deploy them. In the org, discover the corresponding queryable SObjects with
`sf sobject list`, describe each candidate, and query only the mapping/config
records and fields that the describe confirms. The connected-org observation
above confirms queryable `ContextDefinition`, `ContextDefinitionVersion`,
`ContextMapping`, `ContextNode`, `ContextNodeMapping`, and
`ContextUseCaseMapping` objects in that org; other orgs may instead require the
supported Metadata or Connect API workflow documented by `context-service`.

## Interpreting results

- Zero rows means the query found no visible matches. Check filters, sharing,
  object permissions, and license-backed access before treating it as absent.
- A query error naming a field means the field is not available to this API
  version or org context, or the API name is wrong. Re-run describe; don't retry
  with guessed variants.
- A missing SObject can reflect feature/edition/license availability or API
  visibility. Compare the org's settings and release-matched Help before deciding.
- A present `DocumentTemplate` record does not prove the binary, related content,
  token mappings, or generation configuration is usable. Inspect those
  relationships and validate by sandbox generation.
- A visible clause set does not prove it contains active clauses in the required
  language or version. Query and validate clauses separately.

For longer investigations, write read-only queries to a temporary file, record
the org alias and API version, and avoid copying contract names, clause bodies,
or customer content into tracked files.
