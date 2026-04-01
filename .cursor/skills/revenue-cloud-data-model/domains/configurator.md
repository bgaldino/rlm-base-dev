# Configurator Domain

4 objects managing product configuration rules and flow assignments.

## Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `ProductConfigurationFlow` | Flow controlling product configuration UX | ReferenceObjectId (→ Product2) |
| `ProductConfigurationRule` | Validation/constraint rules for product configuration | ProductId (→ Product2) |
| `ProductConfigFlowAssignment` | Assigns configuration flows to contexts | — |
| `ExpressionSetConstraintObj` | Links expression set constraints to configuration | — |

## Key Relationships

```
Product2 ← ProductConfigurationFlow (ReferenceObjectId)
Product2 ← ProductConfigurationRule (ProductId)
```

## Notes

- Configuration rules use Expression Sets and CML (Constraint Markup Language) for validation logic
- TransactionProcessingType objects (separate data plan: `qb-transactionprocessingtypes`) define which constraint types are active
- Configuration flows are typically assigned per-product or per-classification
- The Configurator domain works closely with PCM (product bundles, component groups) and Pricing (valid selling model options)
