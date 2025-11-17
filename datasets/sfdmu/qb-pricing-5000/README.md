# QB-Pricing-1000 Dataset

Pricing data for 1000 products (companion to qb-pcm-1000 dataset).

## Contents
- **PricebookEntry**: 3439 price book entries
- **PriceAdjustmentTier**: 90 tiers
- **AttributeBasedAdjustment**: 124 adjustments
- **BundleBasedAdjustment**: 122 bundle adjustments
- **PricebookEntryDerivedPrice**: 60 derived prices
- **Product2**: 4598 products (reference only)

## Key Features

### AttributeBasedAdjRule Scaling
- Creates unique rules for each generated product
- Pattern: Rule_1724814105445-QB-API-GEN0170
- Ensures business rule: all conditions must reference same product

### PriceAdjustmentSchedule Fix
- Schedules are set to INACTIVE to allow tier import
- IMPORTANT: Manually activate schedules after import!

## Post-Import Steps

After importing, activate PriceAdjustmentSchedules via Apex:

```apex
List<PriceAdjustmentSchedule> scheds = [
  SELECT Id FROM PriceAdjustmentSchedule WHERE IsActive = false
];
for (PriceAdjustmentSchedule s : scheds) {
  s.IsActive = true;
}
update scheds;
```
