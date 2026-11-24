public with sharing class RLM_BillingScheduleGroupController {
    @TestVisible
    private static final String LOAD_FAILED_MESSAGE =
        'The billing schedule groups could not be loaded. Refresh the page; if it continues, contact your administrator.';
    
    public class BsgWrapper {
        @AuraEnabled
        public BillingScheduleGroup bsg { get; set; }
        @AuraEnabled
        public List<BsgRelationship> relationships { get; set; }
        
        public BsgWrapper() {
            this.relationships = new List<BsgRelationship>();
        }
    }
    
    @AuraEnabled(cacheable=true)
    public static List<BsgWrapper> getBillingScheduleGroups(Id accountId) {
        try {
            // Query all BSGs for the account
            List<BillingScheduleGroup> bsgs = [
                SELECT Id,
                       ProductName,
                       ReferenceEntityId,
                       StartDate,
                       EndDate,
                       BillingTermUnit,
                       CurrencyIsoCode,
                       TotalBilledAmount,
                       TotalPendingAmount,
                       BillingType,
                       BillingAccountId
                FROM BillingScheduleGroup 
                WHERE BillingAccountId = :accountId
                WITH USER_MODE ORDER BY StartDate DESC NULLS LAST
            ];
            
            if (bsgs.isEmpty()) {
                return new List<BsgWrapper>();
            }
            
            return wrappersWithRelationships(bsgs);
            
        } catch (Exception e) {
            throw RLM_AuraErrors.failed(LOAD_FAILED_MESSAGE, 'RLM_BillingScheduleGroupController.getBillingScheduleGroups', e);
        }
    }

    // Adds each group's relationships, where it is the main group. Takes the groups so a test
    // can run the relationship query for groups Apex cannot insert.
    @TestVisible
    private static List<BsgWrapper> wrappersWithRelationships(List<BillingScheduleGroup> bsgs) {
        // Get all BSG IDs
        Set<Id> bsgIds = new Set<Id>();
        for (BillingScheduleGroup bsg : bsgs) {
            bsgIds.add(bsg.Id);
        }

        // Query relationships where each BSG is the main (parent) BSG.
        // The UI displays associated BSGs from the main side only.
        List<BsgRelationship> allRelationships = [
            SELECT Id,
                   MainBsgId,
                   AssociatedBsgId,
                   AssociatedBsgRole,
                   AssociatedBsgPricing
            FROM BsgRelationship
            WHERE MainBsgId IN :bsgIds WITH USER_MODE
        ];
        return buildWrappers(bsgs, allRelationships);
    }

    // One wrapper per group, in the groups' order, with the relationships whose main group it is.
    // Takes rows so a test can pass groups and relationships, which Apex cannot insert.
    @TestVisible
    private static List<BsgWrapper> buildWrappers(List<BillingScheduleGroup> bsgs, List<BsgRelationship> allRelationships) {
        Set<Id> bsgIds = new Set<Id>();
        for (BillingScheduleGroup bsg : bsgs) {
            bsgIds.add(bsg.Id);
        }

        // Create a map of BSG Id to its relationships where it is the main BSG
        Map<Id, List<BsgRelationship>> bsgToRelationshipsMap = new Map<Id, List<BsgRelationship>>();
        for (BsgRelationship rel : allRelationships) {
            if (bsgIds.contains(rel.MainBsgId)) {
                if (!bsgToRelationshipsMap.containsKey(rel.MainBsgId)) {
                    bsgToRelationshipsMap.put(rel.MainBsgId, new List<BsgRelationship>());
                }
                bsgToRelationshipsMap.get(rel.MainBsgId).add(rel);
            }
        }

        // Build the wrapper list
        List<BsgWrapper> wrappers = new List<BsgWrapper>();
        for (BillingScheduleGroup bsg : bsgs) {
            BsgWrapper wrapper = new BsgWrapper();
            wrapper.bsg = bsg;
            wrapper.relationships = bsgToRelationshipsMap.get(bsg.Id);
            if (wrapper.relationships == null) {
                wrapper.relationships = new List<BsgRelationship>();
            }
            wrappers.add(wrapper);
        }

        return wrappers;
    }
}
