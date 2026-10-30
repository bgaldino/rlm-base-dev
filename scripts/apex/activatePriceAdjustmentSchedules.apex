/*
This script activates Price Adjustment Schedules if not activated - courtesy of QBranch

'Standard Price Adjustment Tier' (the volume schedule) is deliberately NOT activated.
The platform rejects PriceAdjustmentTier inserts and deletes while that schedule is
active, and every pricing load deletes and re-inserts the tiers, so activating it here
made a prepare_rlm_org rerun fail to reload them. The pricing plans keep it inactive,
and its tiers still price. See datasets/sfdmu/qb/en-US/qb-pricing/README.md.
Not yet verified: the q3 and qb/ja plans hang tiers off 'Standard Tier Based Adjustment' and
'Standard Volume Based Adjustment', which this script still activates.
*/
    List<PriceAdjustmentSchedule> recordsToUpdate = [SELECT Id
                                             FROM PriceAdjustmentSchedule
                                             WHERE Name IN ('Standard Attribute Based Adjustment','Standard Bundle Based Adjustment','Standard Tier Based Adjustment','Standard Volume Based Adjustment') and IsActive = false];

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