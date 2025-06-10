/**
 * Utility class for managing account-related object deletions.
 * This class provides methods to delete various objects related to an account in the correct order
 * to maintain referential integrity. It handles:
 * 
 * 1. Order Management:
 *    - Orders and OrderItems
 *    - TransactionUsageEntitlements
 *    - UsageEntitlementAccounts
 * 
 * 2. Fulfillment Management:
 *    - FulfillmentOrders and FulfillmentOrderLineItems
 *    - FulfillmentPlans and FulfillmentSteps
 *    - FulfillmentAssets and AssetFulfillmentDecomp
 *    - FulfillmentLineSourceRel and FulfillmentStepSource
 * 
 * 3. Usage and Billing:
 *    - TransactionJournals
 *    - UsageSummaries
 *    - BillingScheduleGroups
 *    - Invoices
 * 
 * 4. Other Related Objects:
 *    - Contracts
 *    - Quotes
 *    - Opportunities
 *    - Assets
 * 
 * The class uses a centralized data structure (OrderData) to avoid redundant queries
 * and ensure efficient deletion of related objects.
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
     * This method orchestrates the deletion of all related objects in the correct order:
     * 
     * 1. Orders and Related Objects:
     *    - Orders (after updating to Draft)
     *    - TransactionUsageEntitlements
     *    - UsageEntitlementAccounts
     * 
     * 2. Usage and Billing:
     *    - TransactionJournals
     *    - UsageSummaries
     *    - BillingScheduleGroups
     * 
     * 3. Contracts and Assets:
     *    - Contracts
     *    - Assets (if DeleteAssets is true)
     * 
     * 4. Fulfillment Objects (if DeleteFulfillment is true):
     *    - FulfillmentLineSourceRel
     *    - FulfillmentStepSource
     *    - FulfillmentOrderLineItem
     *    - FulfillmentOrder
     *    - FulfillmentPlan
     *    - FulfillmentAsset
     *    - AssetFulfillmentDecomp
     * 
     * 5. Sales Objects:
     *    - Quotes
     *    - Opportunities
     * 
     * 6. Billing Objects (if DeleteBilling is true):
     *    - Invoices
     * 
     * The method uses a savepoint to ensure all deletions are rolled back if any error occurs.
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
            deleteOrders(accountId, orderData);
            
            // Then handle usage entitlements
            deleteTransactionUsageEntitlement(accountId);
            deleteUsageEntitlementAccount(accountId);
            
            // Then handle journals and summaries
            deleteTransactionJournal(accountId);
            deleteUsageSummaries(accountId);
            deleteBillingScheduleGroups(accountId);
            
            // Handle contracts
            deleteContracts(accountId);
            
            if (deleteFulfillment) {
                // Delete fulfillment objects in the correct order
                // First delete the source relationships
                deleteFulfillmentLineSourceRel(accountId, orderData);
                deleteFulfillmentStepSource(accountId, orderData);
                
                // Then delete the line items
                deleteFulfillmentOrderLineItem(accountId, orderData);
                
                // Then delete the orders
                deleteFulfillmentOrder(accountId, orderData);
                
                // Finally delete the plans
                deleteFulfillmentPlan(accountId, orderData);
                
                // Delete quotes and opportunities last
                deleteQuotes(accountId);
                deleteOpportunities(accountId);
            }
            
            // Handle assets and billing after fulfillment is cleaned up
            if (deleteAssets) {
                deleteAssets(accountId);
                deleteFulfillmentAsset(accountId, orderData);
                deleteAssetFulfillmentDecomp(accountId, orderData);
            }
            if (deleteBilling) {
                deleteInvoices(accountId);
            }
        } catch (Exception e) {
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
     * Uses a single query to get all related objects.
     */
    private static Boolean deleteOrders(String accountId, OrderData orderData) {
        // First get all Orders for this account
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
     * Deletes Usage Entitlement Buckets (UEB) related to Transaction Usage Entitlements (TUE).
     * Uses a single query to get all related buckets and builds the hierarchy.
     */
    private static Boolean deleteUsageEntitlementBucket(Set<Id> entitlementIds) {
        if (entitlementIds.isEmpty()) {
            return true;
        }

        // Get all related buckets in a single query
        List<UsageEntitlementBucket> allBuckets = [
            SELECT Id, Name, ParentId, Parent.Type, Parent.Name 
            FROM UsageEntitlementBucket 
            WHERE TransactionUsageEntitlementId IN :entitlementIds
            OR ParentId IN :entitlementIds
            OR Id IN :entitlementIds
        ];

        return deleteBucketsInOrder(allBuckets);
    }

    /**
     * Deletes Usage Entitlement Buckets (UEB) related to Usage Entitlement Accounts (UEA).
     * Uses a single query to get all related buckets and builds the hierarchy.
     */
    private static Boolean deleteUsageEntitlementBucketParent(Set<Id> entitlementIds) {
        if (entitlementIds.isEmpty()) {
            return true;
        }

        // Get all related buckets in a single query
        List<UsageEntitlementBucket> allBuckets = [
            SELECT Id, Name, ParentId, Parent.Type, Parent.Name 
            FROM UsageEntitlementBucket 
            WHERE ParentId IN :entitlementIds
            OR Id IN :entitlementIds
        ];

        return deleteBucketsInOrder(allBuckets);
    }

    /**
     * Helper method to delete buckets in the correct order.
     * Handles the common logic for both bucket deletion methods.
     */
    private static Boolean deleteBucketsInOrder(List<UsageEntitlementBucket> allBuckets) {
        if (allBuckets.isEmpty()) {
            return true;
        }

        // Create maps to track relationships
        Map<Id, List<Id>> parentToChildrenMap = new Map<Id, List<Id>>();
        Map<Id, Id> childToParentMap = new Map<Id, Id>();
        Set<Id> allBucketIds = new Set<Id>();

        // Build relationship maps
        for (UsageEntitlementBucket bucket : allBuckets) {
            allBucketIds.add(bucket.Id);
            if (bucket.ParentId != null) {
                childToParentMap.put(bucket.Id, bucket.ParentId);
                if (!parentToChildrenMap.containsKey(bucket.ParentId)) {
                    parentToChildrenMap.put(bucket.ParentId, new List<Id>());
                }
                parentToChildrenMap.get(bucket.ParentId).add(bucket.Id);
            }
        }

        // Find top-level parent buckets
        Set<Id> topLevelParentIds = new Set<Id>();
        for (Id bucketId : allBucketIds) {
            if (!childToParentMap.containsKey(bucketId)) {
                topLevelParentIds.add(bucketId);
            }
        }

        // Process buckets level by level
        Set<Id> processedIds = new Set<Id>();
        Set<Id> currentLevel = new Set<Id>(allBucketIds);
        currentLevel.removeAll(topLevelParentIds);

        while (!currentLevel.isEmpty()) {
            Set<Id> nextLevel = new Set<Id>();
            Set<Id> toDelete = new Set<Id>();

            // Find leaf nodes
            for (Id bucketId : currentLevel) {
                if (!parentToChildrenMap.containsKey(bucketId) || 
                    (parentToChildrenMap.containsKey(bucketId) && 
                     processedIds.containsAll(parentToChildrenMap.get(bucketId)))) {
                    toDelete.add(bucketId);
                } else {
                    nextLevel.add(bucketId);
                }
            }

            // Delete leaf nodes
            if (!toDelete.isEmpty()) {
                Database.delete([SELECT Id FROM UsageEntitlementBucket WHERE Id IN :toDelete], false);
                processedIds.addAll(toDelete);
            }

            currentLevel = nextLevel;
        }

        // Delete top-level parent buckets
        if (!topLevelParentIds.isEmpty()) {
            Database.delete([SELECT Id FROM UsageEntitlementBucket WHERE Id IN :topLevelParentIds], false);
        }

        return true;
    }

    /**
     * Deletes TransactionUsageEntitlement records for a given account.
     * These records represent usage entitlements for transactions and can be related to:
     * - OrderItems
     * - UsageEntitlementAccounts
     * 
     * This method must be called after deleting Orders but before deleting UsageEntitlementAccounts
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteTransactionUsageEntitlement(String accountId) {
        // Get all TransactionUsageEntitlements for this account
        List<TransactionUsageEntitlement> recordsToDelete = [
            SELECT Id 
            FROM TransactionUsageEntitlement 
            WHERE AccountId = :accountId
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
        }
        return true;
    }

    /**
     * Deletes UsageEntitlementAccount records for a given account.
     * These records represent usage entitlements at the account level and can be related to:
     * - Account
     * - UsageEntitlementBuckets
     * 
     * This method must be called after deleting TransactionUsageEntitlements
     * to maintain referential integrity.
     * 
     * @param accountId The ID of the account whose records should be deleted
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteUsageEntitlementAccount(String accountId) {
        // Get all UsageEntitlementAccounts for this account
        List<UsageEntitlementAccount> recordsToDelete = [
            SELECT Id 
            FROM UsageEntitlementAccount 
            WHERE AccountId = :accountId
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
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
            WHERE AccountId = :accountId
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
        // Get all Contracts for this account
        List<Contract> recordsToDelete = [
            SELECT Id 
            FROM Contract 
            WHERE AccountId = :accountId
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
        }
        return true;
    }

    /**
     * Deletes assets and their relationships associated with the account.
     * Uses a single query to get all related objects.
     */
    private static Boolean deleteAssets(String accountId) {
        // Get all Assets for this account
        List<Asset> recordsToDelete = [
            SELECT Id 
            FROM Asset 
            WHERE AccountId = :accountId
        ];
        
        if (!recordsToDelete.isEmpty()) {
            Database.delete(recordsToDelete, false);
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
        // Get all Invoices for this account
        List<Invoice> recordsToDelete = [
            SELECT Id 
            FROM Invoice 
            WHERE BillingAccountId = :accountId
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
        if (!orderData.fulfillmentPlans.isEmpty()) {
            Database.delete(orderData.fulfillmentPlans, false);
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
}