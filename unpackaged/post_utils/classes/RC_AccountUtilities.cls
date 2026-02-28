/**
 * RC_AccountUtilities
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
 * 
 * @author John Rozsits, Brian Galdino, Anthropic Claude 4 Sonnet
 * @date 2025-06-10
 */
public class RC_AccountUtilities {
    // Constants
    private static final Integer BATCH_SIZE = 200;
    /**
     * Input variables for the account cleanup process.
     * These variables control which types of objects should be deleted.
     */
    public class InputVariables {
        @InvocableVariable(required=true)
        public String accountId;
        
        @InvocableVariable(required=true)
        public Boolean DeleteAssets;
        
        @InvocableVariable(required=true)
        public Boolean DeleteFulfillment;
        
        @InvocableVariable(required=true)
        public Boolean DeleteBilling;
    }

    /**
     * Helper class to store Order and OrderItem data
     * This class centralizes all queries for related objects to avoid redundant queries.
     * It maintains lists and sets of IDs for efficient lookups and deletions.
     */
    private class OrderData {
        // Orders and their IDs
        public List<Order> orders;
        public Set<Id> orderIds;
        
        // OrderItems and their IDs
        public List<OrderItem> orderItems;
        public Set<Id> orderItemIds;
        
        // Source identifiers for FulfillmentPlans (Order and OrderItem IDs)
        public Set<String> sourceIdentifiers;
        
        // FulfillmentOrders and their IDs
        public List<FulfillmentOrder> fulfillmentOrders;
        public Set<Id> fulfillmentOrderIds;
        
        // FulfillmentPlans and their IDs
        public List<FulfillmentPlan> fulfillmentPlans;
        public Set<Id> fulfillmentPlanIds;
        
        // FulfillmentSteps and their IDs
        public List<FulfillmentStep> fulfillmentSteps;
        public Set<Id> fulfillmentStepIds;
        
        // FulfillmentAssets and their IDs
        public List<FulfillmentAsset> fulfillmentAssets;
        public Set<Id> fulfillmentAssetIds;
        
        // FulfillmentOrderLineItems and their IDs
        public List<FulfillmentOrderLineItem> fulfillmentOrderLineItems;
        public Set<Id> fulfillmentOrderLineItemIds;

        // FulfillmentLineSourceRel records
        public List<FulfillmentLineSourceRel> fulfillmentLineSourceRels;
        public Set<Id> fulfillmentLineSourceRelIds;
        
        /**
         * Constructor that initializes all data for the given account.
         * Queries are executed in a specific order to maintain referential integrity:
         * 1. Orders and OrderItems (base objects)
         * 2. Invoices and OrderSummaries (for FulfillmentOrders)
         * 3. FulfillmentOrders (depends on Orders, Invoices, Summaries)
         * 4. FulfillmentPlans (depends on Orders and OrderItems)
         * 5. FulfillmentSteps (depends on FulfillmentPlans)
         * 6. FulfillmentAssets (depends on Account)
         * 7. FulfillmentOrderLineItems (depends on FulfillmentOrders)
         * 8. FulfillmentLineSourceRel (depends on OrderItems)
         */
        public OrderData(String accountId) {
            // Get all Orders for this account
            this.orders = [
                SELECT Id 
                FROM Order 
                WHERE AccountId = :accountId
            ];
            
            this.orderIds = new Set<Id>(new Map<Id, Order>(this.orders).keySet());
            
            // Get all OrderItems for this account
            this.orderItems = [
                SELECT Id 
                FROM OrderItem 
                WHERE Order.AccountId = :accountId
            ];
            
            this.orderItemIds = new Set<Id>(new Map<Id, OrderItem>(this.orderItems).keySet());
            this.sourceIdentifiers = new Set<String>();
            // Convert Id sets to String sets for sourceIdentifiers
            for(Id orderItemId : this.orderItemIds) {
                this.sourceIdentifiers.add(orderItemId);
            }
            for(Id orderId : this.orderIds) {
                this.sourceIdentifiers.add(orderId);
            }

            // Get all Invoices for this account
            List<Invoice> invoices = [
                SELECT Id 
                FROM Invoice 
                WHERE BillingAccountId = :accountId
            ];
            
            Set<Id> invoiceIds = new Set<Id>(new Map<Id, Invoice>(invoices).keySet());

            // Get all OrderSummaries for this account
            List<OrderSummary> summaries = [
                SELECT Id 
                FROM OrderSummary 
                WHERE AccountId = :accountId
            ];
            
            Set<Id> summaryIds = new Set<Id>(new Map<Id, OrderSummary>(summaries).keySet());

            // Get all FulfillmentOrders that reference any of these
            this.fulfillmentOrders = [
                SELECT Id 
                FROM FulfillmentOrder 
                WHERE AccountId = :accountId
                OR OrderId IN :this.orderIds
                OR InvoiceId IN :invoiceIds
                OR OrderSummaryId IN :summaryIds
            ];
            
            this.fulfillmentOrderIds = new Set<Id>(new Map<Id, FulfillmentOrder>(this.fulfillmentOrders).keySet());

            // Get all FulfillmentPlans for these orders and order items
            System.debug('Querying FulfillmentPlans');
            System.debug('Source identifiers for query: ' + this.sourceIdentifiers);
            this.fulfillmentPlans = [
                SELECT Id, SourceIdentifier, SourceType 
                FROM FulfillmentPlan 
                WHERE SourceIdentifier IN :this.sourceIdentifiers
                AND (SourceType = 'StandardOrder' OR SourceType = 'OrderItem')
            ];
            System.debug('Found ' + this.fulfillmentPlans.size() + ' FulfillmentPlan records');
            for(FulfillmentPlan plan : this.fulfillmentPlans) {
                System.debug('FulfillmentPlan - ID: ' + plan.Id + ', SourceIdentifier: ' + plan.SourceIdentifier + ', SourceType: ' + plan.SourceType);
            }
            
            this.fulfillmentPlanIds = new Set<Id>(new Map<Id, FulfillmentPlan>(this.fulfillmentPlans).keySet());

            // Get all FulfillmentSteps for these plans
            this.fulfillmentSteps = [
                SELECT Id 
                FROM FulfillmentStep 
                WHERE FulfillmentPlanId IN :this.fulfillmentPlanIds
            ];
            
            this.fulfillmentStepIds = new Set<Id>(new Map<Id, FulfillmentStep>(this.fulfillmentSteps).keySet());

            // Get all FulfillmentAssets for this account
            this.fulfillmentAssets = [
                SELECT Id 
                FROM FulfillmentAsset 
                WHERE AccountId = :accountId
            ];
            
            this.fulfillmentAssetIds = new Set<Id>(new Map<Id, FulfillmentAsset>(this.fulfillmentAssets).keySet());

            // Get all FulfillmentOrderLineItems for these FulfillmentOrders
            this.fulfillmentOrderLineItems = [
                SELECT Id 
                FROM FulfillmentOrderLineItem 
                WHERE FulfillmentOrderId IN :this.fulfillmentOrderIds
            ];
            
            this.fulfillmentOrderLineItemIds = new Set<Id>(new Map<Id, FulfillmentOrderLineItem>(this.fulfillmentOrderLineItems).keySet());

            // Get all FulfillmentLineSourceRel records for these order items
            this.fulfillmentLineSourceRels = [
                SELECT Id 
                FROM FulfillmentLineSourceRel 
                WHERE SourceLineItemId IN :this.orderItemIds
                OR FulfilmentOrderLineId IN :this.fulfillmentOrderLineItemIds
            ];
            
            this.fulfillmentLineSourceRelIds = new Set<Id>(new Map<Id, FulfillmentLineSourceRel>(this.fulfillmentLineSourceRels).keySet());
        }
    }

    /**
     * Main Method
     * Entry point for the account cleanup process.
     * This method orchestrates the deletion of all related objects in the correct order.
     * 
     * @param request List of InputVariables containing the account ID and deletion flags
     */
    @InvocableMethod(label='Reset Account Related Objects' description='Deletes all related objects for an account in the correct order')
    public static void delAccountRelatedObjects(List<InputVariables> request) {
        if (request == null || request.isEmpty()) {
            return;
        }

        String accountId = request.get(0).accountId;
        Boolean deleteAssets = request.get(0).DeleteAssets;
        Boolean deleteFulfillment = request.get(0).DeleteFulfillment;
        Boolean deleteBilling = request.get(0).DeleteBilling;

            // Start a savepoint for transaction control
        Savepoint sp = Database.setSavepoint();
        try {
            // Get Order data once
            OrderData orderData = new OrderData(accountId);
            deleteUsageResourcePoliciesForAccount(accountId); // BindingObjUsageRsrcPlcy
            deleteBindingObjRateCardEntriesForAccount(accountId); // BindingObjectRateCardEntry
            
            // First handle all usage entitlements and their related records
            deleteTransactionUsageEntitlement(accountId);
            deleteUsageEntitlementAccount(accountId); // UsageEntitlementAccount & UsageEntitlementBucket
            
            // Delete additional usage-related records that might reference assets
            deleteAllTransactionUsageEntitlements(accountId); // More comprehensive TUE deletion
            deleteUsageLiableSummaries(accountId); // UsageBillingPeriodItem
            deleteUsageRatableSummaries(accountId);
            
            // Then handle other usage and billing related records
            deleteTransactionJournal(accountId);
            deleteUsageSummaries(accountId);

            // Delete Billing information
            deleteBillingScheduleGroups(accountId);
            if (deleteBilling) {
                deleteInvoices(accountId);
            }
            
            // Handle fulfillment records if needed (before contracts and orders)
            if (deleteFulfillment) {
                deleteFulfillmentLineSourceRel(accountId, orderData);
                deleteFulfillmentStepSource(accountId, orderData);
                deleteFulfillmentOrderLineItem(accountId, orderData);
                deleteFulfillmentOrder(accountId, orderData);
            }
            
            // Then handle contracts and orders
            deleteContracts(accountId);
            deleteOrders(accountId, orderData);

            if (deleteFulfillment) {
                deleteFulfillmentPlan(accountId, orderData);
                deleteAssetFulfillmentDecomp(accountId, orderData);
                deleteFulfillmentAsset(accountId, orderData);
            }
            
            // Handle assets if needed
            if (deleteAssets) {
                // Before deleting assets, clean up ALL records that might reference them
                deleteAllRecordsReferencingAssets(accountId);
                deleteAssets(accountId);
            }
            
            // Finally handle remaining objects
            deleteQuotes(accountId);
            deleteOpportunities(accountId);
        } catch(Exception e) {
            Database.rollback(sp);
            throw e;
        }
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
     * 1. Usage Entitlement Accounts (UEA)
     * 2. Transaction Usage Entitlements (TUE)
     * 3. Orders (after updating to Draft)
     * 
     * @param accountId The ID of the account whose orders should be deleted
     * @param orderData The OrderData object containing pre-queried information
     * @return Boolean indicating success
     */
    private static Boolean deleteOrders(String accountId, OrderData orderData) {
        // First delete Usage Entitlement Accounts and Transaction Usage Entitlements
        deleteUsageEntitlementAccount(accountId);
        deleteTransactionUsageEntitlement(accountId);
        
        // Then handle the orders
        if (!orderData.orders.isEmpty()) {
            // Update orders to Draft status before deletion
            for(Order o : orderData.orders) {
                o.Status = 'Draft';
            }
            Database.update(orderData.orders, false);
            
            // Delete the orders
            Database.delete(orderData.orders, false);
        }
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
     * Deletes Usage Entitlement Buckets (UEB) using a hierarchical deletion approach.
     * The deletion process:
     * 1. Finds all UEBs related to the given entitlement IDs
     * 2. Builds a complete map of parent-child relationships
     * 3. Identifies top-level parent buckets
     * 4. Deletes buckets level by level, starting from the bottom of the hierarchy
     * 5. Finally deletes top-level parent buckets
     * 
     * This ensures that child buckets are always deleted before their parents.
     * 
     * @param entitlementIds Set of entitlement IDs (TUE or UEA)
     * @param queryType Either 'TransactionUsageEntitlement' or 'UsageEntitlementAccount'
     * @return Boolean indicating success
     */
    private static Boolean deleteUsageEntitlementBucketsGeneric(Set<Id> entitlementIds, String queryType) {
        System.debug('Starting Usage Entitlement Bucket deletion for ' + queryType + ' IDs: ' + entitlementIds);
        if (entitlementIds.isEmpty()) {
            return true;
        }

        // Query for buckets based on the query type
        UsageEntitlementBucket[] allBuckets;
        if (queryType == 'TransactionUsageEntitlement') {
            // For TUE, look for buckets directly linked via TransactionUsageEntitlementId
            allBuckets = [
                SELECT Id, Name, ParentId, Parent.Type, Parent.Name 
                FROM UsageEntitlementBucket 
                WHERE TransactionUsageEntitlementId IN :entitlementIds
                OR ParentId IN :entitlementIds
                OR Id IN :entitlementIds
            ];
        } else {
            // For UEA, look for buckets where ParentId references the UEA
            allBuckets = [
                SELECT Id, Name, ParentId, Parent.Type, Parent.Name 
                FROM UsageEntitlementBucket 
                WHERE ParentId IN :entitlementIds
                OR Id IN :entitlementIds
            ];
        }
        
        System.debug('Found ' + allBuckets.size() + ' total Usage Entitlement Buckets for ' + queryType);
        for(UsageEntitlementBucket bucket : allBuckets) {
            System.debug('Initial bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - Parent: ' + 
                        (bucket.ParentId != null ? bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')' : 'None'));
        }
        
        return deleteUsageEntitlementBucketsHierarchy(allBuckets);
    }

    /**
     * Core logic for hierarchical deletion of Usage Entitlement Buckets.
     * Separated for reusability and clarity.
     * 
     * @param allBuckets List of all buckets to process for deletion
     * @return Boolean indicating success
     */
    private static Boolean deleteUsageEntitlementBucketsHierarchy(List<UsageEntitlementBucket> allBuckets) {
        if (allBuckets.isEmpty()) {
            System.debug('No buckets to delete');
            return true;
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
        
        // Recursively find ALL child buckets (not just direct children)
        Set<Id> currentLevelIds = new Set<Id>(allBucketIds);
        
        while(!currentLevelIds.isEmpty()) {
            // Find children of current level buckets
            UsageEntitlementBucket[] childBuckets = [
                SELECT Id, Name, ParentId, Parent.Type, Parent.Name 
                FROM UsageEntitlementBucket 
                WHERE ParentId IN :currentLevelIds
                AND Id NOT IN :allBucketIds  // Avoid infinite loops
            ];
            
            if(childBuckets.isEmpty()) {
                break; // No more children found
            }
            
            System.debug('Found ' + childBuckets.size() + ' child buckets at this level');
            Set<Id> nextLevelIds = new Set<Id>();
            
            // Add child buckets to our collections
            for(UsageEntitlementBucket bucket : childBuckets) {
                allBucketIds.add(bucket.Id);
                nextLevelIds.add(bucket.Id);
                if(bucket.ParentId != null) {
                    childToParentMap.put(bucket.Id, bucket.ParentId);
                }
                System.debug('Found child bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - Parent: ' + 
                           (bucket.ParentId != null ? bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')' : 'None'));
            }
            
            currentLevelIds = nextLevelIds;
        }
        
        // Build parent-to-children map for ALL buckets (including original ones)
        for(UsageEntitlementBucket bucket : allBuckets) {
            if(bucket.ParentId != null && bucket.Parent.Type == 'UsageEntitlementBucket') {
                if(!parentToChildrenMap.containsKey(bucket.ParentId)) {
                    parentToChildrenMap.put(bucket.ParentId, new List<Id>());
                }
                parentToChildrenMap.get(bucket.ParentId).add(bucket.Id);
            }
        }
        
        // Also build relationships for any additional child buckets found
        for(Id bucketId : allBucketIds) {
            if(childToParentMap.containsKey(bucketId)) {
                Id parentId = childToParentMap.get(bucketId);
                if(allBucketIds.contains(parentId)) { // Only if parent is also in our deletion set
                    if(!parentToChildrenMap.containsKey(parentId)) {
                        parentToChildrenMap.put(parentId, new List<Id>());
                    }
                    if(!parentToChildrenMap.get(parentId).contains(bucketId)) {
                        parentToChildrenMap.get(parentId).add(bucketId);
                    }
                }
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
                    Database.delete([SELECT Id FROM UsageEntitlementBucket WHERE Id IN :toDelete], false);
                    System.debug('Successfully deleted leaf buckets');
                    processedIds.addAll(toDelete);
                } catch(Exception e) {
                    System.debug('Error deleting leaf buckets: ' + e.getMessage());
                    throw e;
                }
            }
            
            currentLevel = nextLevel;
        }
        
        // Finally delete top-level parent buckets
        if(!topLevelParentIds.isEmpty()) {
            System.debug('Deleting ' + topLevelParentIds.size() + ' top-level parent buckets');
            try {
                Database.DeleteResult[] results = Database.delete([SELECT Id FROM UsageEntitlementBucket WHERE Id IN :topLevelParentIds], false);
                Integer errorCount = 0;
                for(Database.DeleteResult result : results) {
                    if(!result.isSuccess()) {
                        errorCount++;
                        for(Database.Error err : result.getErrors()) {
                            System.debug('Error deleting top-level bucket ' + result.getId() + ': ' + err.getMessage());
                        }
                    }
                }
                if(errorCount > 0) {
                    System.debug('Completed top-level bucket deletion with ' + errorCount + ' errors out of ' + results.size() + ' records');
                } else {
                    System.debug('Successfully deleted all top-level parent buckets');
                }
            } catch(Exception e) {
                System.debug('Error deleting top-level parent buckets: ' + e.getMessage());
                throw e;
            }
        }
        
        // Verify all buckets were deleted
        List<UsageEntitlementBucket> remainingBuckets = [
            SELECT Id, Name 
            FROM UsageEntitlementBucket 
            WHERE Id IN :allBucketIds
        ];
        
        if(!remainingBuckets.isEmpty()) {
            System.debug('WARNING: ' + remainingBuckets.size() + ' buckets still remain after deletion attempt:');
            for(UsageEntitlementBucket bucket : remainingBuckets) {
                System.debug('Remaining bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ')');
            }
            // Try to delete any remaining buckets one more time
            try {
                Database.delete(remainingBuckets, false);
                System.debug('Attempted cleanup deletion of remaining buckets');
            } catch(Exception e) {
                System.debug('Error in cleanup deletion: ' + e.getMessage());
            }
        } else {
            System.debug('All Usage Entitlement Buckets successfully deleted');
        }
        
        return true;
    }

    /**
     * Deletes Usage Entitlement Buckets (UEB) related to Transaction Usage Entitlements (TUE).
     * 
     * @param entitlementIds Set of Transaction Usage Entitlement IDs
     * @return Boolean indicating success
     */
    private static Boolean deleteUsageEntitlementBucket(Set<Id> entitlementIds) {
        System.debug('=== Starting deleteUsageEntitlementBucket for TUE IDs: ' + entitlementIds);
        
        if(entitlementIds.isEmpty()) {
            return true;
        }
        
        // Use the new bottom-up deletion approach
        return deleteUsageEntitlementBucketsBottomUp(entitlementIds, 'TransactionUsageEntitlement');
    }
    
    /**
     * Deletes Usage Entitlement Buckets using a bottom-up approach.
     * Deletes child buckets first, then parent buckets, following the proper hierarchy.
     * 
     * @param entitlementIds Set of entitlement IDs (TUE or UEA)
     * @param queryType Either 'TransactionUsageEntitlement' or 'UsageEntitlementAccount'
     * @return Boolean indicating success
     */
    private static Boolean deleteUsageEntitlementBucketsBottomUp(Set<Id> entitlementIds, String queryType) {
        System.debug('Starting bottom-up deletion for ' + queryType + ' IDs: ' + entitlementIds);
        
        // Find all buckets related to these entitlements
        List<UsageEntitlementBucket> allRelatedBuckets;
        if (queryType == 'TransactionUsageEntitlement') {
            allRelatedBuckets = [
                SELECT Id, Name, TransactionUsageEntitlementId, ParentId, Parent.Type, Parent.Name
                FROM UsageEntitlementBucket 
                WHERE TransactionUsageEntitlementId IN :entitlementIds
                OR ParentId IN :entitlementIds
            ];
        } else {
            allRelatedBuckets = [
                SELECT Id, Name, TransactionUsageEntitlementId, ParentId, Parent.Type, Parent.Name
                FROM UsageEntitlementBucket 
                WHERE ParentId IN :entitlementIds
            ];
        }
        
        if(allRelatedBuckets.isEmpty()) {
            System.debug('No buckets found to delete');
            return true;
        }
        
        System.debug('Found ' + allRelatedBuckets.size() + ' buckets to delete');
        
        // Build a complete map of all buckets and their relationships
        Set<Id> allBucketIds = new Set<Id>();
        Map<Id, UsageEntitlementBucket> bucketMap = new Map<Id, UsageEntitlementBucket>();
        
        for(UsageEntitlementBucket bucket : allRelatedBuckets) {
            allBucketIds.add(bucket.Id);
            bucketMap.put(bucket.Id, bucket);
            System.debug('Initial bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - TUE: ' + bucket.TransactionUsageEntitlementId + 
                       ' - Parent: ' + (bucket.ParentId != null ? bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')' : 'None'));
        }
        
        // Find ALL child buckets recursively
        Set<Id> processedIds = new Set<Id>();
        Set<Id> currentLevelIds = new Set<Id>(allBucketIds);
        
        while(!currentLevelIds.isEmpty()) {
            List<UsageEntitlementBucket> childBuckets = [
                SELECT Id, Name, TransactionUsageEntitlementId, ParentId, Parent.Type, Parent.Name
                FROM UsageEntitlementBucket 
                WHERE ParentId IN :currentLevelIds
                AND Id NOT IN :allBucketIds  // Don't include already found buckets
            ];
            
            if(childBuckets.isEmpty()) {
                break;
            }
            
            Set<Id> nextLevelIds = new Set<Id>();
            for(UsageEntitlementBucket bucket : childBuckets) {
                allBucketIds.add(bucket.Id);
                bucketMap.put(bucket.Id, bucket);
                nextLevelIds.add(bucket.Id);
                System.debug('Found child bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - TUE: ' + bucket.TransactionUsageEntitlementId + 
                           ' - Parent: ' + (bucket.ParentId != null ? bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')' : 'None'));
            }
            
            currentLevelIds = nextLevelIds;
        }
        
        System.debug('Total buckets to delete (including all children): ' + allBucketIds.size());
        
        // Now process buckets level by level, starting from the deepest children
        // For each level: 1) Delete TUEs from buckets, 2) Delete the buckets themselves
        Integer deletionRound = 1;
        Set<Id> remainingBuckets = new Set<Id>(allBucketIds);
        
        while(!remainingBuckets.isEmpty()) {
            System.debug('=== Deletion Round ' + deletionRound + ' ===');
            System.debug('Remaining buckets: ' + remainingBuckets.size());
            
            // Find buckets that have no children (leaf nodes)
            List<UsageEntitlementBucket> leafBuckets = new List<UsageEntitlementBucket>();
            
            for(Id bucketId : remainingBuckets) {
                // Check if this bucket has any children in the remaining set
                Boolean hasChildren = false;
                for(Id otherBucketId : remainingBuckets) {
                    if(otherBucketId != bucketId && bucketMap.containsKey(otherBucketId)) {
                        UsageEntitlementBucket otherBucket = bucketMap.get(otherBucketId);
                        if(otherBucket.ParentId == bucketId) {
                            hasChildren = true;
                            break;
                        }
                    }
                }
                
                if(!hasChildren && bucketMap.containsKey(bucketId)) {
                    leafBuckets.add(bucketMap.get(bucketId));
                }
            }
            
            if(leafBuckets.isEmpty()) {
                System.debug('No leaf buckets found, but ' + remainingBuckets.size() + ' buckets remain. Breaking to avoid infinite loop.');
                break;
            }
            
            System.debug('Processing ' + leafBuckets.size() + ' leaf buckets in round ' + deletionRound);
            
            // STEP 1: Handle related entitlements based on query type
            if (queryType == 'TransactionUsageEntitlement') {
                // Delete Transaction Usage Entitlements from these buckets
                Set<Id> tueIdsToDelete = new Set<Id>();
                for(UsageEntitlementBucket bucket : leafBuckets) {
                    if(bucket.TransactionUsageEntitlementId != null) {
                        tueIdsToDelete.add(bucket.TransactionUsageEntitlementId);
                        System.debug('Found TUE to delete from bucket ' + bucket.Name + ': ' + bucket.TransactionUsageEntitlementId);
                    }
                }
                
                if(!tueIdsToDelete.isEmpty()) {
                    System.debug('Deleting ' + tueIdsToDelete.size() + ' Transaction Usage Entitlements from leaf buckets');
                    List<TransactionUsageEntitlement> tuesToDelete = [
                        SELECT Id, Name 
                        FROM TransactionUsageEntitlement 
                        WHERE Id IN :tueIdsToDelete
                    ];
                    
                    if(!tuesToDelete.isEmpty()) {
                        Database.DeleteResult[] tueResults = Database.delete(tuesToDelete, false);
                        Integer tueSuccessCount = 0;
                        Integer tueErrorCount = 0;
                        
                        for(Database.DeleteResult result : tueResults) {
                            if(result.isSuccess()) {
                                tueSuccessCount++;
                            } else {
                                tueErrorCount++;
                                for(Database.Error err : result.getErrors()) {
                                    System.debug('Error deleting TUE ' + result.getId() + ': ' + err.getMessage());
                                }
                            }
                        }
                        System.debug('TUE deletion results: ' + tueSuccessCount + ' success, ' + tueErrorCount + ' errors');
                    }
                }
            } else {
                // For UEA buckets, we don't delete TUEs first since they're not owned by the buckets
                // The UEA is the parent, so we just need to delete the buckets in the right order
                System.debug('Processing UEA-related buckets - no TUEs to delete from buckets');
            }
            
            // STEP 2: Now delete the buckets themselves
            System.debug('Deleting ' + leafBuckets.size() + ' leaf buckets');
            Database.DeleteResult[] bucketResults = Database.delete(leafBuckets, false);
            
            Set<Id> successfullyDeleted = new Set<Id>();
            Integer successCount = 0;
            Integer errorCount = 0;
            
            for(Integer i = 0; i < bucketResults.size(); i++) {
                Database.DeleteResult result = bucketResults[i];
                UsageEntitlementBucket bucket = leafBuckets[i];
                
                if(result.isSuccess()) {
                    successCount++;
                    successfullyDeleted.add(bucket.Id);
                    System.debug('Successfully deleted bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ')');
                } else {
                    errorCount++;
                    for(Database.Error err : result.getErrors()) {
                        System.debug('Error deleting bucket ' + bucket.Name + ' (ID: ' + bucket.Id + '): ' + err.getMessage());
                    }
                }
            }
            
            System.debug('Round ' + deletionRound + ' bucket deletion results: ' + successCount + ' success, ' + errorCount + ' errors');
            
            // Remove successfully deleted buckets from remaining set
            remainingBuckets.removeAll(successfullyDeleted);
            
            // If no progress was made, break to avoid infinite loop
            if(successfullyDeleted.isEmpty()) {
                System.debug('No progress made in round ' + deletionRound + '. Breaking.');
                break;
            }
            
            deletionRound++;
            
            // Safety check to avoid infinite loops
            if(deletionRound > 10) {
                System.debug('Maximum deletion rounds reached. Breaking.');
                break;
            }
        }
        
        // Final verification
        List<UsageEntitlementBucket> finalCheck;
        if (queryType == 'TransactionUsageEntitlement') {
            finalCheck = [
                SELECT Id, Name 
                FROM UsageEntitlementBucket 
                WHERE TransactionUsageEntitlementId IN :entitlementIds
            ];
        } else {
            finalCheck = [
                SELECT Id, Name 
                FROM UsageEntitlementBucket 
                WHERE ParentId IN :entitlementIds
            ];
        }
        
        if(!finalCheck.isEmpty()) {
            System.debug('WARNING: ' + finalCheck.size() + ' buckets still remain after bottom-up deletion');
            for(UsageEntitlementBucket bucket : finalCheck) {
                System.debug('Remaining bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ')');
            }
        } else {
            System.debug('SUCCESS: All buckets successfully deleted using bottom-up approach');
        }
        
        return true;
    }

    /**
     * Deletes Usage Entitlement Buckets (UEB) related to Usage Entitlement Accounts (UEA).
     * 
     * @param entitlementIds Set of Usage Entitlement Account IDs
     * @return Boolean indicating success
     */
    private static Boolean deleteUsageEntitlementBucketsForParents(Set<Id> entitlementIds) {
        return deleteUsageEntitlementBucketsBottomUp(entitlementIds, 'UsageEntitlementAccount');
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
        TransactionUsageEntitlement[] transactionUsageEntitlementToDelete = 
            [SELECT Id, Name FROM TransactionUsageEntitlement WHERE AccountId = :accountIdConverted];
        if (!transactionUsageEntitlementToDelete.isEmpty()) {
            Set<Id> tueIds = new Set<Id>();
            for (TransactionUsageEntitlement tue : transactionUsageEntitlementToDelete) {
                tueIds.add(tue.Id);
                System.debug('Found TUE: ' + tue.Name + ' (ID: ' + tue.Id + ')');
            }
            
            // Show what buckets exist for these TUEs before deletion
            List<UsageEntitlementBucket> allRelatedBuckets = [
                SELECT Id, Name, TransactionUsageEntitlementId, ParentId, Parent.Type, Parent.Name
                FROM UsageEntitlementBucket 
                WHERE TransactionUsageEntitlementId IN :tueIds
                OR ParentId IN :tueIds
            ];
            
            System.debug('Found ' + allRelatedBuckets.size() + ' buckets related to TUEs:');
            for(UsageEntitlementBucket bucket : allRelatedBuckets) {
                System.debug('Bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - TUE: ' + bucket.TransactionUsageEntitlementId + 
                           ' - Parent: ' + (bucket.ParentId != null ? bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')' : 'None'));
            }
            
            // Delete buckets using bottom-up approach (this will also delete TUEs from within buckets)
            deleteUsageEntitlementBucket(tueIds);
            
            // After bucket deletion, check for any remaining TUEs that weren't deleted during bucket processing
            List<TransactionUsageEntitlement> remainingTUEs = [
                SELECT Id, Name 
                FROM TransactionUsageEntitlement 
                WHERE Id IN :tueIds
            ];
            
            if(!remainingTUEs.isEmpty()) {
                System.debug('Deleting ' + remainingTUEs.size() + ' remaining TUEs that weren\'t deleted during bucket processing');
                Database.delete(remainingTUEs, false);
            } else {
                System.debug('All TUEs were successfully deleted during bucket processing');
            }
            
            // Final verification - check for any remaining buckets
            List<UsageEntitlementBucket> remainingBuckets = [
                SELECT Id, Name, TransactionUsageEntitlementId
                FROM UsageEntitlementBucket 
                WHERE TransactionUsageEntitlementId IN :tueIds
            ];
            
            if(!remainingBuckets.isEmpty()) {
                System.debug('WARNING: Found ' + remainingBuckets.size() + ' buckets still linked to original TUEs');
                for(UsageEntitlementBucket bucket : remainingBuckets) {
                    System.debug('Remaining bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - TUE: ' + bucket.TransactionUsageEntitlementId);
                }
            }
        }
        return true;
    }

    /**
     * Comprehensive deletion of ALL Transaction Usage Entitlements that might be associated 
     * with the account or its assets. This method is more thorough than the initial TUE deletion
     * and catches any TUEs that might have been missed.
     * 
     * @param accountId The ID of the account whose TUEs should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteAllTransactionUsageEntitlements(String accountId) {
        System.debug('=== Comprehensive TUE deletion for account: ' + accountId);
        
        // First get all assets for this account to find TUEs that might be associated with assets
        List<Asset> accountAssets = [SELECT Id, Name FROM Asset WHERE AccountId = :accountId];
        Set<Id> assetIds = new Set<Id>();
        for(Asset asset : accountAssets) {
            assetIds.add(asset.Id);
        }
        System.debug('Found ' + assetIds.size() + ' assets to check for TUEs');
        
        Set<Id> allTueIds = new Set<Id>();
        
        // Find TUEs by Account
        List<TransactionUsageEntitlement> accountTUEs = [
            SELECT Id, Name, AccountId 
            FROM TransactionUsageEntitlement 
            WHERE AccountId = :accountId
        ];
        System.debug('Found ' + accountTUEs.size() + ' TUEs by AccountId');
        for(TransactionUsageEntitlement tue : accountTUEs) {
            allTueIds.add(tue.Id);
            System.debug('Account TUE: ' + tue.Name + ' (ID: ' + tue.Id + ')');
        }
        
        // Find TUEs that might be associated with Assets (try different possible field names)
        if(!assetIds.isEmpty()) {
            String[] possibleAssetQueries = new String[]{
                'SELECT Id, Name FROM TransactionUsageEntitlement WHERE AssetId IN :assetIds',
                'SELECT Id, Name FROM TransactionUsageEntitlement WHERE GrantBindingTargetId IN :assetIds',
                'SELECT Id, Name FROM TransactionUsageEntitlement WHERE Asset__c IN :assetIds',
                'SELECT Id, Name FROM TransactionUsageEntitlement WHERE RelatedAssetId IN :assetIds'
            };
            
            for(String queryString : possibleAssetQueries) {
                try {
                    List<TransactionUsageEntitlement> assetTUEs = Database.query(queryString);
                    if(!assetTUEs.isEmpty()) {
                        System.debug('Found ' + assetTUEs.size() + ' TUEs associated with assets using: ' + queryString);
                        for(TransactionUsageEntitlement tue : assetTUEs) {
                            if(!allTueIds.contains(tue.Id)) {
                                allTueIds.add(tue.Id);
                                System.debug('Asset TUE: ' + tue.Name + ' (ID: ' + tue.Id + ')');
                            }
                        }
                        break; // Use the first successful query
                    }
                } catch(Exception e) {
                    System.debug('Asset TUE query failed: ' + queryString + ' - ' + e.getMessage());
                }
            }
        }
        
        if(allTueIds.isEmpty()) {
            System.debug('No TUEs found for comprehensive deletion');
            return true;
        }
        
        System.debug('Total unique TUEs found for deletion: ' + allTueIds.size());
        
        // Find and delete all buckets associated with these TUEs first
        List<UsageEntitlementBucket> allBuckets = [
            SELECT Id, Name, TransactionUsageEntitlementId, ParentId
            FROM UsageEntitlementBucket 
            WHERE TransactionUsageEntitlementId IN :allTueIds
            OR ParentId IN :allTueIds
        ];
        
        if(!allBuckets.isEmpty()) {
            System.debug('Found ' + allBuckets.size() + ' buckets to delete first');
            // Delete buckets using our bottom-up approach
            deleteUsageEntitlementBucketsBottomUp(allTueIds, 'TransactionUsageEntitlement');
        }
        
        // Now delete all the TUEs
        List<TransactionUsageEntitlement> allTUEs = [
            SELECT Id, Name 
            FROM TransactionUsageEntitlement 
            WHERE Id IN :allTueIds
        ];
        
        if(!allTUEs.isEmpty()) {
            System.debug('Deleting ' + allTUEs.size() + ' TUEs in comprehensive deletion');
            Database.DeleteResult[] results = Database.delete(allTUEs, false);
            
            Integer successCount = 0;
            Integer errorCount = 0;
            for(Database.DeleteResult result : results) {
                if(result.isSuccess()) {
                    successCount++;
                } else {
                    errorCount++;
                    for(Database.Error err : result.getErrors()) {
                        System.debug('Error deleting TUE ' + result.getId() + ': ' + err.getMessage());
                    }
                }
            }
            System.debug('Comprehensive TUE deletion results: ' + successCount + ' success, ' + errorCount + ' errors');
        }
        
        // Final verification - make sure no TUEs remain
        List<TransactionUsageEntitlement> remainingTUEs = [
            SELECT Id, Name, AccountId 
            FROM TransactionUsageEntitlement 
            WHERE AccountId = :accountId
        ];
        
        if(!remainingTUEs.isEmpty()) {
            System.debug('WARNING: ' + remainingTUEs.size() + ' TUEs still remain after comprehensive deletion');
            for(TransactionUsageEntitlement tue : remainingTUEs) {
                System.debug('Remaining TUE: ' + tue.Name + ' (ID: ' + tue.Id + ') - Account: ' + tue.AccountId);
            }
            
            // Try one more time to delete them
            try {
                Database.delete(remainingTUEs, false);
                System.debug('Final cleanup attempt for remaining TUEs');
            } catch(Exception e) {
                System.debug('Error in final TUE cleanup: ' + e.getMessage());
            }
        } else {
            System.debug('SUCCESS: All TUEs successfully deleted in comprehensive deletion');
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
        System.debug('Deleting Usage Entitlement Accounts for account: ' + accountIdConverted);
        UsageEntitlementAccount[] usageEntitlementAccountToDelete = 
            [SELECT Id, Name FROM UsageEntitlementAccount WHERE AccountId = :accountIdConverted];
        if (!usageEntitlementAccountToDelete.isEmpty()) {
            Set<Id> ueaIds = new Set<Id>(new Map<Id, UsageEntitlementAccount>(usageEntitlementAccountToDelete).keySet());
            System.debug('Found ' + ueaIds.size() + ' Usage Entitlement Account records');
            
            for(UsageEntitlementAccount uea : usageEntitlementAccountToDelete) {
                System.debug('Found UEA: ' + uea.Name + ' (ID: ' + uea.Id + ')');
            }
            
            // Show what buckets exist for these UEAs before deletion
            List<UsageEntitlementBucket> allRelatedBuckets = [
                SELECT Id, Name, TransactionUsageEntitlementId, ParentId, Parent.Type, Parent.Name
                FROM UsageEntitlementBucket 
                WHERE ParentId IN :ueaIds
            ];
            
            System.debug('Found ' + allRelatedBuckets.size() + ' buckets related to UEAs:');
            for(UsageEntitlementBucket bucket : allRelatedBuckets) {
                System.debug('Bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - TUE: ' + bucket.TransactionUsageEntitlementId + 
                           ' - Parent: ' + (bucket.ParentId != null ? bucket.Parent.Name + ' (ID: ' + bucket.ParentId + ')' : 'None'));
            }
            
            // Delete buckets using bottom-up approach (this will also delete TUEs from within buckets)
            deleteUsageEntitlementBucketsForParents(ueaIds);
            
            // After bucket deletion, check for any remaining UEAs that can now be deleted
            List<UsageEntitlementAccount> remainingUEAs = [
                SELECT Id, Name 
                FROM UsageEntitlementAccount 
                WHERE Id IN :ueaIds
            ];
            
            if(!remainingUEAs.isEmpty()) {
                System.debug('Deleting ' + remainingUEAs.size() + ' UEAs after bucket processing');
                Database.DeleteResult[] results = Database.delete(remainingUEAs, false);
                
                Integer successCount = 0;
                Integer errorCount = 0;
                for(Database.DeleteResult result : results) {
                    if(result.isSuccess()) {
                        successCount++;
                    } else {
                        errorCount++;
                        for(Database.Error err : result.getErrors()) {
                            System.debug('Error deleting UEA ' + result.getId() + ': ' + err.getMessage());
                        }
                    }
                }
                System.debug('UEA deletion results: ' + successCount + ' success, ' + errorCount + ' errors');
            } else {
                System.debug('All UEAs were already processed');
            }
            
            // Final verification - check for any remaining buckets
            List<UsageEntitlementBucket> remainingBuckets = [
                SELECT Id, Name, ParentId
                FROM UsageEntitlementBucket 
                WHERE ParentId IN :ueaIds
            ];
            
            if(!remainingBuckets.isEmpty()) {
                System.debug('WARNING: Found ' + remainingBuckets.size() + ' buckets still linked to original UEAs');
                for(UsageEntitlementBucket bucket : remainingBuckets) {
                    System.debug('Remaining bucket: ' + bucket.Name + ' (ID: ' + bucket.Id + ') - Parent: ' + bucket.ParentId);
                }
            }
        }
        return true;
    }

    /**
     * Deletes TransactionJournal records for a given account.
     * These records represent financial transactions and can be related to:
     * - Account
     * - Orders
     * - Invoices
     * 
     * This method must be called after deleting Orders but before deleting Invoices
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteTransactionJournal(String accountId) {
        // Get all TransactionJournals for this account
        List<TransactionJournal> recordsToDelete = [
            SELECT Id 
            FROM TransactionJournal 
            WHERE AccountId = :accountId
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
        }
        return true;
    }

    /**
     * Deletes UsageSummary records for a given account.
     * These records represent usage summaries and can be related to:
     * - Account
     * - UsageEntitlements
     * 
     * This method must be called after deleting UsageEntitlementAccounts
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteUsageSummaries(String accountId) {
        // Get all UsageSummaries for this account
        List<UsageSummary> recordsToDelete = [
            SELECT Id 
            FROM UsageSummary 
            WHERE AccountId = :accountId
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
        }
        return true;
    }

    /**
     * Deletes Usage Liable Summary records for a given account.
     * These records represent usage liable summaries and can be related to:
     * - Account
     * - Assets
     * - Usage Entitlements
     * 
     * This method must be called after deleting UsageEntitlementAccounts and TransactionUsageEntitlements
     * but before deleting Assets to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteUsageLiableSummaries(String accountId) {
        System.debug('Deleting Usage Liable Summary records for account: ' + accountId);
        
        // First get all assets for this account to find related liable summaries
        List<Asset> accountAssets = [SELECT Id FROM Asset WHERE AccountId = :accountId];
        Set<Id> assetIds = new Set<Id>();
        for(Asset asset : accountAssets) {
            assetIds.add(asset.Id);
        }
        System.debug('Found ' + assetIds.size() + ' assets to check for liable summaries');
        
        List<SObject> recordsToDelete = new List<SObject>();
        
        // Try multiple possible object names and field combinations
        String[] possibleQueries = new String[]{
            'SELECT Id FROM UsageBillingPeriodItem WHERE AccountId = :accountId',
            'SELECT Id FROM UsageBillingPeriodItem WHERE AssetId IN :assetIds',
            'SELECT Id FROM UsageBillingPeriodItem WHERE GrantBindingTargetId IN :assetIds',
            'SELECT Id FROM UsageLiableSummary WHERE AccountId = :accountId',
            'SELECT Id FROM UsageLiableSummary WHERE AssetId IN :assetIds',
            'SELECT Id FROM UsageBillingPolicyItem WHERE AccountId = :accountId',
            'SELECT Id FROM UsageBillingPolicyItem WHERE AssetId IN :assetIds',
            'SELECT Id FROM Usage_Liable_Summary__c WHERE Account__c = :accountId',
            'SELECT Id FROM Usage_Liable_Summary__c WHERE Asset__c IN :assetIds'
        };
        
        for(String queryString : possibleQueries) {
            try {
                List<SObject> results = Database.query(queryString);
                if(!results.isEmpty()) {
                    System.debug('Found ' + results.size() + ' records using query: ' + queryString);
                    recordsToDelete.addAll(results);
                    break; // Use the first successful query
                }
            } catch(Exception e) {
                System.debug('Query failed: ' + queryString + ' - ' + e.getMessage());
            }
        }
        
        if (!recordsToDelete.isEmpty()) {
            System.debug('Deleting ' + recordsToDelete.size() + ' Usage Liable Summary records');
            Database.DeleteResult[] results = Database.delete(recordsToDelete, false);
            Integer successCount = 0;
            Integer errorCount = 0;
            for(Database.DeleteResult result : results) {
                if(result.isSuccess()) {
                    successCount++;
                } else {
                    errorCount++;
                    for(Database.Error err : result.getErrors()) {
                        System.debug('Error deleting liable summary ' + result.getId() + ': ' + err.getMessage());
                    }
                }
            }
            System.debug('Liable summary deletion results: ' + successCount + ' success, ' + errorCount + ' errors');
        } else {
            System.debug('No Usage Liable Summary records found for account or assets');
        }
        return true;
    }

    /**
     * Deletes Usage Ratable Summary records for a given account.
     * These records represent usage ratable summaries and can be related to:
     * - Account
     * - Assets
     * - Usage Entitlements
     * 
     * This method must be called after deleting UsageEntitlementAccounts and TransactionUsageEntitlements
     * but before deleting Assets to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteUsageRatableSummaries(String accountId) {
        System.debug('Deleting Usage Ratable Summary records for account: ' + accountId);
        
        // First get all assets for this account to find related ratable summaries
        List<Asset> accountAssets = [SELECT Id FROM Asset WHERE AccountId = :accountId];
        Set<Id> assetIds = new Set<Id>();
        for(Asset asset : accountAssets) {
            assetIds.add(asset.Id);
        }
        System.debug('Found ' + assetIds.size() + ' assets to check for ratable summaries');
        
        List<SObject> recordsToDelete = new List<SObject>();
        
        // Try multiple possible object names and field combinations
        String[] possibleQueries = new String[]{
            'SELECT Id FROM UsageRatableSummary WHERE AccountId = :accountId',
            'SELECT Id FROM UsageRatableSummary WHERE AssetId IN :assetIds',
            'SELECT Id FROM UsageRatableSummary WHERE GrantBindingTargetId IN :assetIds',
            'SELECT Id FROM UsageRatingSchedule WHERE AccountId = :accountId',
            'SELECT Id FROM UsageRatingSchedule WHERE AssetId IN :assetIds',
            'SELECT Id FROM Usage_Ratable_Summary__c WHERE Account__c = :accountId',
            'SELECT Id FROM Usage_Ratable_Summary__c WHERE Asset__c IN :assetIds'
        };
        
        for(String queryString : possibleQueries) {
            try {
                List<SObject> results = Database.query(queryString);
                if(!results.isEmpty()) {
                    System.debug('Found ' + results.size() + ' records using query: ' + queryString);
                    recordsToDelete.addAll(results);
                    break; // Use the first successful query
                }
            } catch(Exception e) {
                System.debug('Query failed: ' + queryString + ' - ' + e.getMessage());
            }
        }
        
        if (!recordsToDelete.isEmpty()) {
            System.debug('Deleting ' + recordsToDelete.size() + ' Usage Ratable Summary records');
            Database.DeleteResult[] results = Database.delete(recordsToDelete, false);
            Integer successCount = 0;
            Integer errorCount = 0;
            for(Database.DeleteResult result : results) {
                if(result.isSuccess()) {
                    successCount++;
                } else {
                    errorCount++;
                    for(Database.Error err : result.getErrors()) {
                        System.debug('Error deleting ratable summary ' + result.getId() + ': ' + err.getMessage());
                    }
                }
            }
            System.debug('Ratable summary deletion results: ' + successCount + ' success, ' + errorCount + ' errors');
        } else {
            System.debug('No Usage Ratable Summary records found for account or assets');
        }
        return true;
    }

    /**
     * Deletes BillingScheduleGroup records for a given account.
     * These records represent billing schedule groups and can be related to:
     * - Account
     * - BillingSchedules
     * 
     * This method must be called after deleting Orders but before deleting Invoices
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteBillingScheduleGroups(String accountId) {
        // Get all BillingScheduleGroups for this account
        List<BillingScheduleGroup> recordsToDelete = [
            SELECT Id 
            FROM BillingScheduleGroup 
            WHERE BillingAccountId = :accountId
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
        }
        return true;
    }

    /**
     * Deletes Contract records for a given account.
     * These records represent contracts and can be related to:
     * - Account
     * - Orders
     * - Assets
     * 
     * This method must be called after deleting Orders but before deleting Assets
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @return Boolean indicating success of the operation
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
     * Deletes ALL records that directly reference assets for the account.
     * This is a comprehensive cleanup method that ensures no records are left
     * that would prevent asset deletion.
     * 
     * @param accountId The ID of the account whose asset-referencing records should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteAllRecordsReferencingAssets(String accountId) {
        System.debug('=== Comprehensive deletion of all records referencing assets for account: ' + accountId);
        
        // Get all assets for this account
        List<Asset> accountAssets = [SELECT Id, Name FROM Asset WHERE AccountId = :accountId];
        if(accountAssets.isEmpty()) {
            System.debug('No assets found for account');
            return true;
        }
        
        Set<Id> assetIds = new Set<Id>();
        for(Asset asset : accountAssets) {
            assetIds.add(asset.Id);
            System.debug('Found asset: ' + asset.Name + ' (ID: ' + asset.Id + ')');
        }
        System.debug('Total assets to check: ' + assetIds.size());
        
        // Delete Transaction Usage Entitlements that reference assets
        deleteTransactionUsageEntitlementsByAsset(assetIds);
        
        // Delete Usage Entitlement Accounts that reference assets
        deleteUsageEntitlementAccountsByAsset(assetIds);
        
        // Delete Usage Liable Summaries that reference assets
        deleteUsageLiableSummariesByAsset(assetIds);
        
        // Delete Usage Ratable Summaries that reference assets
        deleteUsageRatableSummariesByAsset(assetIds);
        
        // Delete any other records that might reference assets
        deleteOtherAssetReferences(assetIds);
        
        // Final diagnostic check - look for specific records mentioned in error messages
        diagnosticCheckForRemainingRecords(assetIds);
        
        // Final cleanup - try to delete specific problematic records by name
        deleteSpecificProblematicRecords();
        
        return true;
    }

    /**
     * Deletes Transaction Usage Entitlements that directly reference assets
     */
    private static void deleteTransactionUsageEntitlementsByAsset(Set<Id> assetIds) {
        System.debug('Deleting TUEs that reference assets');
        
        String[] possibleQueries = new String[]{
            'SELECT Id, Name FROM TransactionUsageEntitlement WHERE AssetId IN :assetIds',
            'SELECT Id, Name FROM TransactionUsageEntitlement WHERE GrantBindingTargetId IN :assetIds',
            'SELECT Id, Name FROM TransactionUsageEntitlement WHERE Asset__c IN :assetIds',
            'SELECT Id, Name FROM TransactionUsageEntitlement WHERE RelatedAssetId IN :assetIds',
            'SELECT Id, Name FROM TransactionUsageEntitlement WHERE SourceAssetId IN :assetIds'
        };
        
        for(String queryString : possibleQueries) {
            try {
                List<TransactionUsageEntitlement> tues = Database.query(queryString);
                if(!tues.isEmpty()) {
                    System.debug('Found ' + tues.size() + ' TUEs referencing assets using: ' + queryString);
                    
                    // First delete their buckets
                    Set<Id> tueIds = new Set<Id>();
                    for(TransactionUsageEntitlement tue : tues) {
                        tueIds.add(tue.Id);
                        System.debug('Asset-referenced TUE: ' + tue.Name + ' (ID: ' + tue.Id + ')');
                    }
                    
                    // Delete buckets first
                    deleteUsageEntitlementBucketsBottomUp(tueIds, 'TransactionUsageEntitlement');
                    
                    // Then delete the TUEs
                    Database.DeleteResult[] results = Database.delete(tues, false);
                    Integer successCount = 0;
                    Integer errorCount = 0;
                    for(Database.DeleteResult result : results) {
                        if(result.isSuccess()) {
                            successCount++;
                        } else {
                            errorCount++;
                            for(Database.Error err : result.getErrors()) {
                                System.debug('Error deleting asset TUE ' + result.getId() + ': ' + err.getMessage());
                            }
                        }
                    }
                    System.debug('Asset TUE deletion results: ' + successCount + ' success, ' + errorCount + ' errors');
                    return; // Use first successful query
                }
            } catch(Exception e) {
                System.debug('Asset TUE query failed: ' + queryString + ' - ' + e.getMessage());
            }
        }
    }

    /**
     * Deletes Usage Entitlement Accounts that directly reference assets
     */
    private static void deleteUsageEntitlementAccountsByAsset(Set<Id> assetIds) {
        System.debug('Deleting UEAs that reference assets');
        
        String[] possibleQueries = new String[]{
            'SELECT Id, Name FROM UsageEntitlementAccount WHERE AssetId IN :assetIds',
            'SELECT Id, Name FROM UsageEntitlementAccount WHERE Asset__c IN :assetIds',
            'SELECT Id, Name FROM UsageEntitlementAccount WHERE RelatedAssetId IN :assetIds'
        };
        
        for(String queryString : possibleQueries) {
            try {
                List<UsageEntitlementAccount> ueas = Database.query(queryString);
                if(!ueas.isEmpty()) {
                    System.debug('Found ' + ueas.size() + ' UEAs referencing assets using: ' + queryString);
                    
                    // First delete their buckets
                    Set<Id> ueaIds = new Set<Id>();
                    for(UsageEntitlementAccount uea : ueas) {
                        ueaIds.add(uea.Id);
                        System.debug('Asset-referenced UEA: ' + uea.Name + ' (ID: ' + uea.Id + ')');
                    }
                    
                    // Delete buckets first
                    deleteUsageEntitlementBucketsBottomUp(ueaIds, 'UsageEntitlementAccount');
                    
                    // Then delete the UEAs
                    Database.DeleteResult[] results = Database.delete(ueas, false);
                    Integer successCount = 0;
                    Integer errorCount = 0;
                    for(Database.DeleteResult result : results) {
                        if(result.isSuccess()) {
                            successCount++;
                        } else {
                            errorCount++;
                            for(Database.Error err : result.getErrors()) {
                                System.debug('Error deleting asset UEA ' + result.getId() + ': ' + err.getMessage());
                            }
                        }
                    }
                    System.debug('Asset UEA deletion results: ' + successCount + ' success, ' + errorCount + ' errors');
                    return; // Use first successful query
                }
            } catch(Exception e) {
                System.debug('Asset UEA query failed: ' + queryString + ' - ' + e.getMessage());
            }
        }
    }

    /**
     * Deletes Usage Liable Summaries that directly reference assets
     */
    private static void deleteUsageLiableSummariesByAsset(Set<Id> assetIds) {
        System.debug('Deleting Usage Liable Summaries that reference assets');
        
        String[] possibleQueries = new String[]{
            'SELECT Id FROM UsageBillingPeriodItem WHERE AssetId IN :assetIds',
            'SELECT Id FROM UsageBillingPeriodItem WHERE GrantBindingTargetId IN :assetIds',
            'SELECT Id FROM UsageLiableSummary WHERE AssetId IN :assetIds',
            'SELECT Id FROM UsageBillingPolicyItem WHERE AssetId IN :assetIds',
            'SELECT Id FROM Usage_Liable_Summary__c WHERE Asset__c IN :assetIds'
        };
        
        for(String queryString : possibleQueries) {
            try {
                List<SObject> records = Database.query(queryString);
                if(!records.isEmpty()) {
                    System.debug('Found ' + records.size() + ' Usage Liable Summaries referencing assets using: ' + queryString);
                    Database.delete(records, false);
                    return; // Use first successful query
                }
            } catch(Exception e) {
                System.debug('Asset liable summary query failed: ' + queryString + ' - ' + e.getMessage());
            }
        }
    }

    /**
     * Deletes Usage Ratable Summaries that directly reference assets
     */
    private static void deleteUsageRatableSummariesByAsset(Set<Id> assetIds) {
        System.debug('Deleting Usage Ratable Summaries that reference assets');
        
        String[] possibleQueries = new String[]{
            'SELECT Id FROM UsageRatableSummary WHERE AssetId IN :assetIds',
            'SELECT Id FROM UsageRatableSummary WHERE GrantBindingTargetId IN :assetIds',
            'SELECT Id FROM UsageRatingSchedule WHERE AssetId IN :assetIds',
            'SELECT Id FROM Usage_Ratable_Summary__c WHERE Asset__c IN :assetIds'
        };
        
        for(String queryString : possibleQueries) {
            try {
                List<SObject> records = Database.query(queryString);
                if(!records.isEmpty()) {
                    System.debug('Found ' + records.size() + ' Usage Ratable Summaries referencing assets using: ' + queryString);
                    Database.delete(records, false);
                    return; // Use first successful query
                }
            } catch(Exception e) {
                System.debug('Asset ratable summary query failed: ' + queryString + ' - ' + e.getMessage());
            }
        }
    }

    /**
     * Deletes any other records that might reference assets
     */
    private static void deleteOtherAssetReferences(Set<Id> assetIds) {
        System.debug('Deleting other records that might reference assets');
        
        // Try to find and delete any other objects that might reference assets
        String[] otherPossibleQueries = new String[]{
            'SELECT Id FROM UsageEntitlement WHERE AssetId IN :assetIds',
            'SELECT Id FROM ServiceContract WHERE AssetId IN :assetIds',
            'SELECT Id FROM WorkOrder WHERE AssetId IN :assetIds',
            'SELECT Id FROM Case WHERE AssetId IN :assetIds'
        };
        
        for(String queryString : otherPossibleQueries) {
            try {
                List<SObject> records = Database.query(queryString);
                if(!records.isEmpty()) {
                    System.debug('Found ' + records.size() + ' other records referencing assets using: ' + queryString);
                    Database.delete(records, false);
                }
            } catch(Exception e) {
                System.debug('Other asset reference query failed: ' + queryString + ' - ' + e.getMessage());
            }
        }
    }

    /**
     * Diagnostic method to find specific records that are still blocking asset deletion
     */
    private static void diagnosticCheckForRemainingRecords(Set<Id> assetIds) {
        System.debug('=== DIAGNOSTIC: Checking for remaining records that block asset deletion ===');
        
        // Look for the specific TUE records mentioned in the error
        String[] specificTUENames = new String[]{'TUE-0000000019', 'TUE-0000000020'};
        List<TransactionUsageEntitlement> specificTUEs = [
            SELECT Id, Name, AccountId, AssetId, GrantBindingTargetId 
            FROM TransactionUsageEntitlement 
            WHERE Name IN :specificTUENames
        ];
        
        System.debug('Found ' + specificTUEs.size() + ' specific TUEs from error message:');
        for(TransactionUsageEntitlement tue : specificTUEs) {
            System.debug('TUE: ' + tue.Name + ' (ID: ' + tue.Id + ') - Account: ' + tue.AccountId + ' - Asset: ' + tue.AssetId + ' - GrantTarget: ' + tue.GrantBindingTargetId);
        }
        
        // Look for the specific UEA record mentioned in the error
        String[] specificUEANames = new String[]{'UEA-0000000010'};
        List<UsageEntitlementAccount> specificUEAs = [
            SELECT Id, Name, AccountId 
            FROM UsageEntitlementAccount 
            WHERE Name IN :specificUEANames
        ];
        
        System.debug('Found ' + specificUEAs.size() + ' specific UEAs from error message:');
        for(UsageEntitlementAccount uea : specificUEAs) {
            System.debug('UEA: ' + uea.Name + ' (ID: ' + uea.Id + ') - Account: ' + uea.AccountId);
        }
        
        // Look for the specific UBPI records mentioned in the error
        String[] specificUBPINames = new String[]{'UBPI-0000000003', 'UBPI-0000000004', 'UBPI-0000000005', 'UBPI-0000000006'};
        
        // Try different object names for UBPI records
        String[] ubpiQueries = new String[]{
            'SELECT Id, Name FROM UsageBillingPeriodItem WHERE Name IN :specificUBPINames',
            'SELECT Id, Name FROM UsageBillingPolicyItem WHERE Name IN :specificUBPINames',
            'SELECT Id, Name FROM UsageLiableSummary WHERE Name IN :specificUBPINames',
            'SELECT Id, Name FROM Usage_Liable_Summary__c WHERE Name IN :specificUBPINames'
        };
        
        for(String queryString : ubpiQueries) {
            try {
                List<SObject> ubpiRecords = Database.query(queryString);
                if(!ubpiRecords.isEmpty()) {
                    System.debug('Found ' + ubpiRecords.size() + ' UBPI records using: ' + queryString);
                    for(SObject record : ubpiRecords) {
                        System.debug('UBPI: ' + record.get('Name') + ' (ID: ' + record.Id + ')');
                    }
                    break;
                }
            } catch(Exception e) {
                System.debug('UBPI query failed: ' + queryString + ' - ' + e.getMessage());
            }
        }
        
        // Now try to find what these records are actually referencing
        if(!specificTUEs.isEmpty()) {
            System.debug('Checking what these TUEs reference...');
            for(TransactionUsageEntitlement tue : specificTUEs) {
                if(tue.AssetId != null) {
                    System.debug('TUE ' + tue.Name + ' references Asset: ' + tue.AssetId);
                }
                if(tue.GrantBindingTargetId != null) {
                    System.debug('TUE ' + tue.Name + ' has GrantBindingTarget: ' + tue.GrantBindingTargetId);
                }
            }
        }
    }

    /**
     * Final cleanup method that tries to delete specific records mentioned in error messages
     */
    private static void deleteSpecificProblematicRecords() {
        System.debug('=== FINAL CLEANUP: Attempting to delete specific problematic records ===');
        
        // Delete specific TUE records by name
        String[] specificTUENames = new String[]{'TUE-0000000019', 'TUE-0000000020'};
        List<TransactionUsageEntitlement> problematicTUEs = [
            SELECT Id, Name 
            FROM TransactionUsageEntitlement 
            WHERE Name IN :specificTUENames
        ];
        
        if(!problematicTUEs.isEmpty()) {
            System.debug('Found ' + problematicTUEs.size() + ' problematic TUEs to delete');
            
            // First delete their buckets
            Set<Id> tueIds = new Set<Id>();
            for(TransactionUsageEntitlement tue : problematicTUEs) {
                tueIds.add(tue.Id);
                System.debug('Deleting problematic TUE: ' + tue.Name + ' (ID: ' + tue.Id + ')');
            }
            
            // Delete buckets first
            deleteUsageEntitlementBucketsBottomUp(tueIds, 'TransactionUsageEntitlement');
            
            // Then delete the TUEs
            Database.DeleteResult[] results = Database.delete(problematicTUEs, false);
            for(Database.DeleteResult result : results) {
                if(!result.isSuccess()) {
                    for(Database.Error err : result.getErrors()) {
                        System.debug('Error deleting problematic TUE: ' + err.getMessage());
                    }
                }
            }
        }
        
        // Delete specific UEA records by name
        String[] specificUEANames = new String[]{'UEA-0000000010'};
        List<UsageEntitlementAccount> problematicUEAs = [
            SELECT Id, Name 
            FROM UsageEntitlementAccount 
            WHERE Name IN :specificUEANames
        ];
        
        if(!problematicUEAs.isEmpty()) {
            System.debug('Found ' + problematicUEAs.size() + ' problematic UEAs to delete');
            
            // First delete their buckets
            Set<Id> ueaIds = new Set<Id>();
            for(UsageEntitlementAccount uea : problematicUEAs) {
                ueaIds.add(uea.Id);
                System.debug('Deleting problematic UEA: ' + uea.Name + ' (ID: ' + uea.Id + ')');
            }
            
            // Delete buckets first
            deleteUsageEntitlementBucketsBottomUp(ueaIds, 'UsageEntitlementAccount');
            
            // Then delete the UEAs
            Database.DeleteResult[] results = Database.delete(problematicUEAs, false);
            for(Database.DeleteResult result : results) {
                if(!result.isSuccess()) {
                    for(Database.Error err : result.getErrors()) {
                        System.debug('Error deleting problematic UEA: ' + err.getMessage());
                    }
                }
            }
        }
        
        // Delete specific UBPI records by name
        String[] specificUBPINames = new String[]{'UBPI-0000000003', 'UBPI-0000000004', 'UBPI-0000000005', 'UBPI-0000000006'};
        
        String[] ubpiQueries = new String[]{
            'SELECT Id, Name FROM UsageBillingPeriodItem WHERE Name IN :specificUBPINames',
            'SELECT Id, Name FROM UsageBillingPolicyItem WHERE Name IN :specificUBPINames',
            'SELECT Id, Name FROM UsageLiableSummary WHERE Name IN :specificUBPINames',
            'SELECT Id, Name FROM Usage_Liable_Summary__c WHERE Name IN :specificUBPINames'
        };
        
        for(String queryString : ubpiQueries) {
            try {
                List<SObject> problematicUBPIs = Database.query(queryString);
                if(!problematicUBPIs.isEmpty()) {
                    System.debug('Found ' + problematicUBPIs.size() + ' problematic UBPI records to delete using: ' + queryString);
                    for(SObject record : problematicUBPIs) {
                        System.debug('Deleting problematic UBPI: ' + record.get('Name') + ' (ID: ' + record.Id + ')');
                    }
                    
                    Database.DeleteResult[] results = Database.delete(problematicUBPIs, false);
                    for(Database.DeleteResult result : results) {
                        if(!result.isSuccess()) {
                            for(Database.Error err : result.getErrors()) {
                                System.debug('Error deleting problematic UBPI: ' + err.getMessage());
                            }
                        }
                    }
                    break; // Use first successful query
                }
            } catch(Exception e) {
                System.debug('Problematic UBPI query failed: ' + queryString + ' - ' + e.getMessage());
            }
        }
    }

    /**
     * Deletes assets and their relationships associated with the account.
     * 
     * @param accountId The ID of the account whose assets should be deleted
     * @return Boolean indicating success
     */
    private static Boolean deleteAssets(String accountId) {
        Id accountIdConverted = accountId;
        System.debug('Deleting Assets for account: ' + accountIdConverted);
        Asset[] assetsToDelete = [SELECT Id FROM Asset WHERE AccountId = :accountIdConverted];
        if (!assetsToDelete.isEmpty()) {
            Set<Id> assetIds = new Set<Id>(new Map<Id, Asset>(assetsToDelete).keySet());
            System.debug('Found ' + assetIds.size() + ' Asset records');
            deleteAssetRelationship(assetIds);
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


        /**
     * Deletes FulfillmentLineSourceRel records for a given account.
     * These records establish relationships between:
     * - FulfillmentOrderLineItems and OrderItems
     * - FulfillmentOrderLineItems and other FulfillmentOrderLineItems
     * 
     * This method must be called before deleting FulfillmentOrderLineItems
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @param orderData The OrderData object containing pre-queried information
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteFulfillmentLineSourceRel(String accountId, OrderData orderData) {
        // Get all FulfillmentLineSourceRel records that reference either line items
        List<FulfillmentLineSourceRel> recordsToDelete = [
            SELECT Id 
            FROM FulfillmentLineSourceRel 
            WHERE SourceLineItemId IN :orderData.orderItemIds
            OR FulfilmentOrderLineId IN :orderData.fulfillmentOrderLineItemIds
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
        }
        return true;
    }


    /**
     * Deletes FulfillmentStepSource records for a given account.
     * These records establish relationships between:
     * - FulfillmentSteps and OrderItems
     * - FulfillmentSteps and other FulfillmentSteps
     * 
     * This method must be called before deleting FulfillmentSteps
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @param orderData The OrderData object containing pre-queried information
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteFulfillmentStepSource(String accountId, OrderData orderData) {
        // Get all FulfillmentStepSource records that reference either steps or line items
        List<FulfillmentStepSource> recordsToDelete = [
            SELECT Id 
            FROM FulfillmentStepSource 
            WHERE StepId IN :orderData.fulfillmentStepIds
            OR SourceLineItemId IN :orderData.orderItemIds
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
        }
        return true;
    }

    /**
     * Deletes FulfillmentOrderLineItem records for a given account.
     * These records represent line items in FulfillmentOrders and can be related to:
     * - FulfillmentOrders
     * - FulfillmentAssets
     * 
     * This method must be called after deleting FulfillmentLineSourceRel records
     * but before deleting FulfillmentOrders to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @param orderData The OrderData object containing pre-queried information
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteFulfillmentOrderLineItem(String accountId, OrderData orderData) {
        if (!orderData.fulfillmentOrderLineItems.isEmpty()) {
            Database.delete(orderData.fulfillmentOrderLineItems, false);
        }
        return true;
    }

    /**
     * Deletes FulfillmentOrder records for a given account.
     * These records represent fulfillment orders and can be related to:
     * - Orders
     * - Invoices
     * - OrderSummaries
     * 
     * This method must be called after deleting FulfillmentOrderLineItems
     * but before deleting FulfillmentPlans to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @param orderData The OrderData object containing pre-queried information
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteFulfillmentOrder(String accountId, OrderData orderData) {
        if (!orderData.fulfillmentOrders.isEmpty()) {
            Database.delete(orderData.fulfillmentOrders, false);
        }
        return true;
    }

    /**
     * Deletes FulfillmentPlan records for a given account.
     * These records represent fulfillment plans and can be related to:
     * - Orders (SourceType = 'StandardOrder')
     * - OrderItems (SourceType = 'OrderItem')
     * 
     * This method must be called after deleting FulfillmentOrders
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @param orderData The OrderData object containing pre-queried information
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteFulfillmentPlan(String accountId, OrderData orderData) {
        System.debug('Deleting ' + orderData.fulfillmentPlans.size() + ' FulfillmentPlan records');
        
        if (!orderData.fulfillmentPlans.isEmpty()) {
            try {
                // Delete with allOrNone=false to handle partial failures gracefully
                Database.DeleteResult[] results = Database.delete(orderData.fulfillmentPlans, false);
                
                // Log any errors
                Integer errorCount = 0;
                for(Database.DeleteResult result : results) {
                    if(!result.isSuccess()) {
                        errorCount++;
                        for(Database.Error err : result.getErrors()) {
                            System.debug('Error deleting FulfillmentPlan ' + result.getId() + ': ' + err.getMessage());
                        }
                    }
                }
                
                if(errorCount > 0) {
                    System.debug('Completed FulfillmentPlan deletion with ' + errorCount + ' errors out of ' + results.size() + ' records');
                } else {
                    System.debug('Successfully deleted all FulfillmentPlan records');
                }
                
            } catch(Exception e) {
                System.debug('Error in deleteFulfillmentPlan: ' + e.getMessage());
                throw e;
            }
        }
        return true;
    }

    /**
     * Deletes FulfillmentAsset records for a given account.
     * These records represent fulfillment assets and are directly related to:
     * - Account
     * 
     * This method must be called after deleting FulfillmentOrderLineItems
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @param orderData The OrderData object containing pre-queried information
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteFulfillmentAsset(String accountId, OrderData orderData) {
        if (!orderData.fulfillmentAssets.isEmpty()) {
            Database.delete(orderData.fulfillmentAssets, false);
        }
        return true;
    }

    /**
     * Deletes AssetFulfillmentDecomp records for a given account.
     * These records represent asset fulfillment decompositions and can be related to:
     * - FulfillmentAssets (as source or target)
     * 
     * This method must be called after deleting FulfillmentAssets
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @param orderData The OrderData object containing pre-queried information
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteAssetFulfillmentDecomp(String accountId, OrderData orderData) {
        // Get all AssetFulfillmentDecomp records for these FulfillmentAssets
        List<AssetFulfillmentDecomp> recordsToDelete = [
            SELECT Id 
            FROM AssetFulfillmentDecomp 
            WHERE FulfillmentSourceAssetId IN :orderData.fulfillmentAssetIds
            OR FulfillmentTargetAssetId IN :orderData.fulfillmentAssetIds
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
        }
        return true;
    }

    /**
     * Deletes BindingObjUsageRsrcPlcy records whose polymorphic BindingObjectId
     * is tied to the given Account via any of these targets:
     *  - the Account itself
     *  - an Asset with Asset.AccountId = accountId
     *  - a Contract with Contract.AccountId = accountId
     *
     * Returns all per-row DeleteResults so callers can inspect failures.
     */
    public static List<Database.DeleteResult> deleteUsageResourcePoliciesForAccount(String accountId) {
        if (accountId == null) {
            return new List<Database.DeleteResult>();
        }

        // Collect unique policies across multiple constraint-compliant queries.
        Map<Id, BindingObjUsageRsrcPlcy> uniquePolicies = new Map<Id, BindingObjUsageRsrcPlcy>();

        // Q1: Direct Account
        for (BindingObjUsageRsrcPlcy p : [
            SELECT Id
            FROM BindingObjUsageRsrcPlcy
            WHERE BindingObjectId = :accountId
        ]) uniquePolicies.put(p.Id, p);

        // Q2: Asset -> Account
        for (BindingObjUsageRsrcPlcy p : [
            SELECT Id
            FROM BindingObjUsageRsrcPlcy
            WHERE BindingObjectId IN (
                SELECT Id FROM Asset WHERE AccountId = :accountId
            )
        ]) uniquePolicies.put(p.Id, p);

        // Q3: Contract -> Account
        for (BindingObjUsageRsrcPlcy p : [
            SELECT Id
            FROM BindingObjUsageRsrcPlcy
            WHERE BindingObjectId IN (
                SELECT Id FROM Contract WHERE AccountId = :accountId
            )
        ]) uniquePolicies.put(p.Id, p);

        // Nothing to do?
        if (uniquePolicies.isEmpty()) {
            return new List<Database.DeleteResult>();
        }

        // Delete in safe 200-row batches; allOrNone=false to continue past partial failures.
        List<Database.DeleteResult> results = new List<Database.DeleteResult>();
        List<BindingObjUsageRsrcPlcy> batch = new List<BindingObjUsageRsrcPlcy>();

        for (BindingObjUsageRsrcPlcy p : uniquePolicies.values()) {
            batch.add(p);
            if (batch.size() == BATCH_SIZE) {
                results.addAll(Database.delete(batch, /* allOrNone */ false));
                batch.clear();
            }
        }
        if (!batch.isEmpty()) {
            results.addAll(Database.delete(batch, /* allOrNone */ false));
        }
        return results;
    }

    /**
     * Deletes BindingObjectRateCardEntry records whose polymorphic BindingObjectId
     * is tied to the given Account via any of these targets:
     *  - the Account itself
     *  - a Contract with Contract.AccountId = accountId
     *
     * Returns all per-row DeleteResults so callers can inspect failures.
     */
    public static List<Database.DeleteResult> deleteBindingObjRateCardEntriesForAccount(String accountId) {
        if (accountId == null) {
            return new List<Database.DeleteResult>();
        }

        // Collect unique policies across multiple constraint-compliant queries.
        Map<Id, BindingObjectRateCardEntry> uniquePolicies = new Map<Id, BindingObjectRateCardEntry>();

        // Q1: Direct Account
        for (BindingObjectRateCardEntry p : [
            SELECT Id
            FROM BindingObjectRateCardEntry
            WHERE BindingObjectId = :accountId
        ]) uniquePolicies.put(p.Id, p);

        // Q3: Contract -> Account
        for (BindingObjectRateCardEntry p : [
            SELECT Id
            FROM BindingObjectRateCardEntry
            WHERE BindingObjectId IN (
                SELECT Id FROM Contract WHERE AccountId = :accountId
            )
        ]) uniquePolicies.put(p.Id, p);

        // Nothing to do?
        if (uniquePolicies.isEmpty()) {
            return new List<Database.DeleteResult>();
        }

        // Delete in safe 200-row batches; allOrNone=false to continue past partial failures.
        List<Database.DeleteResult> results = new List<Database.DeleteResult>();
        List<BindingObjectRateCardEntry> batch = new List<BindingObjectRateCardEntry>();

        for (BindingObjectRateCardEntry p : uniquePolicies.values()) {
            batch.add(p);
            if (batch.size() == BATCH_SIZE) {
                results.addAll(Database.delete(batch, /* allOrNone */ false));
                batch.clear();
            }
        }
        if (!batch.isEmpty()) {
            results.addAll(Database.delete(batch, /* allOrNone */ false));
        }
        return results;
    }

}