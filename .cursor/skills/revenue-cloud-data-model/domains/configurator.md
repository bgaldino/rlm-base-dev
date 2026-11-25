# Configurator Domain

4 objects managing product configuration rules and flow assignments.

## Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `ProductConfigurationFlow` | Flow controlling product configuration UX | Name, FlowIdentifier, IsDefault, Status, Type, SubType, Sequence, AssociatedProcessId (→ ApexClass) |
| `ProductConfigurationRule` | Validation/constraint rules for product configuration | Name, ApiName, RuleType, RuleSubType, Status, ProcessScope, Sequence |
| `ProductConfigFlowAssignment` | Assigns a configuration flow to a product or classification | ProductConfigurationFlowId, ProductId, ProductClassificationId, AssignmentType |
| `ExpressionSetConstraintObj` | Links an expression set (constraint model) to a product, classification or component | ExpressionSetId, ReferenceObjectId (→ Product2, ProductClassification or ProductRelatedComponent), ConstraintModelTag, ConstraintModelTagType |

## Key Relationships

```
ProductConfigurationFlow ← ProductConfigFlowAssignment (ProductConfigurationFlowId)
Product2 ← ProductConfigFlowAssignment (ProductId)
ProductClassification ← ProductConfigFlowAssignment (ProductClassificationId)
ExpressionSet ← ExpressionSetConstraintObj (ExpressionSetId)
Product2 ← ExpressionSetConstraintObj (ReferenceObjectId, polymorphic)
```

## Notes

- Configuration rules use Expression Sets and CML (Constraint Markup Language) for validation logic
- TransactionProcessingType objects (separate data plan: `qb-transactionprocessingtypes`) define which constraint types are active
- Configuration flows are typically assigned per-product or per-classification
- The Configurator domain works closely with PCM (product bundles, component groups) and Pricing (valid selling model options)
