# qb-guidedselling-products Data Plan

SFDMU data plan for QuantumBit guided-selling Product2 field values. This plan decorates existing products loaded by `qb-pcm` with the product-discovery attributes used by the guided selling experience.

## CCI Integration

### Flow: `prepare_guidedselling`

This plan is executed after `deploy_post_guidedselling` so the `RLM_` Product2 fields exist before data load. It is gated by the `guidedselling` and `qb` feature flags.

### Task Definition

```yaml
insert_qb_guidedselling_products_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-guidedselling-products"
```

## Data Plan Overview

The plan uses a single SFDMU pass with one Update-only Product2 object. No records are created; existing products are matched by `StockKeepingUnit` and updated with guided-selling attributes.

## Objects

| # | Object | Operation | External ID | Records |
|---|--------|-----------|-------------|---------|
| 1 | Product2 | Update | `StockKeepingUnit` | 3 |

## Fields Updated

- `RLM_Primary_Goal__c` - restricted multiselect picklist
- `RLM_Timeline__c` - restricted picklist
- `RLM_Platform_Control__c` - restricted picklist

## Dependencies

**Upstream:**
- `qb-pcm` - Product2 records must already exist and be matchable by `StockKeepingUnit`.
- `deploy_post_guidedselling` - deploys the three Product2 fields before this data plan runs.

**Downstream:**
- Guided selling Product Discovery experience uses these values for product qualification.

## Notes

This plan intentionally does not import OmniStudio data from `qb-guidedselling`. Product Discovery settings differences from the connected org and deeper `qb-guidedselling` OmniStudio data redesign are tracked as follow-up work and are not included here.
