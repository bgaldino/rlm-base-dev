public with sharing class RLM_BillingScheduleGroupController {
    
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
                       TotalBilledAmount, 
                       TotalPendingAmount, 
                       BillingType,
                       BillingAccountId
                FROM BillingScheduleGroup 
                WHERE BillingAccountId = :accountId
                ORDER BY StartDate DESC NULLS LAST
            ];
            
            if (bsgs.isEmpty()) {
                return new List<BsgWrapper>();
            }
            
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
                WHERE MainBsgId IN :bsgIds
            ];
            
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
            
        } catch (Exception e) {
            throw new AuraHandledException('Error fetching billing schedule groups: ' + e.getMessage());
        }
    }
}