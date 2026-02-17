# Constraints Setup and Deployment Order

This document describes the `prepare_constraints` flow, its dependencies, and how constraint model data is loaded. For full details on the CML constraint utility, see the [Constraints Utility Guide](../datasets/constraints/README.md).

## Flow Order (prepare_constraints)

The `prepare_constraints` flow runs eight steps grouped into two phases:

### Phase 1: Metadata Setup (steps 1-4)

These steps run when the `constraints` flag is `true`:

| Step | Task | Condition | Purpose |
|------|------|-----------|---------|
| 1 | `insert_qb_transactionprocessingtypes_data` | `constraints` + `qb` | Load TransactionProcessingType SFDMU records |
| 2 | `deploy_post_constraints` | `constraints` | Deploy constraint-related metadata |
| 3 | `assign_permission_sets` | `tso` + `procedureplans` | Assign constraint permission sets |
| 4 | `apply_context_constraint_engine_node_status` | `constraints` | Apply context attribute mappings |

### Phase 2: Constraint Data Loading (steps 5-8)

These steps run when both `constraints_data` and `qb` flags are `true`:

| Step | Task | Condition | Purpose |
|------|------|-----------|---------|
| 5 | `validate_cml` | `constraints_data` + `qb` | Validate CML files against QuantumBitComplete data |
| 6 | `import_cml` (QuantumBitComplete) | `constraints_data` + `qb` | Import the QuantumBitComplete constraint model |
| 7 | `import_cml` (Server2) | `constraints_data` + `qb` | Import the Server2 constraint model |
| 8 | `manage_expression_sets` | `constraints_data` + `qb` | Activate QuantumBitComplete_V1 and Server2_V1 |

**Important:** Phase 2 uses the Python-based CML utility (`tasks/rlm_cml.py`) instead of SFDMU. The old SFDMU constraint data plans (`qb-constraints-product`, `qb-constraints-component`, etc.) are deprecated and archived in `datasets/sfdmu/_archived/`.

## Feature Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `constraints` | `true` | Enable constraint metadata deployment (steps 1-4) |
| `constraints_data` | `false` | Enable constraint data loading and activation (steps 5-8) |
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

The `apply_context_constraint_engine_node_status` task applies context attribute additions, mappings, and tags for `RLM_SalesTransactionContext`. For plan structure and verification output details, see:

- [Context Service Utility docs](context_service_utility.md)

## Setup Page Toggles (Planned)

Certain constraint features require toggles on the Salesforce Setup page that cannot be set through Metadata API. A Robot Framework task (similar to `enable_document_builder_toggle`) is planned to automate these toggles. This will be integrated as an additional step in `prepare_constraints` once implemented.

## Deprecated Plans

The following SFDMU constraint data plans are deprecated and archived:

- `datasets/sfdmu/_archived/qb-constraints-product/`
- `datasets/sfdmu/_archived/qb-constraints-component/`
- `datasets/sfdmu/_archived/qb-constraints-consolidated/`
- `datasets/sfdmu/_archived/qb-constraints-prc-aisummit/`

These were early attempts at loading constraint data via SFDMU that could not handle the polymorphic `ReferenceObjectId` field on `ExpressionSetConstraintObj`. They have been replaced by the CML utility.
