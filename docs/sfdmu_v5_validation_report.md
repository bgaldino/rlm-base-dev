# SFDMU v5 Dataset Validation Report

**Generated:** 2026-03-02 18:17:43

## Summary

- **Total datasets validated:** 30
- **Passed:** 21
- **Failed:** 9
- **Total objects validated:** 293
- **Total issues found:** 39

### Issues by Severity

| Severity | Count |
|----------|-------|
| Critical | 17 |
| High | 22 |
| Medium | 0 |
| Info | 0 |

## Dataset Results

### ✅ PASS _archived/qb-constraints-component

- **Path:** `datasets/sfdmu/_archived/qb-constraints-component`
- **Objects validated:** 1
- **Issues found:** 0

### ❌ FAIL _archived/qb-constraints-consolidated

- **Path:** `datasets/sfdmu/_archived/qb-constraints-consolidated`
- **Objects validated:** 5
- **Issues found:** 5

#### Critical Issues (5)

- **Product2**: CSV file not found: Product2.csv (datasets/sfdmu/_archived/qb-constraints-consolidated/Product2.csv)
- **ProductClassification**: CSV file not found: ProductClassification.csv (datasets/sfdmu/_archived/qb-constraints-consolidated/ProductClassification.csv)
- **ProductRelatedComponent**: CSV file not found: ProductRelatedComponent.csv (datasets/sfdmu/_archived/qb-constraints-consolidated/ProductRelatedComponent.csv)
- **ExpressionSet**: CSV file not found: ExpressionSet.csv (datasets/sfdmu/_archived/qb-constraints-consolidated/ExpressionSet.csv)
- **ExpressionSetConstraintObj**: CSV file not found: ExpressionSetConstraintObj.csv (datasets/sfdmu/_archived/qb-constraints-consolidated/ExpressionSetConstraintObj.csv)

### ✅ PASS _archived/qb-constraints-prc-aisummit

- **Path:** `datasets/sfdmu/_archived/qb-constraints-prc-aisummit`
- **Objects validated:** 3
- **Issues found:** 0

### ✅ PASS _archived/qb-constraints-product

- **Path:** `datasets/sfdmu/_archived/qb-constraints-product`
- **Objects validated:** 2
- **Issues found:** 0

### ✅ PASS mfg/en-US/mfg-configflow

- **Path:** `datasets/sfdmu/mfg/en-US/mfg-configflow`
- **Objects validated:** 2
- **Issues found:** 0

### ✅ PASS mfg/en-US/mfg-constraints-p

- **Path:** `datasets/sfdmu/mfg/en-US/mfg-constraints-p`
- **Objects validated:** 1
- **Issues found:** 0

### ✅ PASS mfg/en-US/mfg-constraints-prc

- **Path:** `datasets/sfdmu/mfg/en-US/mfg-constraints-prc`
- **Objects validated:** 1
- **Issues found:** 0

### ❌ FAIL mfg/en-US/mfg-multicurrency

- **Path:** `datasets/sfdmu/mfg/en-US/mfg-multicurrency`
- **Objects validated:** 35
- **Issues found:** 7

#### High Issues (7)

- **ProductRelComponentOverride**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/mfg/en-US/mfg-multicurrency/ProductRelComponentOverride.csv)
- **CostBook**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/mfg/en-US/mfg-multicurrency/CostBook.csv)
- **PriceAdjustmentTier**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/mfg/en-US/mfg-multicurrency/PriceAdjustmentTier.csv)
- **BundleBasedAdjustment**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/mfg/en-US/mfg-multicurrency/BundleBasedAdjustment.csv)
- **PricebookEntryDerivedPrice**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/mfg/en-US/mfg-multicurrency/PricebookEntryDerivedPrice.csv)
- **CostBookEntry**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/mfg/en-US/mfg-multicurrency/CostBookEntry.csv)
- **ProductRampSegment**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/mfg/en-US/mfg-multicurrency/ProductRampSegment.csv)

### ❌ FAIL procedure-plans

- **Path:** `datasets/sfdmu/procedure-plans`
- **Objects validated:** 5
- **Issues found:** 2

#### Critical Issues (2)

- **ExpressionSetDefinition**: CSV file not found: ExpressionSetDefinition.csv (datasets/sfdmu/procedure-plans/ExpressionSetDefinition.csv)
- **ProcedurePlanOption**: CSV file not found: ProcedurePlanOption.csv (datasets/sfdmu/procedure-plans/ProcedurePlanOption.csv)

### ✅ PASS q3/en-US/q3-billing

- **Path:** `datasets/sfdmu/q3/en-US/q3-billing`
- **Objects validated:** 11
- **Issues found:** 0

### ❌ FAIL q3/en-US/q3-dro

- **Path:** `datasets/sfdmu/q3/en-US/q3-dro`
- **Objects validated:** 10
- **Issues found:** 10

#### Critical Issues (10)

- **FulfillmentWorkspace**: CSV file not found: FulfillmentWorkspace.csv (datasets/sfdmu/q3/en-US/q3-dro/FulfillmentWorkspace.csv)
- **FulfillmentStepDefinitionGroup**: CSV file not found: FulfillmentStepDefinitionGroup.csv (datasets/sfdmu/q3/en-US/q3-dro/FulfillmentStepDefinitionGroup.csv)
- **FulfillmentFalloutRule**: CSV file not found: FulfillmentFalloutRule.csv (datasets/sfdmu/q3/en-US/q3-dro/FulfillmentFalloutRule.csv)
- **FulfillmentStepJeopardyRule**: CSV file not found: FulfillmentStepJeopardyRule.csv (datasets/sfdmu/q3/en-US/q3-dro/FulfillmentStepJeopardyRule.csv)
- **FulfillmentStepDefinition**: CSV file not found: FulfillmentStepDefinition.csv (datasets/sfdmu/q3/en-US/q3-dro/FulfillmentStepDefinition.csv)
- **FulfillmentStepDependencyDef**: CSV file not found: FulfillmentStepDependencyDef.csv (datasets/sfdmu/q3/en-US/q3-dro/FulfillmentStepDependencyDef.csv)
- **FulfillmentWorkspaceItem**: CSV file not found: FulfillmentWorkspaceItem.csv (datasets/sfdmu/q3/en-US/q3-dro/FulfillmentWorkspaceItem.csv)
- **ProductFulfillmentDecompRule**: CSV file not found: ProductFulfillmentDecompRule.csv (datasets/sfdmu/q3/en-US/q3-dro/ProductFulfillmentDecompRule.csv)
- **ProductFulfillmentScenario**: CSV file not found: ProductFulfillmentScenario.csv (datasets/sfdmu/q3/en-US/q3-dro/ProductFulfillmentScenario.csv)
- **Product2**: CSV file not found: Product2.csv (datasets/sfdmu/q3/en-US/q3-dro/Product2.csv)

### ❌ FAIL q3/en-US/q3-multicurrency

- **Path:** `datasets/sfdmu/q3/en-US/q3-multicurrency`
- **Objects validated:** 34
- **Issues found:** 4

#### High Issues (4)

- **ProductRelComponentOverride**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/q3/en-US/q3-multicurrency/ProductRelComponentOverride.csv)
- **CostBook**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/q3/en-US/q3-multicurrency/CostBook.csv)
- **PriceAdjustmentTier**: CSV missing composite key column '$$PriceAdjustmentSchedule.Name$Product2.StockKeepingUnit$ProductSellingModel.Name$TierType$TierValue$UpperBound$LowerBound$CurrencyIsoCode' for externalId 'PriceAdjustmentSchedule.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;TierType;TierValue;UpperBound;LowerBound;CurrencyIsoCode'. This will break re-import idempotency in SFDMU v5. (datasets/sfdmu/q3/en-US/q3-multicurrency/PriceAdjustmentTier.csv)
- **CostBookEntry**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/q3/en-US/q3-multicurrency/CostBookEntry.csv)

### ✅ PASS q3/en-US/q3-rates

- **Path:** `datasets/sfdmu/q3/en-US/q3-rates`
- **Objects validated:** 5
- **Issues found:** 0

### ❌ FAIL q3/en-US/q3-rating

- **Path:** `datasets/sfdmu/q3/en-US/q3-rating`
- **Objects validated:** 9
- **Issues found:** 1

#### High Issues (1)

- **UsagePrdGrantBindingPolicy**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/q3/en-US/q3-rating/UsagePrdGrantBindingPolicy.csv)

### ✅ PASS q3/en-US/q3-tax

- **Path:** `datasets/sfdmu/q3/en-US/q3-tax`
- **Objects validated:** 6
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-accounting

- **Path:** `datasets/sfdmu/qb/en-US/qb-accounting`
- **Objects validated:** 4
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-billing

- **Path:** `datasets/sfdmu/qb/en-US/qb-billing`
- **Objects validated:** 11
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-clm

- **Path:** `datasets/sfdmu/qb/en-US/qb-clm`
- **Objects validated:** 7
- **Issues found:** 0

### ❌ FAIL qb/en-US/qb-dro

- **Path:** `datasets/sfdmu/qb/en-US/qb-dro`
- **Objects validated:** 14
- **Issues found:** 4

#### High Issues (4)

- **ValTfrmGrp**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/qb/en-US/qb-dro/ValTfrmGrp.csv)
- **ValTfrm**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/qb/en-US/qb-dro/ValTfrm.csv)
- **FulfillmentWorkspaceItem**: CSV missing composite key column '$$FulfillmentWorkspace.Name$FulfillmentStepDefinitionGroup.Name' for externalId 'FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name'. This will break re-import idempotency in SFDMU v5. (datasets/sfdmu/qb/en-US/qb-dro/FulfillmentWorkspaceItem.csv)
- **FulfillmentTaskAssignmentRule**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/qb/en-US/qb-dro/FulfillmentTaskAssignmentRule.csv)

### ✅ PASS qb/en-US/qb-guidedselling

- **Path:** `datasets/sfdmu/qb/en-US/qb-guidedselling`
- **Objects validated:** 10
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-pcm

- **Path:** `datasets/sfdmu/qb/en-US/qb-pcm`
- **Objects validated:** 28
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-pricing

- **Path:** `datasets/sfdmu/qb/en-US/qb-pricing`
- **Objects validated:** 16
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-product-images

- **Path:** `datasets/sfdmu/qb/en-US/qb-product-images`
- **Objects validated:** 1
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-rates

- **Path:** `datasets/sfdmu/qb/en-US/qb-rates`
- **Objects validated:** 5
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-rating

- **Path:** `datasets/sfdmu/qb/en-US/qb-rating`
- **Objects validated:** 14
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-tax

- **Path:** `datasets/sfdmu/qb/en-US/qb-tax`
- **Objects validated:** 6
- **Issues found:** 0

### ✅ PASS qb/en-US/qb-transactionprocessingtypes

- **Path:** `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes`
- **Objects validated:** 1
- **Issues found:** 0

### ❌ FAIL qb/ja/qb-pcm

- **Path:** `datasets/sfdmu/qb/ja/qb-pcm`
- **Objects validated:** 28
- **Issues found:** 4

#### High Issues (4)

- **ProductQualification**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/qb/ja/qb-pcm/ProductQualification.csv)
- **ProductDisqualification**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/qb/ja/qb-pcm/ProductDisqualification.csv)
- **ProductCategoryDisqual**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/qb/ja/qb-pcm/ProductCategoryDisqual.csv)
- **ProductCategoryQualification**: CSV file is completely empty (no header row). Add header row with fields from query. (datasets/sfdmu/qb/ja/qb-pcm/ProductCategoryQualification.csv)

### ❌ FAIL qb/ja/qb-pricing

- **Path:** `datasets/sfdmu/qb/ja/qb-pricing`
- **Objects validated:** 16
- **Issues found:** 2

#### High Issues (2)

- **PriceAdjustmentTier**: CSV missing composite key column '$$PriceAdjustmentSchedule.Name$Product2.StockKeepingUnit$ProductSellingModel.Name$TierType$TierValue$UpperBound$LowerBound$CurrencyIsoCode' for externalId 'PriceAdjustmentSchedule.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;TierType;TierValue;UpperBound;LowerBound;CurrencyIsoCode'. This will break re-import idempotency in SFDMU v5. (datasets/sfdmu/qb/ja/qb-pricing/PriceAdjustmentTier.csv)
- **PricebookEntry**: CSV missing composite key column '$$Name$Product2.StockKeepingUnit$ProductSellingModel.Name$CurrencyIsoCode' for externalId 'Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode'. This will break re-import idempotency in SFDMU v5. (datasets/sfdmu/qb/ja/qb-pricing/PricebookEntry.csv)

### ✅ PASS scratch_data

- **Path:** `datasets/sfdmu/scratch_data`
- **Objects validated:** 2
- **Issues found:** 0
