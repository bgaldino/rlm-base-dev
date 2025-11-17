// Activate Price Adjustment Schedules (only those with tiers)
// Salesforce requires at least one tier to activate a schedule

System.debug('Starting Price Adjustment Schedule activation...');

// Get all inactive schedules with their tier counts
Map<Id, Integer> scheduleTierCounts = new Map<Id, Integer>();
for (AggregateResult ar : [
    SELECT PriceAdjustmentScheduleId, COUNT(Id) tierCount 
    FROM PriceAdjustmentTier 
    WHERE PriceAdjustmentSchedule.IsActive = false
    GROUP BY PriceAdjustmentScheduleId
]) {
    scheduleTierCounts.put((Id)ar.get('PriceAdjustmentScheduleId'), (Integer)ar.get('tierCount'));
}

System.debug('Found ' + scheduleTierCounts.size() + ' schedules with tiers');

// Get all inactive schedules
List<PriceAdjustmentSchedule> allSchedules = [
    SELECT Id, Name, IsActive 
    FROM PriceAdjustmentSchedule 
    WHERE IsActive = false
];

System.debug('Total inactive schedules: ' + allSchedules.size());

// Only activate schedules that have tiers
List<PriceAdjustmentSchedule> schedulesToActivate = new List<PriceAdjustmentSchedule>();
List<String> skippedSchedules = new List<String>();

for (PriceAdjustmentSchedule schedule : allSchedules) {
    if (scheduleTierCounts.containsKey(schedule.Id)) {
        schedule.IsActive = true;
        schedulesToActivate.add(schedule);
        System.debug('✓ Will activate: ' + schedule.Name + ' (' + scheduleTierCounts.get(schedule.Id) + ' tiers)');
    } else {
        skippedSchedules.add(schedule.Name);
        System.debug('⚠ Skipping: ' + schedule.Name + ' (no tiers)');
    }
}

// Activate schedules
if (!schedulesToActivate.isEmpty()) {
    update schedulesToActivate;
    System.debug('======================================================================');
    System.debug('✓ Successfully activated ' + schedulesToActivate.size() + ' schedule(s)');
} else {
    System.debug('======================================================================');
    System.debug('⚠ No schedules to activate');
}

if (!skippedSchedules.isEmpty()) {
    System.debug('⚠ Skipped ' + skippedSchedules.size() + ' schedule(s) without tiers:');
    for (String name : skippedSchedules) {
        System.debug('  - ' + name);
    }
}

System.debug('======================================================================');
