# Constraints Setup and Deployment Order

This document captures the current constraints deployment ordering and related data plans. It is meant to align the `prepare_constraints` flow with its dependencies.

## Flow Order (prepare_constraints)

The `prepare_constraints` flow runs in this order:

1. `insert_qb_transactionprocessingtypes_data` (QuantumBit only)
2. `deploy_post_constraints`
3. `apply_context_constraint_engine_node_status`
4. `insert_qb_constraints_product_data` (currently disabled)
5. `insert_qb_constraints_component_data` (currently disabled)

This order ensures TransactionProcessingType records exist before constraint metadata deploys, and context updates run after the relevant metadata is available.

## TransactionProcessingType Data Plan

The data plan for Transaction Processing Types is located at:

- `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes`

It is loaded by `insert_qb_transactionprocessingtypes_data` and is required before `deploy_post_constraints`.

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

- `docs/context_service_utility.md`
