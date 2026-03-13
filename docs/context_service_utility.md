## Context Service Utility

This utility updates Context Definitions using the Context Service `connect` APIs. It supports creating attributes and tags, creating context mappings, and applying mapping rules (including context-to-context mappings) without deactivating the definition by default.

### Task

`manage_context_definition` in `tasks/rlm_context_service.py`

### Default Behavior

- Uses the **default CCI org** unless a `context_definition_id` is provided.
- **Does not deactivate** the context definition before updates unless explicitly requested.
- Applies SObject mappings before context-to-context mappings so IDs are available.

### Options

- `context_definition_id` (optional): ContextDefinitionId to modify.
- `developer_name` (optional): DeveloperName of the context definition.
- `plan_file` (required): Path to JSON plan file (single plan or manifest).
- `activate` (optional): Activate the context definition after updates.
- `dry_run` (optional): Log intended requests without executing.
- `deactivate_before` (optional): Deactivate definition before updates (default: false).
- `validate_only` (optional): Validate plan without updating.
- `translate_plan` (optional): Translate `mappingRules` into update payloads (default: true).
- `verify` (optional): Log verification details after updates.

### Creating a New Context Definition

Set `"create": true` in the plan file to create a new context definition when it does not already exist. Required plan fields: `developerName`, `label`. If the definition already exists, the create flag is ignored and the standard update flow runs instead.

Additional plan fields for creation:
- `label` (required): Display name of the definition.
- `primaryDomainObject` (optional): Primary SObject API name for the CS create endpoint (e.g. `"Quote"`). Note: `primaryObject` is not a valid API field — use `primaryDomainObject`.
- `description` (optional): Description.
- `startDate` (optional): Effective start date.
- `contextTtl` (optional): Time-to-live.
- `baseReference` (optional): Standard context base reference for extension definitions.
- `createPayload` (optional): Object whose keys are merged directly into the creation POST body (for API fields not covered above).

Node hierarchy for new definitions uses `contextNodeDefinitions` (instead of `contextNodes`). Each entry supports `parentNodeName` to reference a previously created parent node by name:

```json
"contextNodeDefinitions": [
  { "name": "Quote", "label": "Quote" },
  { "name": "QuoteLineItem", "label": "Quote Line Item", "parentNodeName": "Quote" }
]
```

The create flow runs in the correct order: nodes → mappings → re-fetch → attributes → mapping rules → tags → activate.

**Example — create dedicated DocGen context:**

```bash
cci task run apply_context_docgen
```

Or via `manage_context_definition`:

```bash
cci task run manage_context_definition \
  -o plan_file datasets/context_plans/DocGen/manifest.json \
  -o translate_plan true \
  -o activate true \
  -o verify true
```

### Plan File Structure

You can provide either:

1. A single plan JSON with `developerName` and payloads.
2. A manifest with a `contexts` list that points to plan files.

For multi-plan usage, each plan lives in its own folder:

```
datasets/context_plans/<PlanName>/
  manifest.json
  contexts/<plan>.json
```

#### Manifest Example

```json
{
  "contexts": [
    {
      "developerName": "RLM_SalesTransactionContext",
      "planFile": "contexts/constraint_engine_node_status.json"
    }
  ]
}
```

#### Plan Example (Core Fields)

```json
{
  "developerName": "RLM_SalesTransactionContext",
  "contextAttributesByName": [
    {
      "nodeName": "SalesTransactionItem",
      "name": "ConstraintEngineNodeStatus__c",
      "dataType": "STRING",
      "fieldType": "INPUTOUTPUT"
    }
  ],
  "contextTagsByName": [
    {
      "nodeName": "SalesTransactionItem",
      "attributeName": "ConstraintEngineNodeStatus__c",
      "name": "ConstraintEngineNodeStatus__c"
    }
  ],
  "mappingRules": [
    {
      "mappingName": "QuoteEntitiesMapping",
      "contextNode": "SalesTransactionItem",
      "contextAttribute": "ConstraintEngineNodeStatus__c",
      "mappingType": "SOBJECT",
      "sObject": "QuoteLineItem",
      "sObjectField": "RLM_ConstraintEngineNodeStatus__c"
    }
  ],
  "contextMappingUpdates": {
    "contextMappings": [
      {
        "name": "QuoteEntitiesMapping",
        "isDefault": true
      }
    ]
  },
  "activate": true
}
```

### Mapping Rules

`mappingRules` are translated into Context Service update payloads. The utility:

- Applies SObject mappings first.
- Applies context-to-context mappings after SObject mappings.
- Uses `context-mappings/{contextMappingId}/context-node-mappings` for node mapping updates.

#### SObject Mapping Rule

```json
{
  "mappingName": "OrderEntitiesMapping",
  "contextNode": "SalesTransactionItem",
  "contextAttribute": "ConstraintEngineNodeStatus__c",
  "mappingType": "SOBJECT",
  "sObject": "OrderItem",
  "sObjectField": "RLM_ConstraintEngineNodeStatus__c"
}
```

#### Context-to-Context Mapping Rule

```json
{
  "mappingName": "AssetToSalesTransactionMapping",
  "contextNode": "SalesTransactionItem",
  "contextAttribute": "ConstraintEngineNodeStatus__c",
  "mappingType": "CONTEXT",
  "sourceContextNode": "AssetActionSource",
  "sourceContextAttribute": "AssetConstraintEngineNodeStatus__c"
}
```

When `mappingType` is `CONTEXT`, the utility:

1. Sets `mappedContextNodeId` on the node mapping to point to the source context node.
2. Adds `contextAttrContextHydrationDetails` with the source attribute and parent mapping IDs.
3. Sets `MappedContextDefinition` on the `ContextNodeMapping` sObject record to the context definition's developer name (e.g. `RLM_SalesTransactionContext`). This makes the UI show **"Context Definition"** as the Mapping Source. The Connect API `PATCH /context-mappings` endpoint silently ignores `mappedContextDefinitionName`, so the task uses the sObject REST API (`PATCH /sobjects/ContextNodeMapping/{id}`) to set this field.

### Verification Mode

Set `verify` to log the key changes after updates:

- Mapping rule rows found (mapping, node, sObject, attribute, hydration detail presence).
- Attributes created by `contextAttributesByName`.
- Tags created by `contextTagsByName`.

### Examples

Run with the default CCI org:

```bash
cci task run manage_context_definition \
  -o plan_file datasets/context_plans/ConstraintEngineNodeStatus/manifest.json \
  -o developer_name RLM_SalesTransactionContext \
  -o translate_plan true \
  -o activate true \
  -o deactivate_before false \
  -o verify true
```

Validate only:

```bash
cci task run manage_context_definition \
  -o plan_file datasets/context_plans/ConstraintEngineNodeStatus/manifest.json \
  -o developer_name RLM_SalesTransactionContext \
  -o validate_only true
```

### Archive

Legacy plans are archived under `datasets/context_plans/archive` and are not referenced by flows.

### Notes

- The task skips updates for `TransactionType` because those mappings are inherited.
- Tag names for custom artifacts must end with `__c` in extended definitions.
- For `CONTEXT`-type mapping rules, the task sets `MappedContextDefinition` on the `ContextNodeMapping` sObject directly (via the REST API) because the Connect API `context-mappings` PATCH silently ignores the `mappedContextDefinitionName` field. On re-runs, if the attribute mapping already exists but `MappedContextDefinition` is not set, the task detects this and updates it.
