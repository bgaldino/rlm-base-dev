public with sharing class RLM_BSGTimelineController {
    
    /**
     * Wrapper class for Billing Schedule Group data
     */
    public class BSGData {
        @AuraEnabled public String id;
        @AuraEnabled public String groupNumber;
        @AuraEnabled public String productName;
        @AuraEnabled public String accountName;
        @AuraEnabled public Decimal totalBilledAmount;
        @AuraEnabled public Decimal totalPendingAmount;
        @AuraEnabled public String billingTerm;
        @AuraEnabled public String billingTermUnit;
        @AuraEnabled public Integer billDayOfMonth;
        @AuraEnabled public Date cancellationDate;
        @AuraEnabled public Date startDate;
        @AuraEnabled public Date endDate;
        @AuraEnabled public List<BillingScheduleData> billingSchedules;
    }
    
    /**
     * Wrapper class for Billing Schedule data
     */
    public class BillingScheduleData {
        @AuraEnabled public String id;
        @AuraEnabled public String scheduleNumber;
        @AuraEnabled public String category;
        @AuraEnabled public String status;
        @AuraEnabled public Decimal quantity;
        @AuraEnabled public Decimal billedAmount;
        @AuraEnabled public Decimal pendingAmount;
        @AuraEnabled public Decimal totalAmount;
        @AuraEnabled public Decimal billingPeriodAmount;
        @AuraEnabled public Decimal unitPrice;
        @AuraEnabled public Date startDate;
        @AuraEnabled public Date endDate;
        @AuraEnabled public Date nextBillingDate;
        @AuraEnabled public String billingMethod;
        @AuraEnabled public String billingType;
        @AuraEnabled public Integer billingTerm;
        @AuraEnabled public String billingTermUnit;
    }
    
    /**
     * Wrapper class for consolidated billing timeline segments
     */
    public class ConsolidatedSegment {
        @AuraEnabled public Integer periodNumber;
        @AuraEnabled public Date startDate;
        @AuraEnabled public Date endDate;
        @AuraEnabled public Decimal netQuantity;
        @AuraEnabled public Decimal periodicBilling;
        @AuraEnabled public Decimal credits;
        @AuraEnabled public String status;
        @AuraEnabled public List<String> activeScheduleIds;
        @AuraEnabled public List<String> activeScheduleNumbers;
    }
    
    /**
     * Get Billing Schedule Group with related Billing Schedules
     */
    @AuraEnabled(cacheable=true)
    public static BSGData getBillingScheduleGroupData(String recordId) {
        try {
            // Query BSG with all required fields using correct field names
            List<BillingScheduleGroup> bsgList = [
                SELECT Id, BillingScheduleGroupNumber, ProductName, BillingAccountId, BillingAccount.Name,
                       TotalBilledAmount, TotalPendingAmount, BillingTerm, BillingTermUnit,
                       BillDayOfMonth, CancellationDate, StartDate, EndDate
                FROM BillingScheduleGroup
                WHERE Id = :recordId
                LIMIT 1
            ];
            
            if (bsgList.isEmpty()) {
                throw new AuraHandledException('Billing Schedule Group not found');
            }
            
            BillingScheduleGroup bsg = bsgList[0];
            
            // Query related Billing Schedules separately
            List<BillingSchedule> billingSchedules = [
                SELECT Id, BillingScheduleNumber, Category, Status, Quantity, BilledAmount, 
                       PendingAmount, TotalAmount, BillingPeriodAmount, UnitPrice,
                       BillingScheduleStartDate, BillingScheduleEndDate,
                       NextBillingDate, BillingMethod, BillingType, BillingTerm,
                       BillingTermUnit
                FROM BillingSchedule
                WHERE BillingScheduleGroupId = :recordId
                ORDER BY BillingScheduleStartDate ASC, CreatedDate ASC
            ];
            
            BSGData data = new BSGData();
            data.id = bsg.Id;
            data.groupNumber = bsg.BillingScheduleGroupNumber;
            data.productName = bsg.ProductName;
            data.accountName = bsg.BillingAccount?.Name;
            data.totalBilledAmount = bsg.TotalBilledAmount;
            data.totalPendingAmount = bsg.TotalPendingAmount;
            data.billingTerm = String.valueOf(bsg.BillingTerm);
            data.billingTermUnit = bsg.BillingTermUnit;
            data.billDayOfMonth = bsg.BillDayOfMonth;
            data.cancellationDate = bsg.CancellationDate;
            data.startDate = bsg.StartDate;
            data.endDate = bsg.EndDate;
            
            // Map billing schedules
            data.billingSchedules = new List<BillingScheduleData>();
            for (BillingSchedule bs : billingSchedules) {
                BillingScheduleData bsData = new BillingScheduleData();
                bsData.id = bs.Id;
                bsData.scheduleNumber = bs.BillingScheduleNumber;
                bsData.category = bs.Category;
                bsData.status = bs.Status;
                bsData.quantity = bs.Quantity;
                bsData.billedAmount = bs.BilledAmount;
                bsData.pendingAmount = bs.PendingAmount;
                bsData.totalAmount = bs.TotalAmount;
                bsData.billingPeriodAmount = bs.BillingPeriodAmount;
                bsData.unitPrice = bs.UnitPrice;
                bsData.startDate = bs.BillingScheduleStartDate;
                bsData.endDate = bs.BillingScheduleEndDate;
                bsData.nextBillingDate = bs.NextBillingDate;
                bsData.billingMethod = bs.BillingMethod;
                bsData.billingType = bs.BillingType;
                bsData.billingTerm = bs.BillingTerm;
                bsData.billingTermUnit = bs.BillingTermUnit;
                
                data.billingSchedules.add(bsData);
            }
            
            return data;
            
        } catch (Exception e) {
            throw new AuraHandledException('Error retrieving Billing Schedule Group: ' + e.getMessage());
        }
    }
    
    /**
     * Get consolidated billing timeline segments
     */
    @AuraEnabled(cacheable=true)
    public static List<ConsolidatedSegment> getConsolidatedTimeline(String recordId) {
        try {
            // Get BSG data
            BSGData bsgData = getBillingScheduleGroupData(recordId);
            
            if (bsgData.billingSchedules.isEmpty()) {
                return new List<ConsolidatedSegment>();
            }
            
            // Build segments in a List (insertion order = chronological order since allDates is sorted).
            // A Map was previously used but Map.values() iteration order is not guaranteed in Apex.
            List<ConsolidatedSegment> segments = new List<ConsolidatedSegment>();
            List<Date> allDates = new List<Date>();
            
            // Collect all unique start and end dates
            Set<Date> dateSet = new Set<Date>();
            for (BillingScheduleData bs : bsgData.billingSchedules) {
                if (bs.startDate != null) dateSet.add(bs.startDate);
                if (bs.endDate != null) dateSet.add(bs.endDate.addDays(1)); // Add 1 day for exclusive end
            }
            
            allDates.addAll(dateSet);
            allDates.sort();
            
            // Create segments based on date boundaries
            Integer periodNum = 1;
            for (Integer i = 0; i < allDates.size() - 1; i++) {
                Date segStart = allDates[i];
                Date segEnd = allDates[i + 1].addDays(-1); // Subtract 1 for inclusive end
                
                ConsolidatedSegment segment = new ConsolidatedSegment();
                segment.periodNumber = periodNum++;
                segment.startDate = segStart;
                segment.endDate = segEnd;
                segment.netQuantity = 0;
                segment.periodicBilling = 0;
                segment.credits = 0;
                segment.activeScheduleIds = new List<String>();
                segment.activeScheduleNumbers = new List<String>();
                segment.status = 'Active';
                
                // Find all BS that overlap with this segment
                for (BillingScheduleData bs : bsgData.billingSchedules) {
                    if (bs.startDate <= segEnd && bs.endDate >= segStart) {
                        segment.activeScheduleIds.add(bs.id);
                        segment.activeScheduleNumbers.add(bs.scheduleNumber);
                        
                        // Calculate quantities and amounts
                        if (bs.quantity != null) {
                            segment.netQuantity += bs.quantity;
                        }
                        
                        if (bs.billingPeriodAmount != null) {
                            if (bs.billingPeriodAmount >= 0) {
                                segment.periodicBilling += bs.billingPeriodAmount;
                            } else {
                                segment.credits += bs.billingPeriodAmount;
                            }
                        }
                        
                        // Check if any schedule is cancelled
                        if (bs.category == 'Cancellation' || bs.status == 'Cancelled') {
                            segment.status = 'Cancelled';
                        } else if (bs.status == 'Completely Billed' && segment.status != 'Cancelled') {
                            segment.status = 'Completely Billed';
                        }
                    }
                }
                
                segments.add(segment);
            }

            return segments;
            
        } catch (Exception e) {
            throw new AuraHandledException('Error calculating consolidated timeline: ' + e.getMessage());
        }
    }
}