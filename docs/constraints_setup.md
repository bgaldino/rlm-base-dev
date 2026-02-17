# Constraints Setup and Deployment Order

This document describes the `prepare_constraints` flow, its dependencies, and how constraint model data is loaded. For full details on the CML constraint utility, see the [Constraints Utility Guide](../datasets/constraints/README.md).

## Flow Order (prepare_constraints)

The `prepare_constraints` flow runs nine steps grouped into two phases:

### Phase 1: Metadata Setup (steps 1-4)

These steps run when the `constraints` flag is `true`:

| Step | Task | Condition | Purpose |
|------|------|-----------|---------|
| 1 | `insert_qb_transactionprocessingtypes_data` | `constraints` + `qb` | Load TransactionProcessingType SFDMU records |
| 2 | `deploy_post_constraints` | `constraints` | Deploy constraint-related metadata |
| 3 | `assign_permission_sets` | `tso` + `procedureplans` | Assign constraint permission sets |
| 4 | `apply_context_constraint_engine_node_status` | `constraints` | Apply context attribute mappings |

### Phase 2: Constraint Data Loading (steps 5-9)

These steps run when `constraints_data` is `true` (steps 6-9 also require `qb`):

| Step | Task | Condition | Purpose |
|------|------|-----------|---------|
| 5 | `enable_constraints_settings` | `constraints_data` | Set Default Transaction Type to "Advanced Configurator", set Asset Context for Product Configurator, and enable Constraints Engine toggle via Robot Framework browser automation |
| 6 | `validate_cml` | `constraints_data` + `qb` | Validate CML files against QuantumBitComplete data |
| 7 | `import_cml` (QuantumBitComplete) | `constraints_data` + `qb` | Import the QuantumBitComplete constraint model |
| 8 | `import_cml` (Server2) | `constraints_data` + `qb` | Import the Server2 constraint model |
| 9 | `manage_expression_sets` | `constraints_data` + `qb` | Activate QuantumBitComplete_V1 and Server2_V1 |

**Important:** Phase 2 uses the Python-based CML utility (`tasks/rlm_cml.py`) instead of SFDMU. The old SFDMU constraint data plans (`qb-constraints-product`, `qb-constraints-component`, etc.) are deprecated and archived in `datasets/sfdmu/_archived/`.

## Feature Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `constraints` | `true` | Enable constraint metadata deployment (steps 1-4) |
| `constraints_data` | `true` | Enable constraint data loading and activation (steps 5-9) |
| `qb` | `true` | QuantumBit dataset family gate |

To load constraint data, set `constraints_data: true` in `cumulusci.yml` or override at runtime:

```bash
cci flow run prepare_constraints --org <org> -o constraints_data true
```

## Constraint Model Data Plans

Constraint model data is stored in `datasets/constraints/qb/` with one directory per model:

```
datasets/constraints/qb/
├── QuantumBitComplete/   # 43 ESC records, 22 products
├── Server2/              # 81 ESC records, 41 products
└── README.md             # Detailed CML utility documentation
```

Each directory contains:
- CSV files for ExpressionSet, ExpressionSetDefinitionVersion, ExpressionSetDefinitionContextDefinition, ExpressionSetConstraintObj, Product2, ProductClassification, ProductRelatedComponent
- A `blobs/` subdirectory with the compiled ConstraintModel binary blob

For detailed information on the data plan format, export/import workflows, and polymorphic resolution, see the [Constraints Utility Guide](../datasets/constraints/README.md).

## TransactionProcessingType Data Plan

The data plan for Transaction Processing Types is located at:

- `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes`

It is loaded by `insert_qb_transactionprocessingtypes_data` (step 1) and is required before `deploy_post_constraints`.

If you need to manage TransactionProcessingType records directly (outside the SFDMU plan), use:

```bash
cci task run manage_transaction_processing_types --operation list
```

## post_constraints Metadata

The `unpackaged/post_constraints` bundle contains metadata that must deploy **after** the constraint fields exist. This includes:

- `RLM_QuoteItemTrigger`
- `RC_Asset_Action_Source_Record_Page.flexipage-meta.xml`
- `OrderItem-RLM Order Product Layout.layout-meta.xml`
- `QuoteLineItem-RLM Quote Line Item Layout.layout-meta.xml`
- `RLM_QuantumBit.permissionset-meta.xml` (only field permissions for constraint fields)

This ordering avoids missing field errors during `deploy_full`.

## Context Updates

The `apply_context_constraint_engine_node_status` task (step 4) applies context attribute additions, mappings, and tags for `RLM_SalesTransactionContext`. This includes:

- **SObject attribute mappings** -- standard field-to-context mappings
- **Context-to-context mappings** (`mappingType: CONTEXT`) -- these link the `ConstraintEngineNodeStatus` attribute to another context definition. For CONTEXT-type rules, the task sets `MappedContextDefinition` on the `ContextNodeMapping` sObject directly via the REST API, because the Connect API `PATCH /context-mappings` endpoint silently ignores `mappedContextDefinitionName`. This ensures the UI correctly shows **"Context Definition"** as the Mapping Source. On re-runs, if the attribute mapping already exists but `MappedContextDefinition` is not set, the task detects this and updates it via the sObject API without re-applying node mappings.

For full plan structure, verification output details, and the sObject API workaround, see:

- [Context Service Utility docs](context_service_utility.md)

## Setup Page Automation

Before constraint data can be imported, three Revenue Settings must be configured that cannot be set via Metadata API:

1. **Default Transaction Type** must be set to "Advanced Configurator"
2. **Set Up Asset Context for Product Configurator** must be set (default: `RLM_AssetContext`)
3. **Set Up Configuration Rules and Constraints with Constraints Engine** toggle must be enabled

The `enable_constraints_settings` task (step 5) automates all three using Robot Framework browser automation, following the same pattern as `enable_document_builder_toggle`. It requires the same Robot Framework / SeleniumLibrary / webdriver-manager dependencies (see [Prerequisites](../README.md#installation)).

All values are configurable via `cumulusci.yml` task options:

```yaml
enable_constraints_settings:
  options:
    default_transaction_type: Advanced Configurator
    asset_context: RLM_AssetContext
```

To run manually:
```bash
cci task run enable_constraints_settings --org <org>
```

## Revenue Settings Automation

In addition to the constraints-specific settings above, the `prepare_rlm_org` flow includes two final configuration steps that run after all data/metadata is deployed and before decision table refresh:

### configure_revenue_settings (step 27 of prepare_rlm_org)

Automates general Revenue Settings page configuration via Robot Framework:

- **Pricing Procedure** -- set to `RLM Revenue Management Default Pricing Procedure`
- **Usage Rating Procedure** -- set to `RLM Default Rating Discovery Procedure`
- **Instant Pricing** toggle -- enabled
- **Create Orders Flow** -- set to `RC_CreateOrdersFromQuote`

All values are configurable via `cumulusci.yml` task options.

### reconfigure_pricing_discovery (step 28 of prepare_rlm_org)

Salesforce autoproc creates `Salesforce_Default_Pricing_Discovery_Procedure` in scratch orgs with an incorrect context definition. This Python CCI task performs a deactivate-reconfigure-reactivate cycle via REST API:

1. Deactivates the expression set version
2. Updates the `ExpressionSetDefinitionContextDefinition` junction to point at `RLM_SalesTransactionContext`
3. Sets Rank to `1` and StartDateTime to `2020-01-01T00:00:00.000Z`
4. Reactivates the version

The task is idempotent -- if the context definition is already correct, it skips the update. The repo's metadata version (`Salesforce_Pricing_Discovery_Procedure.expressionSetDefinition-meta.xml`) is in `.forceignore` to avoid deployment conflicts with the autoproc version.

```bash
cci task run reconfigure_pricing_discovery --org <org>
```

## Deprecated Plans

The following SFDMU constraint data plans are deprecated and archived:

- `datasets/sfdmu/_archived/qb-constraints-product/`
- `datasets/sfdmu/_archived/qb-constraints-component/`
- `datasets/sfdmu/_archived/qb-constraints-consolidated/`
- `datasets/sfdmu/_archived/qb-constraints-prc-aisummit/`

These were early attempts at loading constraint data via SFDMU that could not handle the polymorphic `ReferenceObjectId` field on `ExpressionSetConstraintObj`. They have been replaced by the CML utility.
