/*
This script activates Price Adjustment Schedules if not activated - courtesy of QBranch
*/
    List<PriceAdjustmentSchedule> recordsToUpdate = [SELECT Id
                                             FROM PriceAdjustmentSchedule
                                             WHERE Name IN ('Standard Attribute Based Adjustment','Standard Bundle Based Adjustment','Standard Price Adjustment Tier','Standard Tier Based Adjustment','Standard Volume Based Adjustment') and IsActive = false];

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