/*
This script activates Price Adjustment Schedules if not activated - courtesy of QBranch

'Standard Price Adjustment Tier' (the qb volume schedule) is deliberately NOT activated.
The platform rejects any PriceAdjustmentTier insert, update or delete while that schedule
is active. A reload no longer deletes tiers, but a new or corrected tier is still written,
so activating it here would make a prepare_rlm_org rerun fail to load them. The pricing
plans keep it inactive, and its tiers still price. See datasets/sfdmu/qb/en-US/qb-pricing/README.md.
It doesn't activate 'Standard Tier Based Adjustment' or 'Standard Volume Based Adjustment'
either: no pricing procedure reads them, and the q3 tiers moved to 'Standard Price
Adjustment Tier' (todo 319). Known exception: qb/ja's pricing plan declares its Volume
schedule active itself, so a ja reload is still exposed to that rejection (todo 212).
*/
    List<PriceAdjustmentSchedule> recordsToUpdate = [SELECT Id
                                             FROM PriceAdjustmentSchedule
                                             WHERE Name IN ('Standard Attribute Based Adjustment','Standard Bundle Based Adjustment') and IsActive = false];

    // Check if there are records to delete
    if (!recordsToUpdate.isEmpty()){
        for (PriceAdjustmentSchedule priceadjustments : recordsToUpdate){
            priceadjustments.IsActive = true;
        }
        try {
            update recordsToUpdate;
            System.debug('Records updated successfully.');
        } catch (Exception e) {
            System.debug('Error updating records: ' + e.getMessage());
        }
    } else {
        System.debug('No records to update.');
    }