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
 * 
 * @author John Rozsits, Brian Galdino, Anthropic Claude 4 Sonnet
 * @date 2025-06-10
 */
public class RCAccountUtilities {
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
         */
        public OrderData(String accountId) {
            // Get all Orders for this account
            this.orders = [
                SELECT Id 
                FROM Order 
                WHERE AccountId = :accountId
            ];
            
            this.orderIds = new Set<Id>();
            for(Order o : this.orders) {
                this.orderIds.add(o.Id);
            }
            
            // Get all OrderItems for this account
            this.orderItems = [
                SELECT Id 
                FROM OrderItem 
                WHERE Order.AccountId = :accountId
            ];
            
            this.orderItemIds = new Set<Id>();
            this.sourceIdentifiers = new Set<String>();
            for(OrderItem oi : this.orderItems) {
                this.orderItemIds.add(oi.Id);
                this.sourceIdentifiers.add(oi.Id);
            }
            for(Order o : this.orders) {
                this.sourceIdentifiers.add(o.Id);
            }

            // Get all Invoices for this account
            List<Invoice> invoices = [
                SELECT Id 
                FROM Invoice 
                WHERE BillingAccountId = :accountId
            ];
            
            Set<Id> invoiceIds = new Set<Id>();
            for(Invoice inv : invoices) {
                invoiceIds.add(inv.Id);
            }

            // Get all OrderSummaries for this account
            List<OrderSummary> summaries = [
                SELECT Id 
                FROM OrderSummary 
                WHERE AccountId = :accountId
            ];
            
            Set<Id> summaryIds = new Set<Id>();
            for(OrderSummary summary : summaries) {
                summaryIds.add(summary.Id);
            }

            // Get all FulfillmentOrders that reference any of these
            this.fulfillmentOrders = [
                SELECT Id 
                FROM FulfillmentOrder 
                WHERE AccountId = :accountId
                OR OrderId IN :this.orderIds
                OR InvoiceId IN :invoiceIds
                OR OrderSummaryId IN :summaryIds
            ];
            
            this.fulfillmentOrderIds = new Set<Id>();
            for(FulfillmentOrder fo : this.fulfillmentOrders) {
                this.fulfillmentOrderIds.add(fo.Id);
            }

            // Get all FulfillmentPlans for these orders and order items
            this.fulfillmentPlans = [
                SELECT Id 
                FROM FulfillmentPlan 
                WHERE SourceIdentifier IN :this.sourceIdentifiers
                AND (SourceType = 'StandardOrder' OR SourceType = 'OrderItem')
            ];
            
            this.fulfillmentPlanIds = new Set<Id>();
            for(FulfillmentPlan plan : this.fulfillmentPlans) {
                this.fulfillmentPlanIds.add(plan.Id);
            }

            // Get all FulfillmentSteps for these plans
            this.fulfillmentSteps = [
                SELECT Id 
                FROM FulfillmentStep 
                WHERE FulfillmentPlanId IN :this.fulfillmentPlanIds
            ];
            
            this.fulfillmentStepIds = new Set<Id>();
            for(FulfillmentStep step : this.fulfillmentSteps) {
                this.fulfillmentStepIds.add(step.Id);
            }

            // Get all FulfillmentAssets for this account
            this.fulfillmentAssets = [
                SELECT Id 
                FROM FulfillmentAsset 
                WHERE AccountId = :accountId
            ];
            
            this.fulfillmentAssetIds = new Set<Id>();
            for(FulfillmentAsset fa : this.fulfillmentAssets) {
                this.fulfillmentAssetIds.add(fa.Id);
            }

            // Get all FulfillmentOrderLineItems for these FulfillmentOrders
            this.fulfillmentOrderLineItems = [
                SELECT Id 
                FROM FulfillmentOrderLineItem 
                WHERE FulfillmentOrderId IN :this.fulfillmentOrderIds
            ];
            
            this.fulfillmentOrderLineItemIds = new Set<Id>();
            for(FulfillmentOrderLineItem foli : this.fulfillmentOrderLineItems) {
                this.fulfillmentOrderLineItemIds.add(foli.Id);
            }
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
            
            // First handle orders and their related objects
            deleteOrders(accountId);
            deleteTransactionJournal(accountId);
            deleteUsageSummaries(accountId);
            deleteBillingScheduleGroups(accountId);
            
            // Handle contracts
            deleteContracts(accountId);
            deleteAssets(accountId);
            deleteInvoices(accountId);
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
     * Deletes FulfillmentLineSourceRel records for a given account.
     * These records establish relationships between:
     * - FulfillmentOrderLineItems and OrderItems
     * - FulfillmentOrderLineItems and other FulfillmentOrderLineItems
     * 
     * This method must be called before deleting FulfillmentOrderLineItems
     * to maintain referential integrity.
     * 
     * @param orderItems List of order items whose fulfillment relationships should be deleted
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteFulfillmentLineSourceRel(List<OrderItem> orderItems) {
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
        if (entitlementIds.isEmpty()) {
            return true;
        }

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
        if (entitlementIds.isEmpty()) {
            return true;
        }

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