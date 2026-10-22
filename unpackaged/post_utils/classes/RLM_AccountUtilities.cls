/**
 * RLM_AccountUtilities
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
 * ⚠ Sharing: `without sharing`, declared deliberately rather than left implicit.
 * The invocable's job is to clear an account's ENTIRE related graph so a demo
 * account can be rebuilt, and that graph routinely contains records owned by
 * other users — the integration user, an admin, another persona. Under
 * `with sharing` a non-admin assignee would delete only the records they can
 * see and silently leave the rest, producing a half-reset account that looks
 * successful: worse than refusing. The repo's Apex rules permit `without
 * sharing` for exactly this case provided the reason is documented, which is
 * what this note is. Access is instead controlled at the grant: the class is
 * reachable only through RLM_UtilitiesPermset, which is assigned deliberately
 * and kept separate from the component permission sets for this reason.
 *
 * Previously this class declared NO sharing keyword, so it inherited whichever
 * context called it. An omitted keyword is NOT equivalent to `without sharing` in
 * general — from a `with sharing` caller it would have run WITH sharing. It is
 * equivalent for this class's actual callers, which is why pinning it changes
 * nothing today: every production entry is the Flow invocable, and the only Apex
 * caller is RLM_AccountUtilitiesTest, itself `without sharing`. Adding a caller
 * that runs with sharing would previously have silently changed the reset's
 * behaviour; now it cannot.
 *
 * @author John Rozsits, Brian Galdino, Anthropic Claude 4 Sonnet
 * @date 2025-06-10
 */
public without sharing class RLM_AccountUtilities {
    // Constants
    private static final Integer BATCH_SIZE = 200;

    // Usage summary teardown. The graph has circular delete constraints
    // (a ratable summary can be held by a usage summary and vice versa), so the
    // teardown alternates objects and converges. Six rounds has been ample on an
    // org with 831 summaries; the cap only exists so a pathological graph cannot
    // spin.
    //
    // TEARDOWN_BATCH is a per-QUERY ceiling only -- it does NOT bound the
    // transaction. The 10,000-row DML limit is per transaction and this loop
    // issues nine deletes per round, so the real guard is the remaining-budget
    // clamp inside deleteQuietly(), which degrades to a reported partial
    // teardown instead of a LimitException.
    private static final Integer MAX_TEARDOWN_ROUNDS = 6;
    private static final Integer TEARDOWN_BATCH = 2000;
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

        // Optional (required=false) so callers that don't pass it keep working;
        // a null value is treated as false.
        @InvocableVariable(required=false)
        public Boolean PreserveContractsWithContractedPrices;
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
        if (request.size() > 1) {
            throw new IllegalArgumentException('RLM_AccountUtilities.delAccountRelatedObjects: only one request at a time is supported.');
        }

        String accountId = request.get(0).accountId;
        Boolean deleteAssets = request.get(0).DeleteAssets;
        Boolean deleteFulfillment = request.get(0).DeleteFulfillment;
        Boolean deleteBilling = request.get(0).DeleteBilling;
        // '== true' collapses both null (flag omitted) and false to false, so the
        // default/unchecked behavior is identical to the legacy delete-all path.
        Boolean preserveContractsWithPrices = request.get(0).PreserveContractsWithContractedPrices == true;

            // Start a savepoint for transaction control
        // ------------------------------------------------------------------
        // The usage-graph teardown runs BEFORE the savepoint, deliberately.
        //
        // It is idempotent and convergent -- a rerun simply finds fewer rows --
        // and its partial progress MUST survive a later failure. Inside the
        // savepoint, a single exception anywhere in the order/asset/quote
        // cleanup below would roll back every usage row removed here, so the
        // reset could never converge across reruns: each attempt would start
        // from the same untouched graph and surface the same blocker. That is
        // exactly what made the original failure so hard to diagnose, and it
        // would defeat the DML-budget clamp in deleteQuietly(), whose whole
        // point is that a partial teardown is real progress to build on.
        //
        // Nothing here is coupled to the transactional deletes below, so there
        // is no atomicity to preserve -- only progress to lose.
        deleteUsageResourcePoliciesForAccount(accountId); // BindingObjUsageRsrcPlcy
        deleteBindingObjRateCardEntriesForAccount(accountId); // BindingObjectRateCardEntry

        // The summary graph must go FIRST. A UsageEntitlementEntry holds its
        // UsageSummary, and a bucket cannot be deleted while entitlement entries
        // still reference it -- so tearing down buckets before the summaries
        // (the previous order) fails on any account whose usage was ever rated.
        deleteUsageSummaryGraph(accountId);
        // The clamp in deleteQuietly() stops at the DML-row ceiling instead of
        // throwing, precisely so a partial teardown survives as progress. Falling
        // through to the transactional cleanup below would spend what little budget
        // remains and hit an UNCATCHABLE LimitException -- which rolls back the whole
        // transaction, including everything removed above, defeating the clamp. Stop
        // here instead; the next run starts from a smaller graph and converges.
        if (dmlBudgetExhausted) {
            System.debug(LoggingLevel.WARN, 'delAccountRelatedObjects: STOPPED after the '
                + 'usage teardown -- the transaction\'s DML row budget was exhausted. The '
                + 'usage records removed so far are kept. Transactional cleanup (orders, '
                + 'assets, quotes, invoices) has NOT run. Re-run the reset until it '
                + 'completes without this warning.');
            return;
        }
        // Gated on deleteAssets, like the asset deletion itself further down.
        // AssetRateCardEntry rows are generated when the asset is created and are
        // NOT recreated for an existing asset, so removing them while KEEPING the
        // asset leaves a usage asset that can never rate again.
        if (deleteAssets) {
            deleteAssetRateCardEntries(accountId);
        }

        Savepoint sp = Database.setSavepoint();
        try {
            // Get Order data once
            OrderData orderData = new OrderData(accountId);

            // Then the entitlements and their buckets.
            deleteTransactionUsageEntitlement(accountId);
            deleteUsageEntitlementAccount(accountId); // UsageEntitlementAccount & UsageEntitlementBucket
            deleteAllTransactionUsageEntitlements(accountId); // More comprehensive TUE deletion

            // Then handle other usage and billing related records
            // Final sweep. The convergent teardown above already drains journals as
            // their summaries release them; anything still here refused to delete
            // and will block asset deletion, so say so rather than failing later.
            deleteTransactionJournal(accountId);

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
            deleteContracts(accountId, preserveContractsWithPrices);
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

                // Second pass over the binding policies. They are cleared at the top
                // of this method, but the entitlement teardown in between leaves more
                // behind, and an asset cannot be deleted while any remain:
                //   "could not be completed because it is associated with the
                //    following binding object usage resource policies.: BOURP-..."
                // Clearing them once up front is not enough.
                //
                // Both helpers RETURN their DeleteResults and every existing caller
                // discarded them, so a policy that refuses to delete was invisible --
                // the failure only surfaced later as an unexplained asset DELETE_FAILED.
                reportFailures('BindingObjUsageRsrcPlcy',
                    deleteUsageResourcePoliciesForAccount(accountId));
                reportFailures('BindingObjectRateCardEntry',
                    deleteBindingObjRateCardEntriesForAccount(accountId));

                deleteAssets(accountId);
            }
            
            // Finally handle remaining objects
            // Query quotes once and share across cleanup steps to avoid duplicate SOQL.
            Id acctIdConverted = accountId;
            List<Quote> accountQuotes = [SELECT Id FROM Quote WHERE QuoteAccountId = :acctIdConverted];
            // Delete quote-linked ContentDocuments before quotes are removed
            deleteQuoteDocuments(accountQuotes);
            deleteQuotes(accountQuotes);
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
     * Deletes the provided quotes.
     *
     * @param quotesToDelete Pre-fetched list of Quote records to delete
     * @return Boolean indicating success
     */
    private static Boolean deleteQuotes(List<Quote> quotesToDelete) {
        if (!quotesToDelete.isEmpty()) {
            Database.delete(quotesToDelete);
        }
        return true;
    }

    /**
     * Deletes ContentDocuments and DocumentGenerationProcess records linked to an
     * account's Quotes, where those documents are not also linked to other records
     * outside the account's quotes. Includes DocGen outputs and any manually-attached
     * quote files. Must be called BEFORE deleteQuotes because the platform
     * auto-cascades ContentDocumentLink rows when the linked Quote is deleted,
     * making it impossible to discover quote-attached ContentDocuments afterwards.
     *
     * @param quotes Pre-fetched list of Quote records for the account
     */
    private static void deleteQuoteDocuments(List<Quote> quotes) {
        // 1. Collect all quote IDs
        List<Id> quoteIdList = new List<Id>();
        for (Quote q : quotes) {
            quoteIdList.add(q.Id);
        }
        if (quoteIdList.isEmpty()) return;

        // 2. Delete DocumentGenerationProcess records referencing these quotes.
        //    No platform cascade — these orphan silently after Quote deletion without this step.
        List<DocumentGenerationProcess> dgpToDelete = [
            SELECT Id FROM DocumentGenerationProcess WHERE ReferenceObject IN :quoteIdList
        ];
        for (Integer i = 0; i < dgpToDelete.size(); i += BATCH_SIZE) {
            List<DocumentGenerationProcess> dgpBatch = new List<DocumentGenerationProcess>();
            for (Integer j = i; j < Math.min(i + BATCH_SIZE, dgpToDelete.size()); j++) {
                dgpBatch.add(dgpToDelete[j]);
            }
            Database.delete(dgpBatch, false);
        }

        // 3. Collect ContentDocument IDs from CDLs before quotes are deleted.
        //    Chunked by quoteIdList to keep per-query row counts bounded.
        Set<Id> contentDocIds = new Set<Id>();
        for (Integer i = 0; i < quoteIdList.size(); i += BATCH_SIZE) {
            List<Id> chunk = new List<Id>();
            for (Integer j = i; j < Math.min(i + BATCH_SIZE, quoteIdList.size()); j++) {
                chunk.add(quoteIdList[j]);
            }
            for (ContentDocumentLink cdl : [
                SELECT ContentDocumentId FROM ContentDocumentLink WHERE LinkedEntityId IN :chunk
            ]) {
                contentDocIds.add(cdl.ContentDocumentId);
            }
        }
        if (contentDocIds.isEmpty()) return;

        // 4. Exclude ContentDocuments also linked to records outside these quotes
        //    to avoid deleting files shared with Opportunities, Orders, etc.
        //    ShareType='I' (auto-created personal-library links) are excluded in SOQL so
        //    they are not counted as "linked elsewhere" — every document has one, which
        //    would otherwise cause all documents to be skipped.
        List<Id> contentDocIdList = new List<Id>(contentDocIds);
        Set<Id> quoteIdSet = new Set<Id>(quoteIdList);
        Set<Id> linkedElsewhere = new Set<Id>();
        for (Integer i = 0; i < contentDocIdList.size(); i += BATCH_SIZE) {
            List<Id> chunk = new List<Id>();
            for (Integer j = i; j < Math.min(i + BATCH_SIZE, contentDocIdList.size()); j++) {
                chunk.add(contentDocIdList[j]);
            }
            for (ContentDocumentLink cdl : [
                SELECT ContentDocumentId, LinkedEntityId, ShareType FROM ContentDocumentLink
                WHERE ContentDocumentId IN :chunk
            ]) {
                // Skip: linked to one of our quotes (expected), or a personal-library
                // link (ShareType='I') auto-created by the platform for the file owner.
                // NOTE: ShareType cannot be filtered in SOQL here because Salesforce only
                // allows non-Id field filters on ContentDocumentLink when filtering by
                // LinkedEntityId with the equals operator — not with ContentDocumentId IN.
                if (quoteIdSet.contains(cdl.LinkedEntityId) || cdl.ShareType == 'I') continue;
                linkedElsewhere.add(cdl.ContentDocumentId);
            }
        }
        contentDocIds.removeAll(linkedElsewhere);
        if (contentDocIds.isEmpty()) return;

        // 5. Batch-delete ContentDocuments; platform auto-cascades their CDL rows.
        List<ContentDocument> cdsToDelete = [SELECT Id FROM ContentDocument WHERE Id IN :contentDocIds];
        for (Integer i = 0; i < cdsToDelete.size(); i += BATCH_SIZE) {
            List<ContentDocument> cdsBatch = new List<ContentDocument>();
            for (Integer j = i; j < Math.min(i + BATCH_SIZE, cdsToDelete.size()); j++) {
                cdsBatch.add(cdsToDelete[j]);
            }
            Database.delete(cdsBatch, false);
        }
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
            'SELECT Id, Name FROM TransactionUsageEntitlement WHERE (AssetId IN :assetIds) OR (GrantBindingTargetId IN :assetIds) OR (Asset__c IN :assetIds) OR (RelatedAssetId IN :assetIds)'
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
     * Tears down the usage summary graph for an account.
     *
     * Replaces the previous deleteUsageSummaries / deleteUsageLiableSummaries /
     * deleteUsageRatableSummaries trio, which had three defects:
     *
     *  1. UsageEntitlementEntry was never deleted at all. A fully rated
     *     UsageSummary is held by its entitlement entries ("associated with the
     *     following usage entitlement entries"), so any account whose usage
     *     reached LiableSummaryComplete could not be reset.
     *  2. Each method tried up to nine speculative queries and `break`-ed on the
     *     first non-empty one, so a summary linked by AssetId was left behind
     *     whenever the AccountId query happened to match first. Several of those
     *     object names (UsageLiableSummary, Usage_Ratable_Summary__c,
     *     UsageBillingPolicyItem) do not exist in this release.
     *  3. The fixed delete order cannot work in general: a UsageRatableSummary
     *     cannot be deleted while an associated UsageSummary exists, and some
     *     UsageSummary rows are in turn held by ratable rows.
     *
     * So this alternates the objects and stops when a full round makes no
     * progress, rather than hard-coding an order a future release can invert.
     * SOQL cost is fixed per round instead of growing with the org's history.
     *
     * @param accountId The account whose usage summary graph should be removed
     * @return Boolean indicating the graph was fully drained
     */

    /**
     * Logs per-row delete failures that callers previously discarded. A silently
     * failed cleanup shows up much later as an unrelated DELETE_FAILED on the
     * parent record, which is considerably harder to diagnose.
     */
    private static void reportFailures(String label, List<Database.DeleteResult> results) {
        if (results == null) { return; }
        Integer failed = 0;
        for (Database.DeleteResult r : results) {
            if (!r.isSuccess()) {
                failed++;
                for (Database.Error e : r.getErrors()) {
                    System.debug(label + ' delete failed (' + r.getId() + '): ' + e.getMessage());
                }
            }
        }
        if (failed > 0) {
            System.debug(label + ': ' + failed + ' of ' + results.size()
                + ' could not be deleted -- these will block the parent record.');
        }
    }

    private static Boolean deleteUsageSummaryGraph(String accountId) {
        Set<Id> assetIds = new Set<Id>();
        for (Asset a : [SELECT Id FROM Asset WHERE AccountId = :accountId]) {
            assetIds.add(a.Id);
        }

        // ONE convergent loop over the WHOLE usage graph. The delete constraints
        // are circular, so no fixed order can work:
        //   UsageSummary <-> UsageRatableSummary   (each can hold the other)
        //   UsageEntitlementEntry -> UsageSummary  (an entry holds its summary)
        //   TransactionJournal    -> UsageSummary  (a rated journal is held)
        //   UsageEntitlementBucket parent <-> child (3 levels)
        //   TransactionUsageEntitlement <- bucket
        //   UsageEntitlementAccount     <- TUE
        //   UsageCmtAssetRelatedObj     -> Asset   (the commitment junction)
        // Alternate them and stop when a full round makes no progress. Fixed, small
        // SOQL cost per round rather than one that grows with the org's history.
        Integer removed = 0;
        for (Integer round = 1; round <= MAX_TEARDOWN_ROUNDS; round++) {
            Integer progress = 0;

            progress += deleteQuietly([
                SELECT Id FROM UsageEntitlementEntry
                WHERE TransactionUsageEntitlement.Account.Id = :accountId LIMIT :TEARDOWN_BATCH]);
            progress += deleteQuietly([
                SELECT Id FROM UsageBillingPeriodItem
                WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :TEARDOWN_BATCH]);
            progress += deleteQuietly([
                SELECT Id FROM UsageSummary
                WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :TEARDOWN_BATCH]);
            progress += deleteQuietly([
                SELECT Id FROM UsageRatableSummary
                WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :TEARDOWN_BATCH]);
            progress += deleteQuietly([
                SELECT Id FROM TransactionJournal
                WHERE AccountId = :accountId LIMIT :TEARDOWN_BATCH]);
            progress += deleteQuietly([
                SELECT Id FROM UsageEntitlementBucket
                WHERE TransactionUsageEntitlement.Account.Id = :accountId LIMIT :TEARDOWN_BATCH]);
            progress += deleteQuietly([
                SELECT Id FROM TransactionUsageEntitlement
                WHERE AccountId = :accountId LIMIT :TEARDOWN_BATCH]);
            progress += deleteQuietly([
                SELECT Id FROM UsageEntitlementAccount
                WHERE AccountId = :accountId LIMIT :TEARDOWN_BATCH]);
            // The commitment junction. Linking a commitment to its anchor is a
            // post-262 selling step this utility predates, and an anchor asset
            // cannot be deleted while its junction row survives.
            if (!assetIds.isEmpty()) {
                progress += deleteQuietly([
                    SELECT Id FROM UsageCmtAssetRelatedObj
                    WHERE AssetId IN :assetIds OR RelatedObjectId IN :assetIds
                    LIMIT :TEARDOWN_BATCH]);
            }

            removed += progress;
            System.debug('deleteUsageSummaryGraph: round ' + round + ' removed ' + progress);
            if (progress == 0 || dmlBudgetExhausted) { break; }
        }
        System.debug('deleteUsageSummaryGraph: removed ' + removed + ' usage record(s)'
            + ' (DML rows used ' + Limits.getDmlRows() + '/' + Limits.getLimitDmlRows() + ')');
        if (dmlBudgetExhausted) {
            // Not an exception: the rows deleted so far are real progress, and
            // throwing here would roll them back and hide it.
            System.debug(LoggingLevel.WARN, 'deleteUsageSummaryGraph: STOPPED EARLY -- the '
                + 'transaction\'s DML row budget was exhausted. Usage records remain for this '
                + 'account; run the reset again until it reports a clean pass.');
        }
        return true;
    }

    /**
     * Deletes AssetRateCardEntry records for an account's assets.
     *
     * These were never removed, and they block deletion of the design-time
     * RateCardEntry rows they reference -- which is why reloading qb-rates
     * against an org with live assets inserts a second, Draft copy of every
     * entry instead of replacing the Active ones.
     *
     * @param accountId The account whose asset rate card entries should be removed
     * @return Boolean indicating success
     */
    private static Boolean deleteAssetRateCardEntries(String accountId) {
        List<AssetRateCardEntry> arces = [
            SELECT Id FROM AssetRateCardEntry WHERE Asset.AccountId = :accountId
        ];
        Integer removed = deleteQuietly(arces);
        System.debug('deleteAssetRateCardEntries: removed ' + removed);
        return true;
    }

    /** Set when a delete had to be trimmed because the transaction's DML row
     *  budget ran out. Callers report it so a partial teardown is never mistaken
     *  for a complete one. */
    private static Boolean dmlBudgetExhausted = false;

    /**
     * Best-effort delete that reports how many rows actually went, so a
     * convergence loop can tell progress from a no-op round. Failures are
     * expected here (a row still held by a parent) and are logged, not thrown.
     *
     * The 10,000-row DML limit is per TRANSACTION, not per statement. The
     * teardown loop issues nine deletes per round over several rounds, so the
     * list is clamped to the REMAINING budget here -- one clamp covers every
     * call site, and running out degrades to a reported partial teardown rather
     * than a LimitException that rolls back all the progress made.
     */
    private static Integer deleteQuietly(List<SObject> records) {
        if (records == null || records.isEmpty()) { return 0; }
        Integer headroom = Limits.getLimitDmlRows() - Limits.getDmlRows();
        if (headroom <= 0) {
            dmlBudgetExhausted = true;
            return 0;
        }
        if (records.size() > headroom) {
            dmlBudgetExhausted = true;
            List<SObject> trimmed = new List<SObject>();
            for (Integer i = 0; i < headroom; i++) { trimmed.add(records[i]); }
            records = trimmed;
        }
        Integer removed = 0;
        for (Database.DeleteResult r : Database.delete(records, false)) {
            if (r.isSuccess()) {
                removed++;
            } else {
                for (Database.Error err : r.getErrors()) {
                    // Not FINE: a row that refuses to delete is the thing that later
                    // blocks the asset, so it must be visible at the default level.
                    System.debug('deleteQuietly blocked: ' + err.getMessage());
                }
            }
        }
        return removed;
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
     * When preserveContractsWithPrices is true, contracts that have at least one
     * ContractItemPrice (contracted price) child are kept. Because
     * ContractItemPrice.ContractId is a master-detail relationship, a surviving
     * Contract retains its contracted prices automatically — no explicit child
     * handling is required.
     *
     * @param accountId The ID of the account whose records should be deleted
     * @param preserveContractsWithPrices When true, skip contracts that have
     *        ContractItemPrice children; when false, delete all contracts
     * @return Boolean indicating success of the operation
     */
    private static Boolean deleteContracts(String accountId, Boolean preserveContractsWithPrices) {
        Id acctId = accountId;

        if (preserveContractsWithPrices) {
            List<Contract> contractsToDelete;

            if (!Schema.getGlobalDescribe().containsKey('ContractItemPrice')) {
                // Contract Pricing is unavailable, so no contract can have a
                // ContractItemPrice child. Every contract is therefore unpriced
                // and remains eligible for deletion under the preserve-mode rule.
                contractsToDelete = [
                    SELECT Id FROM Contract WHERE AccountId = :acctId
                ];
            } else {
                // Select only contracts with NO ContractItemPrice children via a
                // semi-join on the master-detail FK. Dynamic SOQL keeps this class
                // deployable on editions where Contract Pricing is unavailable.
                contractsToDelete = (List<Contract>) Database.query(
                    'SELECT Id FROM Contract WHERE AccountId = :acctId ' +
                    'AND Id NOT IN (SELECT ContractId FROM ContractItemPrice)');
            }

            if (!contractsToDelete.isEmpty()) {
                Database.delete(contractsToDelete);
            }
            return true;
        }

        // Unchanged legacy behavior: delete all contracts on the account.
        Contract[] contractsToDelete =
            [SELECT Id FROM Contract WHERE AccountId = :acctId];
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
        }
        System.debug('Total assets to clean up: ' + assetIds.size());

        Id acctId = accountId;

        // =================================================================
        // Deletion order (confirmed from org diagnostics):
        //   UAG (UsageSummary) blocks → URS, UEB
        //   URS (UsageRatableSummary) blocks → UEB
        //   UBPI (UsageBillingPeriodItem / liable summaries) blocks → UEB
        //   UEB (UsageEntitlementBucket) blocks → TUE, UEA
        //   TUE, UEA, URS, UAG block → Asset
        //
        // So: UAG → URS → UBPI → UEB (leaf→parent) → TUE → UEA → Asset
        // =================================================================

        // --- 1. Delete UsageSummaries (UAG) — blocks URS and UEB ---
        List<UsageSummary> usList = [SELECT Id FROM UsageSummary WHERE AssetId IN :assetIds];
        if(!usList.isEmpty()) {
            System.debug('Deleting ' + usList.size() + ' Usage Summaries');
            Database.delete(usList, false);
        }
        // Also delete by account (catches any not directly on the asset)
        // Note: no Id NOT IN filter needed — records deleted above won't be returned by a fresh query
        List<UsageSummary> usAcctList = [SELECT Id FROM UsageSummary WHERE AccountId = :acctId];
        if(!usAcctList.isEmpty()) {
            System.debug('Deleting ' + usAcctList.size() + ' additional Usage Summaries by account');
            Database.delete(usAcctList, false);
        }

        // --- 2. Delete UsageRatableSummaries (URS) — blocks UEB ---
        List<UsageRatableSummary> ursList = [SELECT Id FROM UsageRatableSummary WHERE AssetId IN :assetIds];
        if(!ursList.isEmpty()) {
            System.debug('Deleting ' + ursList.size() + ' Usage Ratable Summaries');
            Database.delete(ursList, false);
        }

        // --- 3. Delete UsageBillingPeriodItems (UBPI / liable summaries) — blocks UEB ---
        try {
            List<SObject> ubpiList = Database.query('SELECT Id FROM UsageBillingPeriodItem WHERE AssetId IN :assetIds');
            if(!ubpiList.isEmpty()) {
                System.debug('Deleting ' + ubpiList.size() + ' Usage Billing Period Items');
                Database.delete(ubpiList, false);
            }
        } catch(Exception e) { System.debug('UBPI by asset query skipped: ' + e.getMessage()); }
        // Also try by account
        try {
            List<SObject> ubpiAcct = Database.query('SELECT Id FROM UsageBillingPeriodItem WHERE AccountId = :acctId');
            if(!ubpiAcct.isEmpty()) {
                System.debug('Deleting ' + ubpiAcct.size() + ' UBPI by account');
                Database.delete(ubpiAcct, false);
            }
        } catch(Exception e) { System.debug('UBPI by account query skipped: ' + e.getMessage()); }

        // --- 4. Delete UsageEntitlementBuckets (UEB) — blocks TUE and UEA ---
        // Collect all TUE IDs
        Set<Id> allTueIds = new Set<Id>();
        for(SObject r : [SELECT Id FROM TransactionUsageEntitlement WHERE AssetId IN :assetIds]) { allTueIds.add(r.Id); }
        try {
            for(SObject r : Database.query('SELECT Id FROM TransactionUsageEntitlement WHERE GrantBindingTargetId IN :assetIds')) { allTueIds.add(r.Id); }
        } catch(Exception e) { /* field may not exist */ }
        // Also get all TUEs by account
        for(SObject r : [SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :acctId]) { allTueIds.add(r.Id); }

        // Collect all UEA IDs
        Set<Id> allUeaIds = new Set<Id>();
        for(UsageEntitlementAccount uea : [SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :acctId]) {
            allUeaIds.add(uea.Id);
        }

        // Find all buckets: by TUE reference, by UEA parent, or by account
        Set<Id> bucketSearchIds = new Set<Id>();
        bucketSearchIds.addAll(allTueIds);
        bucketSearchIds.addAll(allUeaIds);

        Set<Id> allBucketIds = new Set<Id>();
        if(!bucketSearchIds.isEmpty()) {
            for(UsageEntitlementBucket b : [
                SELECT Id FROM UsageEntitlementBucket
                WHERE TransactionUsageEntitlementId IN :allTueIds
                OR ParentId IN :bucketSearchIds
            ]) {
                allBucketIds.add(b.Id);
            }
            // Recursively find child buckets until no new descendants are discovered
            Set<Id> currentLevelIds = new Set<Id>(allBucketIds);
            while(!currentLevelIds.isEmpty()) {
                Set<Id> nextLevelIds = new Set<Id>();
                for(UsageEntitlementBucket nb : [
                    SELECT Id FROM UsageEntitlementBucket WHERE ParentId IN :currentLevelIds AND Id NOT IN :allBucketIds
                ]) {
                    nextLevelIds.add(nb.Id);
                    allBucketIds.add(nb.Id);
                }
                currentLevelIds = nextLevelIds;
            }
        }

        // Multi-pass bucket deletion (handles nested parent-child hierarchy)
        if(!allBucketIds.isEmpty()) {
            Integer pass = 0;
            Integer prevSize = allBucketIds.size();
            while(!allBucketIds.isEmpty()) {
                pass++;
                List<UsageEntitlementBucket> toDelete = [SELECT Id FROM UsageEntitlementBucket WHERE Id IN :allBucketIds];
                if(toDelete.isEmpty()) break;
                System.debug('Bucket deletion pass ' + pass + ': ' + toDelete.size() + ' buckets');
                Database.DeleteResult[] results = Database.delete(toDelete, false);
                for(Database.DeleteResult dr : results) {
                    if(dr.isSuccess()) {
                        allBucketIds.remove(dr.getId());
                    }
                }
                // Break if no progress was made to avoid infinite loop
                if(allBucketIds.size() == prevSize) {
                    System.debug('ERROR: Bucket deletion stalled — ' + allBucketIds.size() + ' buckets could not be deleted');
                    break;
                }
                prevSize = allBucketIds.size();
            }
        }

        // --- 5. Delete TUEs ---
        if(!allTueIds.isEmpty()) {
            List<TransactionUsageEntitlement> tuesToDel = [SELECT Id FROM TransactionUsageEntitlement WHERE Id IN :allTueIds];
            if(!tuesToDel.isEmpty()) {
                System.debug('Deleting ' + tuesToDel.size() + ' TUEs');
                Database.delete(tuesToDel, false);
            }
        }

        // --- 6. Delete UEAs ---
        if(!allUeaIds.isEmpty()) {
            List<UsageEntitlementAccount> ueasToDel = [SELECT Id FROM UsageEntitlementAccount WHERE Id IN :allUeaIds];
            if(!ueasToDel.isEmpty()) {
                System.debug('Deleting ' + ueasToDel.size() + ' UEAs');
                Database.delete(ueasToDel, false);
            }
        }

        // --- 7. Delete other asset references (ServiceContract, WorkOrder, Case) ---
        deleteOtherAssetReferences(assetIds);

        return true;
    }

    /**
     * Deletes any other records that might reference assets
     */
    private static void deleteOtherAssetReferences(Set<Id> assetIds) {
        System.debug('Deleting other records that might reference assets');

        // Try to find and delete any other objects that might reference assets
        String[] otherPossibleQueries = new String[]{
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
        List<Invoice> invoicesToDelete = new List<Invoice>();
        Integer retained = 0;
        for (Invoice inv : [SELECT Id, Status FROM Invoice WHERE BillingAccountId = :accountId]) {
            if (inv.Status == 'Draft') { invoicesToDelete.add(inv); } else { retained++; }
        }
        if (!invoicesToDelete.isEmpty()) {
            Database.delete(invoicesToDelete);
        }
        // Posted invoices cannot be deleted, so a reset legitimately leaves them behind. Saying
        // nothing, though, makes a partial clear read as a full one -- the account looks reset
        // while records remain. Report it rather than only filtering it out.
        if (retained > 0) {
            System.debug(LoggingLevel.WARN, 'deleteInvoices: RETAINED ' + retained + ' non-Draft '
                + 'invoice(s) -- posted invoices cannot be deleted. Their Billing '
                + 'TransactionJournal rows carry no AccountId, so they are likewise out of reach '
                + 'of an account-scoped reset. This account is NOT fully cleared.');
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
        // BindingObjectId is POLYMORPHIC (Account / Asset / BindingObjectCustomExt /
        // Contract). A semi-join against a polymorphic lookup does not resolve --
        // it silently matches nothing, which is why asset deletion kept failing with
        // "associated with the following binding object usage resource policies"
        // even though this method reported success. Materialise the ids and bind.
        Set<Id> bindAssetIds = new Set<Id>();
        for (Asset a : [SELECT Id FROM Asset WHERE AccountId = :accountId]) {
            bindAssetIds.add(a.Id);
        }
        if (!bindAssetIds.isEmpty()) {
            for (BindingObjUsageRsrcPlcy p : [
                SELECT Id
                FROM BindingObjUsageRsrcPlcy
                WHERE BindingObjectId IN :bindAssetIds
            ]) uniquePolicies.put(p.Id, p);
        }

        // Q3: Contract -> Account (same polymorphic semi-join problem as Q2).
        Set<Id> bindContractIds = new Set<Id>();
        for (Contract c : [SELECT Id FROM Contract WHERE AccountId = :accountId]) {
            bindContractIds.add(c.Id);
        }
        for (BindingObjUsageRsrcPlcy p : [
            SELECT Id
            FROM BindingObjUsageRsrcPlcy
            WHERE BindingObjectId IN :bindContractIds
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