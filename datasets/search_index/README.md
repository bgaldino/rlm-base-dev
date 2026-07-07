# PCM Search Index Configuration

Declarative JSON configuration files for the Product Catalog Management (PCM)
search index.  Each file specifies which fields should be searchable and/or
facetable.  The `configure_search_index` CCI task reads a file and applies it
to an org via the Connect API (`PUT /connect/pcm/index/configurations`).

## Directory Convention

One JSON file per feature or use-case:

| File | Feature | Flow Step |
|------|---------|-----------|
| `guidedselling.json` | Guided Selling Product2 fields | `prepare_guidedselling` step 5 |

To add index fields for a new feature, create a new JSON file here and wire
it into the appropriate flow step with `options: {path: datasets/search_index/<file>.json}`.

## JSON Schema

```json
{
  "mode": "additive",
  "indexConfigurations": [
    {
      "name": "FieldApiName",
      "isSearchable": true,
      "isFacetable": false,
      "facetDisplayRank": 1,
      "type": "Custom"
    }
  ]
}
```

### Top-level fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `mode` | No | `additive` | `additive` merges into existing config. `replace` makes this file the full desired state (anything not listed is removed). |
| `indexConfigurations` | Yes | — | Array of field entries. |

### Entry fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Field API name (e.g., `Family`, `RLM_Timeline__c`). |
| `isSearchable` | No (default `true`) | Whether the field is full-text searchable. |
| `isFacetable` | No (default `false`) | Whether the field appears as a filter facet in product discovery. |
| `facetDisplayRank` | No | Integer display order for facets. Only meaningful when `isFacetable: true`. |
| `type` | No | Disambiguation hint when the same name exists in multiple object types. Omit unless needed. |

### Supported field types (auto-resolved from API metadata)

| Type | Source Object | ID Resolution |
|------|--------------|---------------|
| `Standard` | Product2 | None needed |
| `Custom` | Product2 | `attributeFieldId` resolved from metadata `customFieldId` |
| `ProductDynamicAttribute` | Product2 (dynamic attributes) | `attributeDefinitionId` resolved from metadata |
| `ProductAttributeDefinitionStandard` | ProductAttributeDefinition | None needed |
| `ProductAttributeDefinitionCustom` | ProductAttributeDefinition | `attributeFieldId` resolved from metadata |

Type and ID resolution is automatic — only `name` is required in the config.
Use the optional `type` field only to disambiguate when a field name exists
in both Product2 and ProductAttributeDefinition (e.g., `Name`).

## Usage

```bash
# Apply guided selling index config
cci task run configure_search_index -o path datasets/search_index/guidedselling.json --org beta

# Replace mode (config = full desired state)
cci task run configure_search_index -o path datasets/search_index/guidedselling.json -o mode replace --org beta
```

## Prerequisites

Target fields must be deployed to the org before running `configure_search_index`.
The task reads available fields from the API metadata response — fields that
don't exist yet will cause an error.

After configuring index fields, run `rebuild_search_index` to build the index
with the new fields included (this happens automatically in `prepare_rlm_org`
step 34).
