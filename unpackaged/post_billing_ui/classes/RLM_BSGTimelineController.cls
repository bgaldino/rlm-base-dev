public with sharing class RLM_BSGTimelineController {
    
    /**
     * Wrapper class for Billing Schedule Group data
     */
    public class BSGData {
        @AuraEnabled public String id;
        @AuraEnabled public String groupNumber;
        @AuraEnabled public String productName;
        @AuraEnabled public String accountName;
        @AuraEnabled public String currencyCode;
        @AuraEnabled public Decimal totalBilledAmount;
        @AuraEnabled public Decimal totalPendingAmount;
        @AuraEnabled public String billingTerm;
        @AuraEnabled public String billingTermUnit;
        @AuraEnabled public Integer billDayOfMonth;
        @AuraEnabled public Date cancellationDate;
        @AuraEnabled public Date startDate;
        @AuraEnabled public Date endDate;
        @AuraEnabled public Date suspensionDate;
        @AuraEnabled public Date resumptionDate;
        @AuraEnabled public List<BillingScheduleData> billingSchedules;
        @AuraEnabled public List<MilestoneChartItem> milestoneItems;
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
     * Wrapper for milestone chart data
     */
    public class MilestoneChartItem {
        @AuraEnabled public String id;
        @AuraEnabled public String name;
        @AuraEnabled public Decimal amount;
        @AuraEnabled public Decimal percentage;
        @AuraEnabled public String status;
        @AuraEnabled public Date completionDate;
        @AuraEnabled public Boolean isAccomplished;
        @AuraEnabled public String milestoneType;
        @AuraEnabled public Decimal referenceAmount;
        @AuraEnabled public Decimal billedAmount;
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
                       CurrencyIsoCode, TotalBilledAmount, TotalPendingAmount, BillingTerm, BillingTermUnit,
                       BillDayOfMonth, CancellationDate, StartDate, EndDate
                FROM BillingScheduleGroup
                WHERE Id = :recordId
                WITH USER_MODE
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
                WITH USER_MODE
                ORDER BY BillingScheduleStartDate ASC, CreatedDate ASC
            ];
            
            BSGData data = new BSGData();
            data.id = bsg.Id;
            data.groupNumber = bsg.BillingScheduleGroupNumber;
            data.productName = bsg.ProductName;
            data.accountName = bsg.BillingAccount?.Name;
            data.currencyCode = bsg.CurrencyIsoCode;
            data.totalBilledAmount = bsg.TotalBilledAmount;
            data.totalPendingAmount = bsg.TotalPendingAmount;
            data.billingTerm = String.valueOf(bsg.BillingTerm);
            data.billingTermUnit = bsg.BillingTermUnit;
            data.billDayOfMonth = bsg.BillDayOfMonth;
            data.cancellationDate = bsg.CancellationDate;
            data.startDate = bsg.StartDate;
            data.endDate = bsg.EndDate;

            // Suspension fields may not be available in all API versions — use dynamic query
            try {
                List<SObject> suspList = Database.query(
                    'SELECT BillingSuspensionDate, BillingResumptionDate FROM BillingScheduleGroup WHERE Id = :recordId LIMIT 1',
                    AccessLevel.USER_MODE
                );
                if (!suspList.isEmpty()) {
                    Object suspVal = suspList[0].get('BillingSuspensionDate');
                    Object resVal  = suspList[0].get('BillingResumptionDate');
                    if (suspVal != null) {
                        data.suspensionDate = Date.valueOf(String.valueOf(suspVal));
                    }
                    if (resVal != null) {
                        data.resumptionDate = Date.valueOf(String.valueOf(resVal));
                    }
                }
            } catch (Exception ex) {
                // Fields not available
            }
            
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

            // Inline milestone data if applicable. Billing milestone objects/fields are
            // license-gated billing extensions that aren't visible to the Apex compiler for
            // static references, so getMilestoneChartData() accesses them dynamically and
            // returns an empty list when no plan (or the feature) is present.
            List<MilestoneChartItem> milestones = getMilestoneChartData(recordId);
            if (!milestones.isEmpty()) {
                data.milestoneItems = milestones;
            }
            
            return data;
            
        } catch (Exception e) {
            throw new AuraHandledException('Error retrieving Billing Schedule Group: ' + e.getMessage());
        }
    }

    @AuraEnabled(cacheable=true)
    public static List<MilestoneChartItem> getMilestoneChartData(String recordId) {
        List<MilestoneChartItem> result = new List<MilestoneChartItem>();
        try {
            // BillingMilestonePlan(Item) and BillingSchedule.BillingMilestonePlanId are
            // license-gated billing extensions: present at runtime but not visible to the
            // Apex compiler for static SOQL/types. Access them dynamically (USER_MODE) so the
            // class compiles in every org and gracefully no-ops where the feature is absent.
            List<SObject> bsList = Database.query(
                'SELECT BillingMilestonePlanId FROM BillingSchedule ' +
                'WHERE BillingScheduleGroupId = :recordId AND BillingMilestonePlanId != null LIMIT 1',
                AccessLevel.USER_MODE
            );
            if (bsList.isEmpty()) {
                return result;
            }

            Id planId = (Id) bsList[0].get('BillingMilestonePlanId');

            List<SObject> bmpList = Database.query(
                'SELECT ReferenceItemAmount FROM BillingMilestonePlan WHERE Id = :planId LIMIT 1',
                AccessLevel.USER_MODE
            );
            Decimal referenceAmount = bmpList.isEmpty()
                ? null
                : (Decimal) bmpList[0].get('ReferenceItemAmount');

            List<BillingScheduleGroup> bsgList = [
                SELECT TotalBilledAmount FROM BillingScheduleGroup WHERE Id = :recordId WITH USER_MODE LIMIT 1
            ];
            Decimal groupBilledAmount = bsgList.isEmpty() ? null : bsgList[0].TotalBilledAmount;

            List<SObject> items = Database.query(
                'SELECT Id, Name, MilestoneAmount, Percentage, Status, ' +
                'MilestoneAccomplishmentDate, IsMilestoneAccomplished, MilestoneType ' +
                'FROM BillingMilestonePlanItem WHERE BillingMilestonePlanId = :planId ' +
                'ORDER BY IsMilestoneAccomplished DESC, MilestoneAccomplishmentDate ASC NULLS LAST, MilestoneAmount DESC',
                AccessLevel.USER_MODE
            );

            for (SObject item : items) {
                MilestoneChartItem mci = new MilestoneChartItem();
                mci.id = String.valueOf(item.get('Id'));
                mci.name = String.valueOf(item.get('Name'));
                mci.amount = (Decimal) item.get('MilestoneAmount');
                mci.percentage = (Decimal) item.get('Percentage');
                mci.status = (String) item.get('Status');
                mci.completionDate = (Date) item.get('MilestoneAccomplishmentDate');
                mci.isAccomplished = (Boolean) item.get('IsMilestoneAccomplished');
                mci.milestoneType = (String) item.get('MilestoneType');
                mci.referenceAmount = referenceAmount;
                mci.billedAmount = groupBilledAmount;
                result.add(mci);
            }
        } catch (Exception e) {
            // Billing milestone objects/fields not available in this org — return empty
        }
        return result;
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
