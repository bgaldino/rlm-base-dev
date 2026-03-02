# SFDMU v5 Dataset Validation Report

**Generated:** 2026-03-02 17:31:38

## Summary

- **Total datasets validated:** 14
- **Passed:** 11
- **Failed:** 3
- **Total objects validated:** 161
- **Total issues found:** 10

### Issues by Severity

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 10 |
| Medium | 0 |
| Info | 0 |

## Dataset Results

### ✅ PASS qb/en-US/qb-accounting

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-accounting`
- **Objects validated:** 4
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-billing

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-billing`
- **Objects validated:** 11
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-clm

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-clm`
- **Objects validated:** 7
- **Issues found:** 0

### ❌ FAIL qb/en-US/qb-dro

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-dro`
- **Objects validated:** 14
- **Issues found:** 4

#### High Issues (4)

- **ValTfrmGrp**: CSV file is completely empty (no header row). Add header row with fields from query. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-dro/ValTfrmGrp.csv)
- **ValTfrm**: CSV file is completely empty (no header row). Add header row with fields from query. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-dro/ValTfrm.csv)
- **FulfillmentWorkspaceItem**: CSV missing composite key column '$$FulfillmentWorkspace.Name$FulfillmentStepDefinitionGroup.Name' for externalId 'FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name'. This will break re-import idempotency in SFDMU v5. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-dro/FulfillmentWorkspaceItem.csv)
- **FulfillmentTaskAssignmentRule**: CSV file is completely empty (no header row). Add header row with fields from query. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-dro/FulfillmentTaskAssignmentRule.csv)

### ✅ PASS qb/en-US/qb-guidedselling

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-guidedselling`
- **Objects validated:** 10
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-pcm

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-pcm`
- **Objects validated:** 28
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-pricing

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-pricing`
- **Objects validated:** 16
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-product-images

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-product-images`
- **Objects validated:** 1
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-rates

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-rates`
- **Objects validated:** 5
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-rating

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-rating`
- **Objects validated:** 14
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-tax

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-tax`
- **Objects validated:** 6
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-transactionprocessingtypes

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes`
- **Objects validated:** 1
- **Issues found:** 0

### ❌ FAIL qb/ja/qb-pcm

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/ja/qb-pcm`
- **Objects validated:** 28
- **Issues found:** 4

#### High Issues (4)

- **ProductQualification**: CSV file is completely empty (no header row). Add header row with fields from query. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/ja/qb-pcm/ProductQualification.csv)
- **ProductDisqualification**: CSV file is completely empty (no header row). Add header row with fields from query. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/ja/qb-pcm/ProductDisqualification.csv)
- **ProductCategoryDisqual**: CSV file is completely empty (no header row). Add header row with fields from query. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/ja/qb-pcm/ProductCategoryDisqual.csv)
- **ProductCategoryQualification**: CSV file is completely empty (no header row). Add header row with fields from query. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/ja/qb-pcm/ProductCategoryQualification.csv)

### ❌ FAIL qb/ja/qb-pricing

- **Path:** `/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/ja/qb-pricing`
- **Objects validated:** 16
- **Issues found:** 2

#### High Issues (2)

- **PriceAdjustmentTier**: CSV missing composite key column '$$PriceAdjustmentSchedule.Name$Product2.StockKeepingUnit$ProductSellingModel.Name$TierType$TierValue$UpperBound$LowerBound$CurrencyIsoCode' for externalId 'PriceAdjustmentSchedule.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;TierType;TierValue;UpperBound;LowerBound;CurrencyIsoCode'. This will break re-import idempotency in SFDMU v5. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/ja/qb-pricing/PriceAdjustmentTier.csv)
- **PricebookEntry**: CSV missing composite key column '$$Name$Product2.StockKeepingUnit$ProductSellingModel.Name$CurrencyIsoCode' for externalId 'Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode'. This will break re-import idempotency in SFDMU v5. (/Users/scheck/Code/rlm-base-dev/datasets/sfdmu/qb/ja/qb-pricing/PricebookEntry.csv)
