/**
 * RCAccountUtilities
 * 
 * This class provides functionality to delete all related objects for an account in the correct order.
 * It handles complex relationships between objects, particularly focusing on Usage Entitlement Buckets
 * which have parent-child relationships that must be respected during deletion.
 * 
 * The deletion process follows this general hierarchy:
 * 1. Orders and Order Items
 * 2. Usage Entitlement Accounts (UEA)
 * 3. Transaction Usage Entitlements (TUE)
 * 4. Usage Entitlement Buckets (UEB)
 * 5. Assets and Asset Relationships
 * 6. Contracts
 * 7. Invoices
 * 8. Quotes
 * 9. Opportunities
 * 
 * Special attention is paid to the Usage Entitlement Bucket deletion process, which must:
 * - Handle parent-child relationships
 * - Delete child buckets before parent buckets
 * - Maintain referential integrity
 * - Handle complex multi-level hierarchies
 */
public class RCAccountUtilities {
    /**
     * Input Variables Class
     * Used to pass parameters to the main deletion method
     */
    public class InputVariables {
        @InvocableVariable
        public String accountId;
        @InvocableVariable
        public Boolean DeleteAssets;
        @InvocableVariable
        public Boolean DeleteFulfillment;
        @InvocableVariable
        public Boolean DeleteBilling;
    }

    /**
     * Main Method
     * Entry point for the account cleanup process.
     * This method orchestrates the deletion of all related objects in the correct order.
     * 
     * @param request List of InputVariables containing the account ID and deletion flags
     */
    @InvocableMethod(label='Reset Account Related Objects.')
    public static void delAccountRelatedObjects(List<InputVariables> request) {
        String accountId = request.get(0).accountId;
        Boolean deleteAssets = request.get(0).DeleteAssets;
        Boolean deleteFulfillment = request.get(0).DeleteFulfillment;
        Boolean deleteBilling = request.get(0).DeleteBilling;

        deleteOrders(accountId);
        deleteTransactionJournal(accountId);
        deleteUsageSummaries(accountId);
        deleteBillingScheduleGroups(accountId);
        deleteContracts(accountId);
        deleteAssets(accountId);
        deleteInvoices(accountId);
        deleteQuotes(accountId);
        deleteOpportunities(accountId);
    }

    /**
     * Deletes all opportunities associated with the account.
     * 
     * @param accountId The ID of the account whose opportunities should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteOpportunities(String accountId) {
        Id accountIdConverted = accountId;
        Opportunity[] opportunitiesToDelete = [SELECT Id FROM Opportunity WHERE AccountId = :accountIdConverted];
        if (!opportunitiesToDelete.isEmpty()) {
            Database.delete(opportunitiesToDelete);
        }
        return true;
    }

    /**
     * Deletes all quotes associated with the account.
     * 
     * @param accountId The ID of the account whose quotes should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteQuotes(String accountId) {
        Id accountIdConverted = accountId;
        Quote[] quotesToDelete = [SELECT Id FROM Quote WHERE QuoteAccountId = :accountIdConverted];
        if (!quotesToDelete.isEmpty()) {
            Set<Id> quoteIds = new Set<Id>();
            for (Quote q : quotesToDelete) {
                quoteIds.add(q.Id);
            }
            Database.delete(quotesToDelete);
        }
        return true;
    }

    /**
     * Deletes all orders and related objects for an account.
     * The deletion process follows this hierarchy:
     * 1. Orders
     * 2. Order Items
     * 3. Usage Entitlement Accounts (UEA)
     * 4. Transaction Usage Entitlements (TUE)
     * 5. Usage Entitlement Buckets (UEB)
     * 
     * The UEB deletion is particularly complex as it needs to handle parent-child relationships:
     * - UEBs can be parents of other UEBs
     * - UEBs can be children of UEAs or other UEBs
     * - Deletion must happen from bottom to top of the hierarchy
     * 
     * @param accountId The ID of the account whose orders should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteOrders(String accountId) {
        Id accountIdConverted = accountId;
        Order[] ordersToDelete = [SELECT Id FROM Order WHERE AccountId = :accountIdConverted];
        if (!ordersToDelete.isEmpty()) {
            Set<Id> orderIds = new Set<Id>();
            for (Order o : ordersToDelete) {
                orderIds.add(o.Id);
                o.Status = 'Draft';
            }
            update ordersToDelete;
            
            OrderItem[] orderItems = getOrderItems(orderIds);
            if (!orderItems.isEmpty()) {
                // Delete in correct order: UEA -> TUE -> UEB
                deleteUsageEntitlementAccount(accountId);
                deleteTransactionUsageEntitlement(accountId);
                deleteFulfillmentLineSourceRel(orderItems);
            }
            
            for (Order o : ordersToDelete) {
                o.Status = 'Draft';
            }
            Database.update(ordersToDelete);
            Database.delete(ordersToDelete);
        }
        System.debug('Total Number of SOQL Queries after deleteOrders(): ' + Limits.getQueries());
        return true;
    }

    /**
     * Retrieves all order items for a given set of order IDs.
     * 
     * @param orderIds Set of order IDs to find related order items
     * @return List of OrderItem records
     */
    private static List<OrderItem> getOrderItems(Set<Id> orderIds) {
        return [SELECT Id FROM OrderItem WHERE OrderId IN :orderIds];
    }

    /**
     * Deletes fulfillment line source relationships for a set of order items.
     * 
     * @param orderItems List of order items whose fulfillment relationships should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteFulfillmentLineSourceRel(OrderItem[] orderItems) {
        if (!orderItems.isEmpty()) {
            Set<Id> orderItemIds = new Set<Id>();
            for (OrderItem oi : orderItems) {
                orderItemIds.add(oi.Id);
            }
            FulfillmentLineSourceRel[] fulfillmentLineSourceRelToDelete = 
                [SELECT Id FROM FulfillmentLineSourceRel WHERE SourceLineItemId IN :orderItemIds];
            if (!fulfillmentLineSourceRelToDelete.isEmpty()) {
                Database.delete(fulfillmentLineSourceRelToDelete);
            }
        }
        return true;
    }

    /**
     * Deletes Usage Entitlement Buckets (UEB) related to Transaction Usage Entitlements (TUE).
     * The deletion process:
     * 1. Finds all UEBs related to the TUEs (either directly or through parent relationships)
     * 2. Builds a complete map of parent-child relationships
     * 3. Identifies top-level parent buckets
     * 4. Deletes buckets level by level, starting from the bottom of the hierarchy
     * 5. Finally deletes top-level parent buckets
     * 
     * This ensures that child buckets are always deleted before their parents.
     * 
     * @param entitlementIds Set of Transaction Usage Entitlement IDs
     * @return Boolean indicating success
     */
    private static Boolean deleteUsageEntitlementBucket(Set<Id> entitlementIds) {
        System.debug('Delete Entitlement Bucket - Starting deletion for entitlement IDs: ' + entitlementIds);
        
        // First, find all buckets that might be related (either directly or through parent relationships)
        UsageEntitlementBucket[] allBuckets = [
            SELECT Id, Name, ParentId, Parent.Type, Parent.Name 
            FROM UsageEntitlementBucket 
            WHERE TransactionUsageEntitlementId IN :entitlementIds
            OR ParentId IN :entitlementIds
            OR Id IN :entitlementIds
        ];
        System.debug('Found ' + allBuckets.size() + ' total Usage Entitlement Buckets');
        for(UsageEntitlementBucket bucket : allBuckets) {
            System.debug('Bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - Parent: ' + (bucket.ParentId != null ? bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')' : 'None'));
        }
        
        // Create maps to track relationships
        Map<Id, List<Id>> parentToChildrenMap = new Map<Id, List<Id>>();
        Map<Id, Id> childToParentMap = new Map<Id, Id>();
        Set<Id> allBucketIds = new Set<Id>();
        
        // First pass - collect all bucket IDs and build child-to-parent map
        for(UsageEntitlementBucket bucket : allBuckets) {
            allBucketIds.add(bucket.Id);
            if(bucket.ParentId != null) {
                childToParentMap.put(bucket.Id, bucket.ParentId);
            }
        }
        
        // Find all child buckets
        UsageEntitlementBucket[] childBuckets = [
            SELECT Id, Name, ParentId, Parent.Type, Parent.Name 
            FROM UsageEntitlementBucket 
            WHERE ParentId IN :allBucketIds
        ];
        System.debug('Found ' + childBuckets.size() + ' child buckets');
        for(UsageEntitlementBucket bucket : childBuckets) {
            System.debug('Child Bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - Parent: ' + bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')');
            allBucketIds.add(bucket.Id);
            childToParentMap.put(bucket.Id, bucket.ParentId);
        }
        
        // Build parent-to-children map
        for(UsageEntitlementBucket bucket : childBuckets) {
            if(bucket.ParentId != null && bucket.Parent.Type == 'UsageEntitlementBucket') {
                if(!parentToChildrenMap.containsKey(bucket.ParentId)) {
                    parentToChildrenMap.put(bucket.ParentId, new List<Id>());
                }
                parentToChildrenMap.get(bucket.ParentId).add(bucket.Id);
                System.debug('Added relationship - Parent: ' + bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ') -> Child: ' + bucket.Name + ' (ID: ' + bucket.Id + ')');
            }
        }
        
        // Find top-level parent buckets (those that are not children of any other bucket)
        Set<Id> topLevelParentIds = new Set<Id>();
        for(Id bucketId : allBucketIds) {
            if(!childToParentMap.containsKey(bucketId)) {
                topLevelParentIds.add(bucketId);
            }
        }
        System.debug('Found ' + topLevelParentIds.size() + ' top-level parent buckets');
        
        // Process buckets level by level, starting from the bottom
        Set<Id> processedIds = new Set<Id>();
        Set<Id> currentLevel = new Set<Id>(allBucketIds);
        currentLevel.removeAll(topLevelParentIds);
        
        while(!currentLevel.isEmpty()) {
            Set<Id> nextLevel = new Set<Id>();
            Set<Id> toDelete = new Set<Id>();
            
            // Find leaf nodes (buckets that have no children or whose children are already processed)
            for(Id bucketId : currentLevel) {
                if(!parentToChildrenMap.containsKey(bucketId) || 
                   (parentToChildrenMap.containsKey(bucketId) && 
                    processedIds.containsAll(parentToChildrenMap.get(bucketId)))) {
                    toDelete.add(bucketId);
                } else {
                    nextLevel.add(bucketId);
                }
            }
            
            // Delete leaf nodes
            if(!toDelete.isEmpty()) {
                System.debug('Deleting ' + toDelete.size() + ' leaf buckets');
                try {
                    Database.delete([SELECT Id, Name FROM UsageEntitlementBucket WHERE Id IN :toDelete]);
                    System.debug('Successfully deleted leaf buckets');
                    processedIds.addAll(toDelete);
                } catch(Exception e) {
                    System.debug('Error deleting leaf buckets: ' + e.getMessage());
                    System.debug('Stack trace: ' + e.getStackTraceString());
                    throw e;
                }
            }
            
            currentLevel = nextLevel;
        }
        
        // Finally delete top-level parent buckets
        if(!topLevelParentIds.isEmpty()) {
            System.debug('Deleting ' + topLevelParentIds.size() + ' top-level parent buckets');
            try {
                Database.delete([SELECT Id, Name FROM UsageEntitlementBucket WHERE Id IN :topLevelParentIds]);
                System.debug('Successfully deleted top-level parent buckets');
            } catch(Exception e) {
                System.debug('Error deleting top-level parent buckets: ' + e.getMessage());
                System.debug('Stack trace: ' + e.getStackTraceString());
                throw e;
            }
        }
        
        return true;
    }

    /**
     * Deletes Usage Entitlement Buckets (UEB) related to Usage Entitlement Accounts (UEA).
     * The deletion process:
     * 1. Finds all UEBs related to the UEAs (either directly or through parent relationships)
     * 2. Builds a complete map of parent-child relationships
     * 3. Identifies top-level parent buckets
     * 4. Deletes buckets level by level, starting from the bottom of the hierarchy
     * 5. Finally deletes top-level parent buckets
     * 
     * This ensures that child buckets are always deleted before their parents.
     * 
     * @param entitlementIds Set of Usage Entitlement Account IDs
     * @return Boolean indicating success
     */
    private static Boolean deleteUsageEntitlementBucketParent(Set<Id> entitlementIds) {
        System.debug('Delete Entitlement Bucket Parent - Starting deletion for entitlement IDs: ' + entitlementIds);
        
        // First, find all buckets that might be related (either directly or through parent relationships)
        UsageEntitlementBucket[] allBuckets = [
            SELECT Id, Name, ParentId, Parent.Type, Parent.Name 
            FROM UsageEntitlementBucket 
            WHERE ParentId IN :entitlementIds
            OR Id IN :entitlementIds
        ];
        System.debug('Found ' + allBuckets.size() + ' total Usage Entitlement Buckets');
        for(UsageEntitlementBucket bucket : allBuckets) {
            System.debug('Bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - Parent: ' + (bucket.ParentId != null ? bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')' : 'None'));
        }
        
        // Create maps to track relationships
        Map<Id, List<Id>> parentToChildrenMap = new Map<Id, List<Id>>();
        Map<Id, Id> childToParentMap = new Map<Id, Id>();
        Set<Id> allBucketIds = new Set<Id>();
        
        // First pass - collect all bucket IDs and build child-to-parent map
        for(UsageEntitlementBucket bucket : allBuckets) {
            allBucketIds.add(bucket.Id);
            if(bucket.ParentId != null) {
                childToParentMap.put(bucket.Id, bucket.ParentId);
            }
        }
        
        // Find all child buckets
        UsageEntitlementBucket[] childBuckets = [
            SELECT Id, Name, ParentId, Parent.Type, Parent.Name 
            FROM UsageEntitlementBucket 
            WHERE ParentId IN :allBucketIds
        ];
        System.debug('Found ' + childBuckets.size() + ' child buckets');
        for(UsageEntitlementBucket bucket : childBuckets) {
            System.debug('Child Bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - Parent: ' + bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')');
            allBucketIds.add(bucket.Id);
            childToParentMap.put(bucket.Id, bucket.ParentId);
        }
        
        // Build parent-to-children map
        for(UsageEntitlementBucket bucket : childBuckets) {
            if(bucket.ParentId != null && bucket.Parent.Type == 'UsageEntitlementBucket') {
                if(!parentToChildrenMap.containsKey(bucket.ParentId)) {
                    parentToChildrenMap.put(bucket.ParentId, new List<Id>());
                }
                parentToChildrenMap.get(bucket.ParentId).add(bucket.Id);
                System.debug('Added relationship - Parent: ' + bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ') -> Child: ' + bucket.Name + ' (ID: ' + bucket.Id + ')');
            }
        }
        
        // Find top-level parent buckets (those that are not children of any other bucket)
        Set<Id> topLevelParentIds = new Set<Id>();
        for(Id bucketId : allBucketIds) {
            if(!childToParentMap.containsKey(bucketId)) {
                topLevelParentIds.add(bucketId);
            }
        }
        System.debug('Found ' + topLevelParentIds.size() + ' top-level parent buckets');
        
        // Process buckets level by level, starting from the bottom
        Set<Id> processedIds = new Set<Id>();
        Set<Id> currentLevel = new Set<Id>(allBucketIds);
        currentLevel.removeAll(topLevelParentIds);
        
        while(!currentLevel.isEmpty()) {
            Set<Id> nextLevel = new Set<Id>();
            Set<Id> toDelete = new Set<Id>();
            
            // Find leaf nodes (buckets that have no children or whose children are already processed)
            for(Id bucketId : currentLevel) {
                if(!parentToChildrenMap.containsKey(bucketId) || 
                   (parentToChildrenMap.containsKey(bucketId) && 
                    processedIds.containsAll(parentToChildrenMap.get(bucketId)))) {
                    toDelete.add(bucketId);
                } else {
                    nextLevel.add(bucketId);
                }
            }
            
            // Delete leaf nodes
            if(!toDelete.isEmpty()) {
                System.debug('Deleting ' + toDelete.size() + ' leaf buckets');
                try {
                    Database.delete([SELECT Id, Name FROM UsageEntitlementBucket WHERE Id IN :toDelete]);
                    System.debug('Successfully deleted leaf buckets');
                    processedIds.addAll(toDelete);
                } catch(Exception e) {
                    System.debug('Error deleting leaf buckets: ' + e.getMessage());
                    System.debug('Stack trace: ' + e.getStackTraceString());
                    throw e;
                }
            }
            
            currentLevel = nextLevel;
        }
        
        // Finally delete top-level parent buckets
        if(!topLevelParentIds.isEmpty()) {
            System.debug('Deleting ' + topLevelParentIds.size() + ' top-level parent buckets');
            try {
                Database.delete([SELECT Id, Name FROM UsageEntitlementBucket WHERE Id IN :topLevelParentIds]);
                System.debug('Successfully deleted top-level parent buckets');
            } catch(Exception e) {
                System.debug('Error deleting top-level parent buckets: ' + e.getMessage());
                System.debug('Stack trace: ' + e.getStackTraceString());
                throw e;
            }
        }
        
        return true;
    }

    /**
     * Deletes Transaction Usage Entitlements (TUE) and their related Usage Entitlement Buckets (UEB)
     * for a given account.
     * 
     * @param accountId The ID of the account whose TUEs should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteTransactionUsageEntitlement(String accountId) {
        Id accountIdConverted = accountId;
        System.debug('JOHN');
        TransactionUsageEntitlement[] transactionUsageEntitlementToDelete = 
            [SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :accountIdConverted];
        if (!transactionUsageEntitlementToDelete.isEmpty()) {
            Set<Id> tueIds = new Set<Id>();
            for (TransactionUsageEntitlement tue : transactionUsageEntitlementToDelete) {
                tueIds.add(tue.Id);
            }
            deleteUsageEntitlementBucket(tueIds);
            Database.delete(transactionUsageEntitlementToDelete);
        }
        return true;
    }

    /**
     * Deletes Usage Entitlement Accounts (UEA) and their related Usage Entitlement Buckets (UEB)
     * for a given account.
     * 
     * @param accountId The ID of the account whose UEAs should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteUsageEntitlementAccount(String accountId) {
        Id accountIdConverted = accountId;
        System.debug('UEA ' + accountIdConverted);
        UsageEntitlementAccount[] usageEntitlementAccountToDelete = 
            [SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :accountIdConverted];
        if (!usageEntitlementAccountToDelete.isEmpty()) {
            Set<Id> ueaIds = new Set<Id>();
            for (UsageEntitlementAccount uea : usageEntitlementAccountToDelete) {
                ueaIds.add(uea.Id);
            }
            System.debug('UEA Ids ' + ueaIds);
            deleteUsageEntitlementBucketParent(ueaIds);
            Database.delete(usageEntitlementAccountToDelete);
        }
        return true;
    }

    /**
     * Deletes transaction journals associated with the account.
     * 
     * @param accountId The ID of the account whose transaction journals should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteTransactionJournal(String accountId) {
        TransactionJournal[] transactionJournalToDelete = 
            [SELECT Id FROM TransactionJournal WHERE AccountId = :accountId];
        if (!transactionJournalToDelete.isEmpty()) {
            Database.delete(transactionJournalToDelete);
        }
        return true;
    }

    /**
     * Deletes usage summaries associated with the account.
     * 
     * @param accountId The ID of the account whose usage summaries should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteUsageSummaries(String accountId) {
        UsageSummary[] usageSummaryToDelete = 
            [SELECT Id FROM UsageSummary WHERE AccountId = :accountId];
        if (!usageSummaryToDelete.isEmpty()) {
            Database.delete(usageSummaryToDelete);
        }
        return true;
    }

    /**
     * Deletes billing schedule groups associated with the account.
     * 
     * @param accountId The ID of the account whose billing schedule groups should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteBillingScheduleGroups(String accountId) {
        BillingScheduleGroup[] billingScheduleGroupsToDelete = 
            [SELECT Id FROM BillingScheduleGroup WHERE BillingAccountId = :accountId];
        if (!billingScheduleGroupsToDelete.isEmpty()) {
            Database.delete(billingScheduleGroupsToDelete);
        }
        return true;
    }

    /**
     * Deletes contracts associated with the account.
     * 
     * @param accountId The ID of the account whose contracts should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteContracts(String accountId) {
        Contract[] contractsToDelete = 
            [SELECT Id FROM Contract WHERE AccountId = :accountId];
        if (!contractsToDelete.isEmpty()) {
            Database.delete(contractsToDelete);
        }
        return true;
    }

    /**
     * Deletes asset relationships for a set of assets.
     * 
     * @param assetIds Set of asset IDs whose relationships should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteAssetRelationship(Set<Id> assetIds) {
        AssetRelationship[] assetRelationshipToDelete = 
            [SELECT Id FROM AssetRelationship WHERE AssetId IN :assetIds];
        if (!assetRelationshipToDelete.isEmpty()) {
            Database.delete(assetRelationshipToDelete);
        }
        return true;
    }

    /**
     * Deletes assets and their relationships associated with the account.
     * 
     * @param accountId The ID of the account whose assets should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteAssets(String accountId) {
        Id accountIdConverted = accountId;
        System.debug('ASS ' + accountIdConverted);
        Asset[] assetsToDelete = [SELECT Id FROM Asset WHERE AccountId = :accountIdConverted];
        if (!assetsToDelete.isEmpty()) {
            Set<Id> assIds = new Set<Id>();
            for (Asset ass : assetsToDelete) {
                assIds.add(ass.Id);
            }
            System.debug('ASS Ids ' + assIds);
            deleteAssetRelationship(assIds);
            Database.delete(assetsToDelete);
        }
        return true;
    }

    /**
     * Deletes draft invoices associated with the account.
     * 
     * @param accountId The ID of the account whose invoices should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteInvoices(String accountId) {
        Invoice[] invoicesToDelete = 
            [SELECT Id FROM Invoice WHERE BillingAccountId = :accountId AND Status = 'Draft'];
        if (!invoicesToDelete.isEmpty()) {
            Database.delete(invoicesToDelete);
        }
        return true;
    }
}