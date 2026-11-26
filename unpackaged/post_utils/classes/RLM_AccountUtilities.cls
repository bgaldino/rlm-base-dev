/**
 * RLM_AccountUtilities
 *
 * Resets a demo account so it can be sold to again. Deletes the orders, assets,
 * contracts, billing records, collection plans, disputes, quotes and
 * opportunities built on the account, along with the usage and fulfillment
 * records that would otherwise block those deletes. Invoked by the
 * RLM_Account_Utilities screen flow (quick action Account.RLM_Reset_Account),
 * which shows the Result returned here.
 *
 * The reset runs in two phases:
 *  1. The usage graph: binding policies, usage summaries, entitlements and their
 *     buckets, rated journals and asset rate card entries. Runs BEFORE the
 *     savepoint, so its progress survives a later failure.
 *  2. Everything else, inside a savepoint: collections, billing, fulfillment,
 *     contracts, orders, assets, quotes and opportunities. If any of it fails,
 *     all of it rolls back and the Result says why.
 *
 * Neither phase may exceed a governor limit: that throws a LimitException, which
 * cannot be caught and rolls back BOTH phases. So every delete is clamped to the
 * DML budget left (deleteRows), and the usage loop starts a round only while the
 * queries phase 2 needs are still available (QUERY_RESERVE). Running short ends
 * the run with a Result that asks for another run, which continues from there.
 *
 * Preflight (todo 397; owner decision: refuse the whole reset). Before phase 1, a
 * read-only check (Preflight) finds, in system mode, every record the run would delete
 * or change for the selected options, and refuses the whole reset, changing nothing, if
 * the running user could not delete all of them. A record blocks when the user has no
 * delete permission on its object, no delete access to the record
 * (UserRecordAccess.HasDeleteAccess), cannot see it (HasReadAccess false), or cannot read
 * its object at all, and when a permission the run needs on it is missing (Edit
 * Activated Orders for an activated order, Access Lifecycle-Managed Assets for a
 * lifecycle-managed asset, Delete Invoice and Invoice Lines for a posted invoice). The
 * Result then says the reset was not run and lists the blockers: visible records by
 * object with their names and the reason, hidden or unreadable ones as counts. Live 264
 * (as the salesrep persona, under System.runAs and in a Login As session) a query in this
 * class saw only the records sharing showed that user, although the class is declared
 * without sharing, and a delete of a record the user could edit but not delete was
 * refused; that is why the check is needed and why it reads in system mode.
 *
 * Because the preflight refused any account holding records of an object the user cannot
 * read, the steps below skip such objects (canRead) without a report: for this account
 * they are empty.
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

    // Usage summary teardown. The graph has circular delete constraints
    // (a ratable summary can be held by a usage summary and vice versa), so the
    // teardown alternates objects and converges. Six rounds has been ample on an
    // org with 831 summaries; the cap only exists so a pathological graph cannot
    // spin. In practice QUERY_RESERVE ends a run first, after four or five rounds
    // (the preflight's reads come first, their number depending on the user and the
    // account, and a round needs 59 left to start; the preflight stops, changing nothing,
    // rather than leave fewer), and the next run carries on.
    //
    // TEARDOWN_BATCH is a per-QUERY ceiling only -- it does NOT bound the
    // transaction. The 10,000-row DML limit is per transaction and this loop
    // issues nine deletes per round, so the real guard is the remaining-budget
    // clamp inside deleteRows(), which stops the run with a Result instead of
    // a LimitException.
    private static final Integer MAX_TEARDOWN_ROUNDS = 6;
    private static final Integer TEARDOWN_BATCH = 2000;

    // The queries one teardown round issues, and what is kept back for phase 2. Phase 2's
    // fixed queries total at most 43 (counted from the code, with every option on and
    // data in every branch): 27 before the asset step (order data 10, collections 5,
    // schedule groups 1, billing 7, fulfillment 2, contracts 2), the asset step's rate
    // card entries 1, its lookup of entitlements bound to the assets 1 and its other
    // lookups 8, quotes and opportunities 5 = 42 on the drained path, plus the journal
    // query, which only the undrained path runs = 43. The permission checks moved to the
    // preflight, and the rate card entries moved here from phase 1. 29 is what an account with no such data measures.
    // QUERY_RESERVE covers the 43 and the usage retries. A round starts only while both
    // are left; otherwise a large usage graph would spend phase 2's queries and end in a
    // LimitException. A test holds the measured 29 and the reserve against the 43.
    private static final Integer QUERIES_PER_ROUND = 9;
    @TestVisible
    private static final Integer QUERY_RESERVE = 50;
    @TestVisible
    private static final Integer PHASE_TWO_FIXED_MAX = 43;
    // The bucket walks (usage retries, the asset step's usage block) issue a number of
    // queries that grows with the tree. Each walk query first requires the queries that
    // can follow it before the next guard or the end of phase 2, counted from the code:
    //  - RETRY_TAIL, for the usage retries: at most 26 follow the journal guard (journal 1,
    //    collections 5, schedule groups 1, billing 7, fulfillment 2, contracts 2, the asset
    //    step with no assets 3, quotes and opportunities 5). 30 keeps four spare.
    //  - ASSET_TAIL, for the asset step: at most 13 follow its last guard (other asset
    //    references 2, resource policies 3, rate card entries 1, assets 2, quotes and
    //    opportunities 5). 16 keeps three spare.
    // No walk can end in a LimitException. Sizing the guards by position stops a run with a
    // "run again" reason a little less often than one flat figure would; either way a stopped
    // run converges, because phase 1's progress persists. These figures must grow with any
    // query added after a guard; the tests cannot catch growth in the data-dependent branches.
    @TestVisible
    private static final Integer RETRY_TAIL = 30;
    @TestVisible
    private static final Integer ASSET_TAIL = 16;
    private static final Integer UNSEEN_QUERIES = 4;

    private static final String RUN_AGAIN = 'Run the reset again; it continues from where this run stopped.';
    // Reached only when the round cap binds before the query budget does: a caller with
    // more than the synchronous 100 queries (asynchronous gets 200). Tests lower the cap
    // through maxTeardownRoundsForTest.
    private static final String USAGE_TOO_LARGE = 'The account has more usage records than one run can remove.';
    private static final String ROLLED_BACK_FOREIGN_BUCKET =
        'not deleted: the run was rolled back; the bucket holds, or is above, another account\'s entitlement';
    private static final String FOREIGN_BUCKET = 'kept: holds, or is above, another account\'s entitlement';
    private static final String INCOMPLETE_BUCKETS = 'Usage Entitlement Buckets: the list of buckets the rollback restored may be '
        + 'incomplete, because the query limit was reached while listing them';
    private static final String DML_LIMIT = 'The reset reached the Salesforce limit on record changes in one run.';
    private static final String QUERY_LIMIT = 'The reset reached the Salesforce limit on queries in one run.';
    // Preflight refusal. Plain wording: the reset was not run.
    private static final String REFUSED = 'The reset was not run, and nothing was changed: the user running it '
        + 'cannot delete everything it would delete.';
    private static final String REFUSED_ADVICE = 'Ask a user with that access, or with Modify All Data, to run it, '
        + 'or have the records reassigned to the user running the reset.';
    private static final String PREFLIGHT_TOO_LARGE = 'The reset was not run, and nothing was changed: checking '
        + 'what it would delete left too few queries for the reset itself in one run. Running it again as the same '
        + 'user stops at the same point; a user with Modify All Data and View All Data needs far fewer queries for '
        + 'that check.';
    private static final String NO_PERMISSION = 'no permission to delete this kind of record';
    private static final String NO_ACCESS = 'no delete access to these records';
    private static final String NOT_VISIBLE = 'not visible to the user running the reset';
    private static final String CANNOT_READ = 'the user running the reset cannot read this kind of record';
    private static final String NEEDS_EDIT_ACTIVATED = 'activated; setting them back to Draft needs the Edit '
        + 'Activated Orders permission';
    private static final String NEEDS_LIFECYCLE = 'lifecycle-managed; deleting them needs the Access '
        + 'Lifecycle-Managed Assets permission';
    private static final String INVOICE_NEEDS_PERMISSION = 'not Draft or Canceled; deleting them needs the '
        + 'Delete Invoice and Invoice Lines permission (permission set RLM_DeleteInvoices)';
    private static final String INVOICE_IN_PROGRESS = 'still processing; run the reset once they finish';
    // Names listed per object in a refusal; the rest are counted.
    private static final Integer NAMES_LISTED = 5;
    private static final String PAYMENTS_KEPT = 'payments are not deleted: Salesforce does not allow deleting processed payments';
    private static final String MEMO_ON_KEPT_INVOICE = 'applied to an invoice that was not deleted';
    private static final String DEBIT_MEMOS_KEPT = 'posted or void; Salesforce does not allow deleting them, or canceling a posted one';

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
        public Boolean DeleteCollectionPlans;

        // Optional (required=false) so callers that don't pass it keep working;
        // a null value is treated as false.
        @InvocableVariable(required=false)
        public Boolean PreserveContractsWithContractedPrices;
    }

    /**
     * What the reset did. When `completed` is false the run stopped early or
     * failed, everything phase 2 deleted was rolled back, and `reason` says why.
     * `cleared` is true only when the run completed and kept nothing.
     */
    public class Result {
        @InvocableVariable(label='Completed' description='True when every reset step ran.')
        public Boolean completed;

        @InvocableVariable(label='Cleared' description='True when the reset completed and kept nothing.')
        public Boolean cleared;

        @InvocableVariable(label='Reason' description='Why the reset stopped, when it did not complete.')
        public String reason;

        @InvocableVariable(label='Removed' description='Records the reset deleted, by object.')
        public String removedSummary;

        @InvocableVariable(label='Retained' description='Records the reset did not delete, by object, with the reason.')
        public String retainedSummary;
    }

    /** Ends a run early when a limit is close, before the platform throws a LimitException. */
    private class ResetStoppedException extends Exception {}

    /**
     * What the current run removed and kept. Copied before phase 2, so that a
     * rollback can restore what phase 1 actually did.
     */
    private class ResetReport {
        public List<String> removedLabels = new List<String>();
        public Map<String, Integer> removed = new Map<String, Integer>();
        public List<Kept> kept = new List<Kept>();
        // Rows a delete refused, with the error. A later attempt that removes the
        // row (the usage loop retries every round) takes it back out.
        public Map<Id, String> refused = new Map<Id, String>();
        // Buckets the usage retries left alone because they hold another account's
        // entitlement, or sit above one that does. A Set, so a bucket the retries meet
        // again is counted once.
        public Set<Id> foreignBuckets = new Set<Id>();
        // True when the bucket list after a rollback ran out of queries part way.
        public Boolean incompleteBuckets = false;

        public ResetReport copy() {
            ResetReport c = new ResetReport();
            c.removedLabels = removedLabels.clone();
            c.removed = removed.clone();
            c.kept = kept.clone();
            c.refused = refused.clone();
            c.foreignBuckets = foreignBuckets.clone();
            c.incompleteBuckets = incompleteBuckets;
            return c;
        }
    }

    /** Rows of one object kept for one reason. Replaced, never changed, so a shallow copy of the list is safe. */
    private class Kept {
        public String label;
        public String why;
        public Integer count;

        public Kept(String label, String why, Integer count) {
            this.label = label;
            this.why = why;
            this.count = count;
        }
    }

    private static ResetReport report = new ResetReport();

    // The preflight of the current run, whose rows phase 1 reuses instead of querying again.
    private static Preflight preflight;

    // The account's assets and contracts, read at the start of the run by several
    // steps in both phases. The reset never creates either.
    private static Set<Id> accountAssetIds = new Set<Id>();
    private static Set<Id> accountContractIds = new Set<Id>();

    // True when the last teardown round found no usage rows at all. Phase 2 then
    // skips the passes that only retry rows the teardown could not delete.
    private static Boolean usageDrained = false;

    // Rows the current teardown round found, deleted or not.
    private static Integer roundFound = 0;

    // Lets a test fail phase 2 after it has deleted something, to prove the rollback.
    @TestVisible
    private static Exception phaseTwoFailureForTest;

    // Lets a test shrink the teardown round cap. In a synchronous run the query budget
    // always ends the loop first (a round needs 59 queries left, and 100 allow at most four or five, depending on the
    // queries the preflight spends before the loop), so
    // USAGE_TOO_LARGE is the cap for callers with more queries (asynchronous, 200); a
    // test reaches it by lowering the cap.
    @TestVisible
    private static Integer maxTeardownRoundsForTest;

    // Lets a test cap the queries the rollback's bucket listing may spend (the two
    // lookups included), which a real run reaches only after phase 2 has spent nearly
    // all of them: under 4 stops it before any lookup; 4 lets the two lookups and two
    // levels of a deep tree through and stops the walk part way.
    @TestVisible
    private static Integer unseenQueriesForTest;
    // Queries the last rollback listing spent, so a test can tell which way it stopped.
    @TestVisible
    private static Integer unseenListQueriesSpentForTest;

    // Queries phase 2 spent in the last run, for a test to hold against PHASE_TWO_FIXED_MAX.
    @TestVisible
    private static Integer phaseTwoQueriesForTest;
    private static Integer phaseTwoQueriesAtStart;

    // Lets a test shrink the DML row budget, to prove a run that runs out stops cleanly.
    @TestVisible
    private static Integer dmlRowLimitForTest;

    // Let a test run as a user who cannot read, or has no delete permission on, these
    // objects (canRead, objectDeletable), since a test user cannot be given the usage and
    // core object access the reset also needs.
    @TestVisible
    private static Set<String> unreadableForTest = new Set<String>();
    @TestVisible
    private static Set<String> undeletableForTest = new Set<String>();

    /**
     * The account's orders, invoices and fulfillment records, queried once at the
     * start of phase 2 and shared by the steps that delete them. Invoices are queried
     * only for a step that uses them, and the fulfillment graph only when it is going to
     * be deleted; an object the user cannot read is skipped (the preflight refused the
     * run if it had records here).
     */
    private class OrderData {
        public List<Order> orders;
        public Set<Id> orderIds;
        public Set<Id> orderItemIds;
        // Status and PaymentScheduleId are for Delete Billing; the Ids also find the
        // fulfillment orders and disputes raised against an invoice.
        public List<Invoice> invoices = new List<Invoice>();

        public List<FulfillmentOrder> fulfillmentOrders = new List<FulfillmentOrder>();
        public List<FulfillmentPlan> fulfillmentPlans = new List<FulfillmentPlan>();
        public Set<Id> fulfillmentStepIds = new Set<Id>();
        public List<FulfillmentAsset> fulfillmentAssets = new List<FulfillmentAsset>();
        public Set<Id> fulfillmentAssetIds = new Set<Id>();
        public List<FulfillmentOrderLineItem> fulfillmentOrderLineItems = new List<FulfillmentOrderLineItem>();
        public List<FulfillmentLineSourceRel> fulfillmentLineSourceRels = new List<FulfillmentLineSourceRel>();

        public OrderData(Id accountId, Boolean withInvoices, Boolean withFulfillment) {
            this.orders = [SELECT Id FROM Order WHERE AccountId = :accountId];
            this.orderIds = new Map<Id, Order>(this.orders).keySet();
            this.orderItemIds = new Map<Id, OrderItem>(
                [SELECT Id FROM OrderItem WHERE Order.AccountId = :accountId]).keySet();
            // Not for a run that deletes neither billing, collections nor fulfillment: live
            // 264, this query failed for the salesrep persona, who cannot read invoices
            // ("sObject type 'Invoice' is not supported"), on every reset.
            if (withInvoices && canRead('Invoice')) {
                this.invoices = [
                    SELECT Id, Status, PaymentScheduleId FROM Invoice WHERE BillingAccountId = :accountId
                ];
            }
            if (withFulfillment) {
                loadFulfillment(accountId);
            }
        }

        /**
         * Queried in dependency order: fulfillment orders reference orders,
         * invoices and order summaries; plans reference orders and order items;
         * steps reference plans; line items reference fulfillment orders; source
         * relations reference order items and line items.
         */
        private void loadFulfillment(Id accountId) {
            Set<String> sourceIdentifiers = new Set<String>();
            for (Id orderItemId : this.orderItemIds) {
                sourceIdentifiers.add(orderItemId);
            }
            for (Id orderId : this.orderIds) {
                sourceIdentifiers.add(orderId);
            }
            Set<Id> invoiceIds = new Map<Id, Invoice>(this.invoices).keySet();
            Set<Id> fulfillmentOrderIds = new Set<Id>();
            if (canRead('FulfillmentOrder')) {
                Set<Id> summaryIds = new Set<Id>();
                if (canRead('OrderSummary')) {
                    summaryIds = new Map<Id, OrderSummary>(
                        [SELECT Id FROM OrderSummary WHERE AccountId = :accountId]).keySet();
                }
                this.fulfillmentOrders = [
                    SELECT Id
                    FROM FulfillmentOrder
                    WHERE AccountId = :accountId
                    OR OrderId IN :this.orderIds
                    OR InvoiceId IN :invoiceIds
                    OR OrderSummaryId IN :summaryIds
                ];
                fulfillmentOrderIds = new Map<Id, FulfillmentOrder>(this.fulfillmentOrders).keySet();
            }
            if (canRead('FulfillmentPlan')) {
                this.fulfillmentPlans = [
                    SELECT Id
                    FROM FulfillmentPlan
                    WHERE SourceIdentifier IN :sourceIdentifiers
                    AND (SourceType = 'StandardOrder' OR SourceType = 'OrderItem')
                ];
                if (canRead('FulfillmentStep')) {
                    Set<Id> planIds = new Map<Id, FulfillmentPlan>(this.fulfillmentPlans).keySet();
                    this.fulfillmentStepIds = new Map<Id, FulfillmentStep>(
                        [SELECT Id FROM FulfillmentStep WHERE FulfillmentPlanId IN :planIds]).keySet();
                }
            }
            if (canRead('FulfillmentAsset')) {
                this.fulfillmentAssets = [SELECT Id FROM FulfillmentAsset WHERE AccountId = :accountId];
                this.fulfillmentAssetIds = new Map<Id, FulfillmentAsset>(this.fulfillmentAssets).keySet();
            }
            Set<Id> lineItemIds = new Set<Id>();
            if (canRead('FulfillmentOrderLineItem')) {
                this.fulfillmentOrderLineItems = [
                    SELECT Id FROM FulfillmentOrderLineItem WHERE FulfillmentOrderId IN :fulfillmentOrderIds
                ];
                lineItemIds = new Map<Id, FulfillmentOrderLineItem>(this.fulfillmentOrderLineItems).keySet();
            }
            if (canRead('FulfillmentLineSourceRel')) {
                this.fulfillmentLineSourceRels = [
                    SELECT Id
                    FROM FulfillmentLineSourceRel
                    WHERE SourceLineItemId IN :this.orderItemIds
                    OR FulfilmentOrderLineId IN :lineItemIds
                ];
            }
        }
    }

    /**
     * Main Method
     * Entry point for the account reset; see the class header for its two phases.
     *
     * @param request One InputVariables: the account, and which records to delete
     * @return One Result for the request, or none for an empty request
     */
    @InvocableMethod(label='Reset Account Related Objects' description='Deletes the records built on an account so it can be sold to again, and reports what it removed and what it kept')
    public static List<Result> delAccountRelatedObjects(List<InputVariables> request) {
        if (request == null || request.isEmpty()) {
            return new List<Result>();
        }
        if (request.size() > 1) {
            throw new IllegalArgumentException('RLM_AccountUtilities.delAccountRelatedObjects: only one request at a time is supported.');
        }
        return new List<Result>{ resetAccount(request.get(0)) };
    }

    private static Result resetAccount(InputVariables input) {
        startRun();
        Id accountId = toAccountId(input.accountId);
        if (accountId == null) {
            return finish(false, 'Not an Account Id: ' + input.accountId);
        }
        Boolean deleteAssets = input.DeleteAssets == true;
        Boolean deleteFulfillment = input.DeleteFulfillment == true;
        Boolean deleteBilling = input.DeleteBilling == true;
        // '== true' collapses both null (flag omitted) and false to false, so the
        // default/unchecked behavior is identical to the legacy delete-all path.
        Boolean deleteCollections = input.DeleteCollectionPlans == true;
        Boolean preserveContractsWithPrices = input.PreserveContractsWithContractedPrices == true;

        // ------------------------------------------------------------------
        // Preflight: read only. If the user could not delete everything the run would
        // delete, nothing is changed and the Result lists why (see the class header).
        try {
            preflight = new Preflight(
                accountId, deleteAssets, deleteFulfillment, deleteBilling, deleteCollections, preserveContractsWithPrices);
        } catch (PreflightTooLargeException e) {
            return refuse(PREFLIGHT_TOO_LARGE);
        }
        if (!preflight.blockers.isEmpty()) {
            return refuse(REFUSED + ' ' + preflight.describeBlockers() + '. ' + REFUSED_ADVICE);
        }

        // ------------------------------------------------------------------
        // Phase 1: the usage graph, BEFORE the savepoint, deliberately.
        //
        // It is idempotent and convergent -- a rerun simply finds fewer rows --
        // and its partial progress MUST survive a later failure. Inside the
        // savepoint, a single exception anywhere in the order/asset/quote
        // cleanup below would roll back every usage row removed here, so the
        // reset could never converge across reruns: each attempt would start
        // from the same untouched graph and surface the same blocker. That is
        // exactly what made the original failure so hard to diagnose, and it
        // would defeat the DML-budget clamp in deleteRows(), whose whole point
        // is that a partial teardown is real progress to build on.
        //
        // Nothing here is coupled to the transactional deletes below, so there
        // is no atomicity to preserve -- only progress to lose. For the same
        // reason a failure here is returned as a Result rather than thrown: a
        // thrown exception fails the flow, which rolls back the whole
        // transaction, this progress included.
        try {
            // The preflight already read the assets, contracts, binding policies and rate
            // card entries, in system mode, and they are all the user's to delete.
            accountAssetIds = new Map<Id, SObject>(preflight.rowsOf('Asset')).keySet();
            accountContractIds = new Map<Id, SObject>(preflight.rowsOf('Contract')).keySet();

            deleteQuietly(preflight.rowsOf('BindingObjUsageRsrcPlcy'));
            deleteQuietly(preflight.rowsOf('BindingObjectRateCardEntry'));

            // The summary graph must go FIRST. A UsageEntitlementEntry holds its
            // UsageSummary, and a bucket cannot be deleted while entitlement entries
            // still reference it -- so tearing down buckets before the summaries
            // (the previous order) fails on any account whose usage was ever rated.
            // Not when the preflight found no usage records: nothing to tear down.
            if (preflight.hasUsage) {
                deleteUsageSummaryGraph(accountId);
            } else {
                usageDrained = true;
            }
        } catch (ResetStoppedException e) {
            return finish(false, e.getMessage()
                + ' The usage records removed so far stay deleted; nothing else was touched. ' + RUN_AGAIN);
        } catch (Exception e) {
            return finish(false, 'The usage cleanup failed: ' + e.getMessage()
                + ' The usage records it removed stay deleted; nothing else was touched.');
        }

        // ------------------------------------------------------------------
        // Phase 2: inside the savepoint. All of it is kept, or none of it.
        Savepoint sp = Database.setSavepoint();
        phaseTwoQueriesAtStart = Limits.getQueries();
        ResetReport afterPhaseOne = report.copy();
        try {
            OrderData orderData = new OrderData(
                accountId, deleteBilling || deleteCollections || deleteFulfillment, deleteFulfillment);

            if (!usageDrained) {
                // The teardown loop left rows it could not delete. Retry them along
                // the bucket hierarchy, which the loop does not follow.
                deleteTransactionUsageEntitlement(accountId);
                deleteUsageEntitlementAccount(accountId);
                // Again: a TUE whose bucket an entitlement account held can go now.
                deleteTransactionUsageEntitlement(accountId);
                // Final sweep. The convergent teardown already drains journals as
                // their summaries release them; anything still here refused to delete
                // and will block asset deletion, so say so rather than failing later.
                deleteTransactionJournal(accountId);
            }

            // Before billing: deleting an invoice clears a dispute's link to it.
            if (deleteCollections) {
                deleteCollectionRecords(accountId, orderData.invoices);
            }

            // Delete Billing information
            deleteBillingScheduleGroups(accountId);
            if (deleteBilling) {
                deleteBillingRecords(accountId, orderData);
            }

            // Handle fulfillment records if needed (before contracts and orders)
            if (deleteFulfillment) {
                deleteFulfillmentLineSourceRel(orderData);
                deleteFulfillmentStepSource(orderData);
                deleteFulfillmentOrderLineItem(orderData);
                deleteFulfillmentOrder(orderData);
            }

            // Then handle contracts and orders
            deleteContracts(accountId, preserveContractsWithPrices);
            deleteOrders(orderData);

            if (deleteFulfillment) {
                deleteFulfillmentPlan(orderData);
                deleteAssetFulfillmentDecomp(orderData);
                deleteFulfillmentAsset(orderData);
            }

            // Handle assets if needed
            if (deleteAssets) {
                // In phase 2, so a rollback restores them with the assets. Gated on
                // deleteAssets, like the asset deletion itself: AssetRateCardEntry rows are
                // generated when the asset is created and are NOT recreated for an existing
                // asset, so removing them while KEEPING the asset leaves a usage asset that
                // can never rate again.
                deleteAssetRateCardEntries();
                // Before deleting assets, clean up ALL records that might reference them
                deleteAllRecordsReferencingAssets(accountId);

                // Second pass over the binding policies. They are cleared at the top
                // of this method, but the entitlement teardown in between leaves more
                // behind, and an asset cannot be deleted while any remain:
                //   "could not be completed because it is associated with the
                //    following binding object usage resource policies.: BOURP-..."
                // Clearing them once up front is not enough. A policy that still
                // refuses is reported as retained, and the asset delete below then
                // fails with the platform's reason.
                deleteUsageResourcePolicies(accountId);
                deleteBindingObjRateCardEntries(accountId);

                deleteAssets();
            }

            // Finally handle remaining objects. QuoteAccountId is the quote's own
            // account and AccountId its opportunity's; a quote can have either alone.
            List<Quote> accountQuotes = [
                SELECT Id FROM Quote WHERE QuoteAccountId = :accountId OR AccountId = :accountId
            ];
            // Delete quote-linked ContentDocuments before quotes are removed
            deleteQuoteDocuments(accountQuotes);
            deleteAll(accountQuotes);
            deleteAll([SELECT Id FROM Opportunity WHERE AccountId = :accountId]);

            if (phaseTwoFailureForTest != null) {
                throw phaseTwoFailureForTest;
            }
        } catch (Exception e) {
            Database.rollback(sp);
            phaseTwoQueriesForTest = Limits.getQueries() - phaseTwoQueriesAtStart;
            report = afterPhaseOne;
            reportUnseenBuckets(accountId);
            String cause = e instanceof ResetStoppedException ? e.getMessage() + ' ' + RUN_AGAIN : e.getMessage();
            String kept = report.removedLabels.isEmpty()
                ? 'Nothing was deleted; the run was rolled back. '
                : 'Only what the usage cleanup deleted stays deleted (see Removed); everything else was rolled back. ';
            return finish(false, kept + cause);
        }
        phaseTwoQueriesForTest = Limits.getQueries() - phaseTwoQueriesAtStart;
        return finish(true, null);
    }

    /**
     * The Result of a run the preflight refused: not completed, nothing removed, and the
     * reason that lists why. Nothing was changed, so there is nothing else to report.
     */
    private static Result refuse(String reason) {
        Result result = new Result();
        result.completed = false;
        result.cleared = false;
        result.reason = reason;
        return result;
    }

    @TestVisible
    private static void startRun() {
        report = new ResetReport();
        describedTypes = null;
        userPermissions = null;
        preflight = null;
        accountAssetIds = new Set<Id>();
        accountContractIds = new Set<Id>();
        usageDrained = false;
        unseenListQueriesSpentForTest = null;
    }

    /** The Id when `value` is an Account Id, else null. */
    private static Id toAccountId(String value) {
        if (String.isBlank(value)) {
            return null;
        }
        try {
            Id candidate = Id.valueOf(value);
            return candidate.getSObjectType() == Account.SObjectType ? candidate : null;
        } catch (StringException e) {
            return null;
        }
    }

    private static Result finish(Boolean completed, String reason) {
        // Refusals become retained rows. A refused row that a later attempt deleted
        // was taken back out; one that went with its parent came back as
        // ENTITY_IS_DELETED and never got in.
        Map<Schema.SObjectType, Integer> refusedCount = new Map<Schema.SObjectType, Integer>();
        Map<Schema.SObjectType, String> firstError = new Map<Schema.SObjectType, String>();
        for (Id rowId : report.refused.keySet()) {
            Schema.SObjectType type = rowId.getSObjectType();
            if (!refusedCount.containsKey(type)) {
                refusedCount.put(type, 0);
                firstError.put(type, report.refused.get(rowId));
            }
            refusedCount.put(type, refusedCount.get(type) + 1);
        }
        for (Schema.SObjectType type : refusedCount.keySet()) {
            recordRetained(type, refusedCount.get(type), 'could not be deleted: ' + firstError.get(type));
        }

        recordRetained(UsageEntitlementBucket.SObjectType, report.foreignBuckets.size(), FOREIGN_BUCKET);

        List<String> removed = new List<String>();
        for (String label : report.removedLabels) {
            removed.add(label + ': ' + report.removed.get(label));
        }
        List<String> kept = new List<String>();
        for (Kept k : report.kept) {
            kept.add(k.label + ': ' + k.count + ' (' + k.why + ')');
        }

        if (report.incompleteBuckets) {
            kept.add(INCOMPLETE_BUCKETS);
        }

        Result result = new Result();
        result.completed = completed;
        result.cleared = completed && kept.isEmpty();
        result.reason = reason;
        result.removedSummary = removed.isEmpty() ? null : String.join(removed, '; ');
        result.retainedSummary = kept.isEmpty() ? null : String.join(kept, '; ');
        return result;
    }

    private static String labelOf(Schema.SObjectType type) {
        return type.getDescribe().getLabelPlural();
    }

    private static void recordRemoved(Schema.SObjectType type, Integer count) {
        if (count <= 0) {
            return;
        }
        String label = labelOf(type);
        if (!report.removed.containsKey(label)) {
            report.removedLabels.add(label);
            report.removed.put(label, 0);
        }
        report.removed.put(label, report.removed.get(label) + count);
    }

    private static void recordRetained(Schema.SObjectType type, Integer count, String why) {
        if (count <= 0) {
            return;
        }
        String label = labelOf(type);
        for (Integer i = 0; i < report.kept.size(); i++) {
            Kept k = report.kept[i];
            if (k.label.equals(label) && k.why.equals(why)) {
                report.kept[i] = new Kept(label, why, k.count + count);
                return;
            }
        }
        report.kept.add(new Kept(label, why, count));
    }

    // The org's object types, described once per run.
    private static Map<String, Schema.SObjectType> describedTypes;

    private static Schema.SObjectType typeOf(String objectName) {
        if (describedTypes == null) {
            describedTypes = Schema.getGlobalDescribe();
        }
        return describedTypes.get(objectName);
    }

    /**
     * True when the org has the object and the running user can read it. Live 264, a
     * query on an object the user cannot read failed in this class although it runs
     * without sharing ("sObject type 'Invoice' is not supported", the salesrep persona),
     * and isAccessible() was false for exactly the objects whose queries failed.
     */
    @TestVisible
    private static Boolean canRead(String objectName) {
        if (unreadableForTest.contains(objectName)) {
            return false;
        }
        Schema.SObjectType type = typeOf(objectName);
        return type != null && type.getDescribe().isAccessible();
    }

    /**
     * True when the user has delete permission on the object. Live 264 that is also what
     * reflects Allow Revenue Records Deletion for credit memos: isDeletable() was false
     * without it and true with it, for a System Administrator.
     */
    private static Boolean objectDeletable(String objectName) {
        if (undeletableForTest.contains(objectName)) {
            return false;
        }
        Schema.SObjectType type = typeOf(objectName);
        return type != null && type.getDescribe().isDeletable();
    }

    // The running user's permissions, read once per user: the core ones statically, in one
    // query, and the billing and lifecycle ones dynamically in another, so a release
    // without one of those fields reads it as false and nothing else.
    private static Map<String, Boolean> userPermissions;
    private static Id userPermissionsOf;
    private static final Set<String> CORE_PERMISSIONS = new Set<String>{
        'PermissionsModifyAllData', 'PermissionsViewAllData', 'PermissionsEditActivatedOrders'
    };
    private static final List<String> OTHER_PERMISSIONS = new List<String>{
        'PermissionsBillingInvoiceSuperUser', 'PermissionsDeleteRevenueRecords', 'PermissionsCalmSobjectAccessUser'
    };

    /**
     * Whether the running user has the permission, from their profile, a permission set or
     * a group. UserPermissionAccess holds the user's effective permissions, and any user may
     * read their own; a non-admin is refused PermissionSetAssignment.
     */
    private static Boolean hasUserPermission(String field) {
        if (userPermissions == null || userPermissionsOf != UserInfo.getUserId()) {
            userPermissionsOf = UserInfo.getUserId();
            userPermissions = new Map<String, Boolean>();
        }
        if (!userPermissions.containsKey(field)) {
            if (CORE_PERMISSIONS.contains(field)) {
                UserPermissionAccess core = [
                    SELECT PermissionsModifyAllData, PermissionsViewAllData, PermissionsEditActivatedOrders
                    FROM UserPermissionAccess LIMIT 1
                ];
                userPermissions.put('PermissionsModifyAllData', core.PermissionsModifyAllData == true);
                userPermissions.put('PermissionsViewAllData', core.PermissionsViewAllData == true);
                userPermissions.put('PermissionsEditActivatedOrders', core.PermissionsEditActivatedOrders == true);
            } else {
                List<SObject> access = new List<SObject>();
                try {
                    access = Database.query('SELECT ' + String.join(OTHER_PERMISSIONS, ', ') + ' FROM UserPermissionAccess');
                } catch (QueryException e) {
                    access = new List<SObject>();
                }
                for (String name : OTHER_PERMISSIONS) {
                    userPermissions.put(name, !access.isEmpty() && access[0].get(name) == true);
                }
            }
        }
        return userPermissions.get(field) == true;
    }

    /**
     * True when the running user has BillingInvoiceSuperUser ("Delete Invoice and Invoice
     * Lines"). Live 264 it is the only permission that lets a Posted invoice be deleted,
     * settled or not; Allow Revenue Records Deletion alone is refused with "You can only
     * delete the invoice if it is in Draft or Canceled status."
     */
    @TestVisible
    private static Boolean canDeletePostedInvoices() {
        return hasUserPermission('PermissionsBillingInvoiceSuperUser');
    }

    /**
     * True when the running user has DeleteRevenueRecords ("Allow Revenue Records
     * Deletion", managed Billing Admin set). Live 264 it is what lets a Draft or Canceled
     * credit memo be deleted; Delete Invoice and Invoice Lines does not. It also lets
     * Draft and Canceled invoices go, but not Posted ones.
     */
    @TestVisible
    private static Boolean canDeleteRevenueRecords() {
        return hasUserPermission('PermissionsDeleteRevenueRecords');
    }

    // Rows the next DML statement may touch: what is left of the transaction's row
    // budget, or none once its statement budget is spent.
    private static Integer dmlRowsLeft() {
        if (Limits.getDmlStatements() >= Limits.getLimitDmlStatements()) {
            return 0;
        }
        Integer rowLimit = dmlRowLimitForTest != null ? dmlRowLimitForTest : Limits.getLimitDmlRows();
        return rowLimit - Limits.getDmlRows();
    }

    /**
     * Deletes the rows and records the outcome: rows that went count as removed,
     * rows that refused as retained unless a later attempt removes them. With
     * allOrNone, a refusal throws instead, which rolls back phase 2.
     *
     * The 10,000-row DML limit is per TRANSACTION, not per statement, and the
     * teardown loop alone issues nine deletes per round. So the list is clamped to
     * the remaining budget here -- one clamp covers every call site. Running out
     * deletes what fits and then stops the run with a ResetStoppedException,
     * rather than a LimitException that rolls back all the progress made.
     *
     * @return The ids that are gone, including rows a parent's delete already took
     */
    private static Set<Id> deleteRows(List<SObject> records, Boolean allOrNone) {
        Set<Id> gone = new Set<Id>();
        if (records == null || records.isEmpty()) {
            return gone;
        }
        Integer room = dmlRowsLeft();
        Boolean trimmed = records.size() > room;
        if (trimmed) {
            if (allOrNone || room <= 0) {
                throw new ResetStoppedException(DML_LIMIT);
            }
            List<SObject> fits = new List<SObject>();
            for (Integer i = 0; i < room; i++) {
                fits.add(records[i]);
            }
            records = fits;
        }
        Integer removed = 0;
        Database.DeleteResult[] results = Database.delete(records, allOrNone);
        for (Integer i = 0; i < results.size(); i++) {
            Id rowId = records[i].Id;
            if (results[i].isSuccess()) {
                removed++;
            } else if (results[i].getErrors()[0].getStatusCode() != StatusCode.ENTITY_IS_DELETED) {
                report.refused.put(rowId, results[i].getErrors()[0].getMessage());
                // Refused is the reason now; a bucket is never reported under both.
                report.foreignBuckets.remove(rowId);
                continue;
            }
            gone.add(rowId);
            report.refused.remove(rowId);
            report.foreignBuckets.remove(rowId);
        }
        recordRemoved(records[0].getSObjectType(), removed);
        if (trimmed) {
            throw new ResetStoppedException(DML_LIMIT);
        }
        return gone;
    }

    /**
     * Best-effort delete that reports how many rows went, so a convergence loop
     * can tell progress from a no-op round. A refusal is expected here (a row
     * still held by a parent) and is recorded, not thrown.
     */
    private static Integer deleteQuietly(List<SObject> records) {
        return deleteRows(records, false).size();
    }

    /** All-or-nothing delete: any refusal throws and rolls back phase 2. */
    private static void deleteAll(List<SObject> records) {
        deleteRows(records, true);
    }

    /**
     * All-or-nothing update, for a change made only on the way to a delete (an order set
     * back to Draft, a credit memo canceled): a refusal throws and rolls back phase 2.
     */
    private static void updateAll(List<SObject> records) {
        if (records.isEmpty()) {
            return;
        }
        if (records.size() > dmlRowsLeft()) {
            throw new ResetStoppedException(DML_LIMIT);
        }
        Database.update(records, true);
    }

    /** Stops the run while it still can, instead of letting the next query throw a LimitException. */
    private static void requireQueries(Integer needed) {
        if (Limits.getLimitQueries() - Limits.getQueries() < needed) {
            throw new ResetStoppedException(QUERY_LIMIT);
        }
    }

    /**
     * The usage retries and the asset step's usage block issue a number of queries
     * that grows with the bucket tree. Each one first requires the queries that can
     * follow it (`tail`: RETRY_TAIL or ASSET_TAIL), so a deep tree ends the run with a
     * reported reason instead of starving the later steps into an uncatchable
     * LimitException.
     */
    private static void requireWalkQueries(Integer tail) {
        requireQueries(1 + tail);
    }

    /**
     * Removes from `buckets` every bucket that holds an entitlement outside
     * `ownTueIds`, and every ancestor of one, and records them as kept: a reset never
     * touches another account's data, and a bucket cannot go while a child remains.
     * One exception, made by the asset step and not here: another account's entitlement
     * bound to one of this account's assets is deleted with the asset, and so is its bucket.
     * A bucket kept here and then deleted that way leaves the foreign set (deleteRows).
     * The ids come out of `report.refused` too, so a bucket is reported once.
     */
    private static void keepForeignBuckets(Map<Id, UsageEntitlementBucket> buckets, Set<Id> ownTueIds) {
        Set<Id> keep = foreignBucketIds(buckets, ownTueIds);
        buckets.keySet().removeAll(keep);
        report.foreignBuckets.addAll(keep);
        report.refused.keySet().removeAll(keep);
    }

    /** The buckets that hold an entitlement outside `ownTueIds`, and every ancestor of one. */
    private static Set<Id> foreignBucketIds(Map<Id, UsageEntitlementBucket> buckets, Set<Id> ownTueIds) {
        Set<Id> keep = new Set<Id>();
        for (UsageEntitlementBucket bucket : buckets.values()) {
            if (bucket.TransactionUsageEntitlementId == null
                || ownTueIds.contains(bucket.TransactionUsageEntitlementId)) {
                continue;
            }
            UsageEntitlementBucket up = bucket;
            while (up != null && keep.add(up.Id)) {
                up = buckets.get(up.ParentId);
            }
        }
        return keep;
    }

    /**
     * Delete Collection Plans: the account's collection plans with their items,
     * promise-to-pay payment schedules and cases, then its disputes, including
     * those raised against its invoices, with their items and cases. Only the
     * account's own cases go, and only those of a plan or dispute that was deleted.
     *
     * Deleting a plan does not take its cases (Case.SourceId) or promise-to-pay
     * schedules (PaymentSchedule.ReferenceEntityId or CollectionPlanItemId) with it,
     * it clears their link to the plan, so both are found before the plan goes. A
     * case cannot be deleted while a dispute references it, so cases go last. Plan,
     * dispute and payment schedule items go with their parents (live 264).
     *
     * Queried dynamically, so the class still deploys to an org without Collections
     * or Billing Dispute Management.
     */
    private static void deleteCollectionRecords(Id accountId, List<Invoice> invoices) {
        // An object the user cannot read is skipped: the preflight refused the run if it
        // had records here. Without Case read, there are no cases of plans or disputes.
        Boolean casesReadable = canRead('Case');
        Set<Id> caseIds = new Set<Id>();
        if (canRead('CollectionPlan')) {
            List<SObject> plans = Database.query('SELECT Id FROM CollectionPlan WHERE AccountId = :accountId');
            Set<Id> planIds = new Map<Id, SObject>(plans).keySet();
            if (!planIds.isEmpty()) {
                // Bound, not a semi-join: SOQL does not allow a semi-join inside OR.
                Set<Id> itemIds = new Map<Id, SObject>(Database.query(
                    'SELECT Id FROM CollectionPlanItem WHERE CollectionPlanId IN :planIds')).keySet();
                if (canRead('PaymentSchedule')) {
                    deleteQuietly(Database.query('SELECT Id FROM PaymentSchedule WHERE ReferenceEntityId IN :planIds '
                        + 'OR CollectionPlanItemId IN :itemIds'));
                }
                Map<Id, Set<Id>> casesByPlan = new Map<Id, Set<Id>>();
                for (SObject planCase : !casesReadable ? new List<SObject>() : Database.query(
                    'SELECT Id, SourceId FROM Case WHERE SourceId IN :planIds AND AccountId = :accountId'
                )) {
                    Id planId = (Id) planCase.get('SourceId');
                    if (!casesByPlan.containsKey(planId)) {
                        casesByPlan.put(planId, new Set<Id>());
                    }
                    casesByPlan.get(planId).add(planCase.Id);
                }
                for (Id planId : deleteRows(plans, false)) {
                    if (casesByPlan.containsKey(planId)) {
                        caseIds.addAll(casesByPlan.get(planId));
                    }
                }
            }
        }
        if (canRead('Dispute')) {
            Set<Id> invoiceIds = new Map<Id, Invoice>(invoices).keySet();
            List<SObject> disputes = Database.query('SELECT Id, CaseId' + (casesReadable ? ', Case.AccountId' : '')
                + ' FROM Dispute WHERE AccountId = :accountId OR InvoiceId IN :invoiceIds');
            Set<Id> gone = deleteRows(disputes, false);
            for (SObject dispute : disputes) {
                SObject disputeCase = casesReadable ? dispute.getSObject('Case') : null;
                if (gone.contains(dispute.Id) && disputeCase != null && disputeCase.get('AccountId') == accountId) {
                    caseIds.add((Id) dispute.get('CaseId'));
                }
            }
        }
        List<Case> cases = new List<Case>();
        for (Id caseId : caseIds) {
            cases.add(new Case(Id = caseId));
        }
        deleteQuietly(cases);
    }

    /**
     * Delete Billing: the account's debit memos, then its invoices with their
     * documents and payment schedules, then its credit memos. Payments, and posted
     * or void debit memos, are left in place: Salesforce never allows deleting them.
     *
     * The preflight refused the run if any invoice is still processing, if a posted one
     * needs Delete Invoice and Invoice Lines the user lacks (live 264, the only permission
     * that deletes a Posted invoice), or if the user cannot delete the credit memos (Allow
     * Revenue Records Deletion, measured as the object's delete permission). So every
     * invoice queried here is one the user may delete, in ONE delete call that is never
     * retried. Do not add a retry: live 264, a second delete of a Posted invoice the
     * platform had just refused, in the same transaction, succeeded.
     *
     * Deleting an invoice takes its lines, taxes, billing period items, credit
     * memo and payment applications, and billing journals with it. It does not
     * take its payment schedule, files or DocumentGenerationProcess rows, which
     * are deleted here. An object the user cannot read is skipped: the preflight
     * refused the run if it had records here.
     */
    private static void deleteBillingRecords(Id accountId, OrderData orderData) {
        // First, so that a debit memo line adjusting an invoice line, or a debit
        // memo raised from a credit memo, is gone before either is deleted.
        deleteDebitMemos(accountId);

        Set<Id> keptInvoiceIds = new Set<Id>();
        if (canRead('Invoice')) {
            List<Invoice> invoices = orderData.invoices;
            // Collected first: the delete takes the files' links with it.
            Map<Id, Set<Id>> files = exclusiveFiles(new Map<Id, Invoice>(invoices).keySet());
            Set<Id> deleted = deleteRows(invoices, false);

            Set<Id> schedules = new Set<Id>();
            Set<Id> keptSchedules = new Set<Id>();
            for (Invoice inv : invoices) {
                Boolean gone = deleted.contains(inv.Id);
                if (!gone) {
                    keptInvoiceIds.add(inv.Id);
                }
                if (inv.PaymentScheduleId != null) {
                    if (gone) {
                        schedules.add(inv.PaymentScheduleId);
                    } else {
                        keptSchedules.add(inv.PaymentScheduleId);
                    }
                }
            }
            // A schedule that a kept invoice still uses stays. Deleting one takes its
            // PaymentScheduleItems with it.
            schedules.removeAll(keptSchedules);
            if (canRead('PaymentSchedule')) {
                List<PaymentSchedule> paymentSchedules = new List<PaymentSchedule>();
                for (Id scheduleId : schedules) {
                    paymentSchedules.add(new PaymentSchedule(Id = scheduleId));
                }
                deleteQuietly(paymentSchedules);
            }

            deleteGeneratedDocuments(deleted);
            Set<Id> orphanedFiles = new Set<Id>();
            for (Id fileId : files.keySet()) {
                if (deleted.containsAll(files.get(fileId))) {
                    orphanedFiles.add(fileId);
                }
            }
            deleteFiles(orphanedFiles);
        }

        // A user who cannot read invoices cannot read credit memo applications either
        // (that read depends on invoice read); the preflight refused the run if such a
        // user's account had credit memos to delete.
        if (canRead('CreditMemo') && canRead('CreditMemoInvApplication')) {
            deleteCreditMemos(accountId, keptInvoiceIds);
        }
        // Counted in system mode: payments are reported whether or not the user can read
        // them, since they are never deleted.
        recordRetained(Payment.SObjectType,
            [SELECT COUNT() FROM Payment WHERE AccountId = :accountId WITH SYSTEM_MODE], PAYMENTS_KEPT);
    }

    /**
     * A posted credit memo cannot be deleted, but it can be canceled and a canceled
     * one deleted, which takes its lines and journals with it (live 264). Memos
     * applied to an invoice that was kept are left alone: canceling one would
     * change that invoice's balance.
     */
    private static void deleteCreditMemos(Id accountId, Set<Id> keptInvoiceIds) {
        Set<Id> onKeptInvoices = new Set<Id>();
        if (!keptInvoiceIds.isEmpty()) {
            for (CreditMemoInvApplication application : [
                SELECT CreditMemoId FROM CreditMemoInvApplication WHERE InvoiceId IN :keptInvoiceIds
            ]) {
                onKeptInvoices.add(application.CreditMemoId);
            }
        }
        List<CreditMemo> deletable = new List<CreditMemo>();
        List<CreditMemo> posted = new List<CreditMemo>();
        Map<String, Integer> keptByStatus = new Map<String, Integer>();
        Integer applied = 0;
        for (CreditMemo memo : [SELECT Id, Status FROM CreditMemo WHERE BillingAccountId = :accountId]) {
            if (onKeptInvoices.contains(memo.Id)) {
                applied++;
            } else if (memo.Status == 'Draft' || memo.Status == 'Canceled') {
                deletable.add(memo);
            } else if (memo.Status == 'Posted') {
                memo.Status = 'Canceled';
                posted.add(memo);
            } else {
                Integer soFar = keptByStatus.containsKey(memo.Status) ? keptByStatus.get(memo.Status) : 0;
                keptByStatus.put(memo.Status, soFar + 1);
            }
        }
        recordRetained(CreditMemo.SObjectType, applied, MEMO_ON_KEPT_INVOICE);
        for (String status : keptByStatus.keySet()) {
            recordRetained(CreditMemo.SObjectType, keptByStatus.get(status),
                'status ' + status + ' can be neither canceled nor deleted');
        }
        // All or nothing: a refusal fails the run with the platform's message and rolls
        // phase 2 back, so no memo is left canceled but not deleted.
        updateAll(posted);
        for (CreditMemo canceled : posted) {
            deletable.add(new CreditMemo(Id = canceled.Id));
        }
        deleteAll(deletable);
    }

    /**
     * Deletes the account's debit memos, which takes their lines with them. A
     * posted debit memo can be voided but not canceled, and Salesforce refuses to
     * delete a posted or void one even with Delete Invoice and Invoice Lines (live
     * 264), so those are kept and reported. Queried dynamically, so the class does
     * not depend on DebitMemo to deploy.
     */
    private static void deleteDebitMemos(Id accountId) {
        Schema.SObjectType memoType = typeOf('DebitMemo');
        if (!canRead('DebitMemo')) {
            return;
        }
        List<SObject> deletable = new List<SObject>();
        Integer locked = 0;
        for (SObject memo : Database.query('SELECT Id, Status FROM DebitMemo WHERE AccountId = :accountId')) {
            String status = (String) memo.get('Status');
            if (status == 'Posted' || status == 'Void') {
                locked++;
            } else {
                deletable.add(memo);
            }
        }
        recordRetained(memoType, locked, DEBIT_MEMOS_KEPT);
        deleteQuietly(deletable);
    }

    /**
     * Maps each file linked to the given records to the records it is linked to,
     * leaving out files that are also linked anywhere else (to avoid deleting
     * files shared with Opportunities, Orders, etc.). Call it BEFORE deleting the
     * records: their ContentDocumentLinks go with them, and with the links the
     * only way to find the files.
     */
    @TestVisible
    private static Map<Id, Set<Id>> exclusiveFiles(Set<Id> parentIds) {
        Map<Id, Set<Id>> parentsByFile = new Map<Id, Set<Id>>();
        if (parentIds.isEmpty()) {
            return parentsByFile;
        }
        // Two queries however many records there are, not one per chunk: phase 2's
        // query budget is the fixed QUERY_RESERVE, so a count that grows with the
        // account could exceed it and end in a LimitException.
        for (ContentDocumentLink cdl : [
            SELECT ContentDocumentId, LinkedEntityId FROM ContentDocumentLink WHERE LinkedEntityId IN :parentIds
        ]) {
            if (!parentsByFile.containsKey(cdl.ContentDocumentId)) {
                parentsByFile.put(cdl.ContentDocumentId, new Set<Id>());
            }
            parentsByFile.get(cdl.ContentDocumentId).add(cdl.LinkedEntityId);
        }
        if (parentsByFile.isEmpty()) {
            return parentsByFile;
        }

        Set<Id> fileIds = new Set<Id>(parentsByFile.keySet());
        for (ContentDocumentLink cdl : [
            SELECT ContentDocumentId, LinkedEntityId, ShareType FROM ContentDocumentLink
            WHERE ContentDocumentId IN :fileIds
        ]) {
            // Skip: linked to one of our records (expected), or a personal-library
            // link (ShareType='I') auto-created by the platform for the file owner --
            // every document has one, so counting it would skip them all.
            // NOTE: ShareType cannot be filtered in SOQL here because Salesforce only
            // allows non-Id field filters on ContentDocumentLink when filtering by
            // LinkedEntityId with the equals operator — not with ContentDocumentId IN.
            if (parentIds.contains(cdl.LinkedEntityId) || cdl.ShareType == 'I') {
                continue;
            }
            parentsByFile.remove(cdl.ContentDocumentId);
        }
        return parentsByFile;
    }

    /** Deleting a ContentDocument takes its links and versions with it. */
    private static void deleteFiles(Set<Id> fileIds) {
        List<ContentDocument> files = new List<ContentDocument>();
        for (Id fileId : fileIds) {
            files.add(new ContentDocument(Id = fileId));
        }
        deleteQuietly(files);
    }

    /**
     * DocumentGenerationProcess rows name their record in a text field
     * (ReferenceObject), so nothing cascades them: they orphan silently when the
     * record is deleted.
     */
    private static void deleteGeneratedDocuments(Set<Id> recordIds) {
        // Skipped for a user who cannot read them: the preflight refused the run if any
        // were linked to the records this run deletes.
        if (recordIds.isEmpty() || !canRead('DocumentGenerationProcess')) {
            return;
        }
        deleteQuietly([SELECT Id FROM DocumentGenerationProcess WHERE ReferenceObject IN :recordIds]);
    }

    /**
     * Deletes the files and DocumentGenerationProcess rows of the account's quotes:
     * DocGen outputs and any manually attached quote files. Must be called BEFORE
     * the quotes are deleted, because the platform cascades their
     * ContentDocumentLink rows, making the files impossible to find afterwards.
     *
     * @param quotes Pre-fetched list of Quote records for the account
     */
    private static void deleteQuoteDocuments(List<Quote> quotes) {
        Set<Id> quoteIds = new Map<Id, Quote>(quotes).keySet();
        if (quoteIds.isEmpty()) {
            return;
        }
        deleteGeneratedDocuments(quoteIds);
        deleteFiles(exclusiveFiles(quoteIds).keySet());
    }

    /**
     * Deletes the account's orders, after setting them back to Draft: an
     * activated order cannot be deleted.
     *
     * @param orderData The OrderData object containing pre-queried information
     */
    private static void deleteOrders(OrderData orderData) {
        if (orderData.orders.isEmpty()) {
            return;
        }
        // All or nothing: a refusal fails the run with the platform's message and rolls
        // phase 2 back, so no order is left set back to Draft but not deleted.
        for (Order o : orderData.orders) {
            o.Status = 'Draft';
        }
        updateAll(orderData.orders);
        deleteAll(orderData.orders);
    }

    /**
     * The buckets whose parent is one of `parentIds` or which hold one of
     * `heldByTueIds`, and every descendant of those, one level per query. Each query
     * first requires `reserve` more, for what the run still has to do.
     */
    private static Map<Id, UsageEntitlementBucket> loadBucketTree(
        Set<Id> parentIds, Set<Id> heldByTueIds, Integer reserve
    ) {
        requireQueries(1 + reserve);
        Map<Id, UsageEntitlementBucket> buckets = new Map<Id, UsageEntitlementBucket>([
            SELECT Id, TransactionUsageEntitlementId, ParentId
            FROM UsageEntitlementBucket
            WHERE ParentId IN :parentIds
            OR TransactionUsageEntitlementId IN :heldByTueIds
        ]);
        Set<Id> frontier = new Set<Id>(buckets.keySet());
        while (!frontier.isEmpty()) {
            requireQueries(1 + reserve);
            Set<Id> known = new Set<Id>(buckets.keySet());
            List<UsageEntitlementBucket> children = [
                SELECT Id, TransactionUsageEntitlementId, ParentId
                FROM UsageEntitlementBucket
                WHERE ParentId IN :frontier
                AND Id NOT IN :known
            ];
            frontier = new Set<Id>();
            for (UsageEntitlementBucket child : children) {
                buckets.put(child.Id, child);
                frontier.add(child.Id);
            }
        }
        return buckets;
    }

    /**
     * After a phase 2 rollback: the account's buckets that are still there and that
     * the teardown loop never saw (a bucket holding no entitlement is not reachable
     * through an entitlement's account) are reported kept. Skipped when the loop
     * drained the usage graph. When too few queries are left to look, or the walk
     * runs out of them, the report says the list may be incomplete.
     */
    private static void reportUnseenBuckets(Id accountId) {
        if (usageDrained) {
            return;
        }
        Integer unseen = 0;
        Integer foreign = 0;
        Integer queriesAtStart = Limits.getQueries();
        try {
            Integer left = Limits.getLimitQueries() - Limits.getQueries();
            Integer allowance = unseenQueriesForTest != null ? unseenQueriesForTest : left;
            if (allowance < UNSEEN_QUERIES) {
                throw new ResetStoppedException(QUERY_LIMIT);
            }
            Set<Id> ueaIds = new Map<Id, UsageEntitlementAccount>(
                [SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :accountId]).keySet();
            Set<Id> tueIds = new Map<Id, TransactionUsageEntitlement>(
                [SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :accountId]).keySet();
            // The walk may spend `allowance` queries in all (the two lookups above count).
            Map<Id, UsageEntitlementBucket> tree = loadBucketTree(ueaIds, tueIds, left - allowance);
            // A completed run would keep these too, so they are not "rolled back" rows.
            Set<Id> foreignIds = foreignBucketIds(tree, tueIds);
            for (Id bucketId : tree.keySet()) {
                if (foreignIds.contains(bucketId)) {
                    // One chain gets one reason: a refused bucket above a foreign child
                    // is reported with the child, not with the platform's error.
                    report.refused.remove(bucketId);
                    foreign++;
                } else if (!report.refused.containsKey(bucketId)) {
                    unseen++;
                }
            }
        } catch (ResetStoppedException e) {
            report.incompleteBuckets = true;
        }
        unseenListQueriesSpentForTest = Limits.getQueries() - queriesAtStart;
        recordRetained(UsageEntitlementBucket.SObjectType, foreign, ROLLED_BACK_FOREIGN_BUCKET);
        recordRetained(UsageEntitlementBucket.SObjectType, unseen,
            'not deleted: the run was rolled back');
    }

    /**
     * Deletes the Usage Entitlement Buckets under the given entitlements (TUEs or
     * UEAs), leaves first: a bucket cannot go while it has children. For TUE
     * buckets, the TUE a leaf bucket holds is deleted just before the bucket.
     *
     * @param entitlementIds Set of entitlement IDs (TUE or UEA)
     * @param forTues True when `entitlementIds` are TUEs, false when UEAs
     * @param ownTueIds The account's own TUEs: a bucket holding any other stays
     */
    private static void deleteUsageEntitlementBucketsBottomUp(Set<Id> entitlementIds, Boolean forTues, Set<Id> ownTueIds) {
        Map<Id, UsageEntitlementBucket> buckets = loadBucketTree(
            entitlementIds, forTues ? entitlementIds : new Set<Id>(), RETRY_TAIL);
        // A bucket holding another account's entitlement, and the buckets above it, stay.
        keepForeignBuckets(buckets, ownTueIds);
        if (buckets.isEmpty()) {
            return;
        }

        // Leaves first, a level per round, until a round removes nothing.
        Set<Id> remaining = new Set<Id>(buckets.keySet());
        for (Integer round = 1; round <= 10 && !remaining.isEmpty(); round++) {
            Set<Id> parents = new Set<Id>();
            for (Id bucketId : remaining) {
                parents.add(buckets.get(bucketId).ParentId);
            }
            List<UsageEntitlementBucket> leaves = new List<UsageEntitlementBucket>();
            Set<Id> heldTues = new Set<Id>();
            for (Id bucketId : remaining) {
                if (!parents.contains(bucketId)) {
                    UsageEntitlementBucket leaf = buckets.get(bucketId);
                    leaves.add(leaf);
                    if (forTues && entitlementIds.contains(leaf.TransactionUsageEntitlementId)) {
                        heldTues.add(leaf.TransactionUsageEntitlementId);
                    }
                }
            }
            if (leaves.isEmpty()) {
                break;
            }
            if (!heldTues.isEmpty()) {
                requireWalkQueries(RETRY_TAIL);
                deleteQuietly([SELECT Id FROM TransactionUsageEntitlement WHERE Id IN :heldTues]);
            }
            Set<Id> gone = deleteRows(leaves, false);
            if (gone.isEmpty()) {
                break;
            }
            remaining.removeAll(gone);
        }
    }

    /**
     * Deletes Transaction Usage Entitlements (TUE) and their related Usage Entitlement Buckets (UEB)
     * for a given account.
     *
     * @param accountId The ID of the account whose TUEs should be deleted
     */
    private static void deleteTransactionUsageEntitlement(Id accountId) {
        requireWalkQueries(RETRY_TAIL);
        Set<Id> tueIds = new Map<Id, TransactionUsageEntitlement>(
            [SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :accountId]).keySet();
        if (tueIds.isEmpty()) {
            return;
        }
        // Buckets first, bottom-up; that also deletes the TUEs the buckets hold.
        deleteUsageEntitlementBucketsBottomUp(tueIds, true, tueIds);
        requireWalkQueries(RETRY_TAIL);
        deleteQuietly([SELECT Id FROM TransactionUsageEntitlement WHERE Id IN :tueIds]);
    }

    /**
     * Deletes Usage Entitlement Accounts (UEA) and their related Usage Entitlement Buckets (UEB)
     * for a given account.
     *
     * @param accountId The ID of the account whose UEAs should be deleted
     */
    private static void deleteUsageEntitlementAccount(Id accountId) {
        requireWalkQueries(RETRY_TAIL);
        Set<Id> ueaIds = new Map<Id, UsageEntitlementAccount>(
            [SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :accountId]).keySet();
        if (ueaIds.isEmpty()) {
            return;
        }
        requireWalkQueries(RETRY_TAIL);
        Set<Id> ownTueIds = new Map<Id, TransactionUsageEntitlement>(
            [SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :accountId]).keySet();
        deleteUsageEntitlementBucketsBottomUp(ueaIds, false, ownTueIds);
        requireWalkQueries(RETRY_TAIL);
        deleteQuietly([SELECT Id FROM UsageEntitlementAccount WHERE Id IN :ueaIds]);
    }

    /**
     * Deletes TransactionJournal records for a given account.
     * These records represent financial transactions and can be related to:
     * - Account
     * - Orders
     * - Invoices
     *
     * @param accountId The ID of the account whose records should be deleted
     */
    private static void deleteTransactionJournal(Id accountId) {
        requireWalkQueries(RETRY_TAIL);
        deleteQuietly([SELECT Id FROM TransactionJournal WHERE AccountId = :accountId]);
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
     * When the rounds or the query budget run out while rows are still going, it
     * stops the run: the rows removed so far stay removed, and the next run
     * continues.
     *
     * @param accountId The account whose usage summary graph should be removed
     */
    private static void deleteUsageSummaryGraph(Id accountId) {
        Set<Id> assetIds = accountAssetIds;

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
        Boolean queryBudgetSpent = false;
        Integer maxRounds = maxTeardownRoundsForTest != null ? maxTeardownRoundsForTest : MAX_TEARDOWN_ROUNDS;
        for (Integer round = 1; round <= maxRounds; round++) {
            if (Limits.getLimitQueries() - Limits.getQueries() < QUERIES_PER_ROUND + QUERY_RESERVE) {
                queryBudgetSpent = true;
                break;
            }
            roundFound = 0;
            Integer progress = 0;

            progress += drain([
                SELECT Id FROM UsageEntitlementEntry
                WHERE TransactionUsageEntitlement.Account.Id = :accountId LIMIT :TEARDOWN_BATCH]);
            progress += drain([
                SELECT Id FROM UsageBillingPeriodItem
                WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :TEARDOWN_BATCH]);
            progress += drain([
                SELECT Id FROM UsageSummary
                WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :TEARDOWN_BATCH]);
            progress += drain([
                SELECT Id FROM UsageRatableSummary
                WHERE AccountId = :accountId OR AssetId IN :assetIds LIMIT :TEARDOWN_BATCH]);
            progress += drain([
                SELECT Id FROM TransactionJournal
                WHERE AccountId = :accountId LIMIT :TEARDOWN_BATCH]);
            progress += drain([
                SELECT Id FROM UsageEntitlementBucket
                WHERE TransactionUsageEntitlement.Account.Id = :accountId LIMIT :TEARDOWN_BATCH]);
            progress += drain([
                SELECT Id FROM TransactionUsageEntitlement
                WHERE AccountId = :accountId LIMIT :TEARDOWN_BATCH]);
            progress += drain([
                SELECT Id FROM UsageEntitlementAccount
                WHERE AccountId = :accountId LIMIT :TEARDOWN_BATCH]);
            // The commitment junction. Linking a commitment to its anchor is a
            // post-262 selling step this utility predates, and an anchor asset
            // cannot be deleted while its junction row survives.
            if (!assetIds.isEmpty()) {
                progress += drain([
                    SELECT Id FROM UsageCmtAssetRelatedObj
                    WHERE AssetId IN :assetIds OR RelatedObjectId IN :assetIds
                    LIMIT :TEARDOWN_BATCH]);
            }

            if (progress == 0) {
                usageDrained = roundFound == 0;
                return;
            }
        }
        // Still removing rows when the rounds or the query budget ran out. Not a
        // failure: the rows deleted so far are real progress, and phase 1 keeps them.
        throw new ResetStoppedException(queryBudgetSpent ? QUERY_LIMIT : USAGE_TOO_LARGE);
    }

    private static Integer drain(List<SObject> rows) {
        roundFound += rows.size();
        return deleteQuietly(rows);
    }

    /**
     * Deletes AssetRateCardEntry records for an account's assets.
     *
     * These were never removed, and they block deletion of the design-time
     * RateCardEntry rows they reference -- which is why reloading qb-rates
     * against an org with live assets inserts a second, Draft copy of every
     * entry instead of replacing the Active ones.
     */
    private static void deleteAssetRateCardEntries() {
        if (accountAssetIds.isEmpty()) {
            return;
        }
        deleteQuietly([SELECT Id FROM AssetRateCardEntry WHERE AssetId IN :accountAssetIds]);
    }

    /**
     * Deletes BillingScheduleGroup records for a given account.
     * These records represent billing schedule groups and can be related to:
     * - Account
     * - BillingSchedules
     *
     * Runs before the orders are deleted: the billing schedules, which go with
     * their group, reference them.
     *
     * @param accountId The ID of the account whose records should be deleted
     */
    private static void deleteBillingScheduleGroups(Id accountId) {
        // Skipped for a user who cannot read them: the preflight refused the run if any existed.
        if (!canRead('BillingScheduleGroup')) {
            return;
        }
        deleteQuietly([SELECT Id FROM BillingScheduleGroup WHERE BillingAccountId = :accountId]);
    }

    /**
     * Deletes Contract records for a given account.
     * These records represent contracts and can be related to:
     * - Account
     * - Orders
     * - Assets
     *
     * When preserveContractsWithPrices is true, contracts that have at least one
     * ContractItemPrice (contracted price) child are kept. Because
     * ContractItemPrice.ContractId is a master-detail relationship, a surviving
     * Contract retains its contracted prices automatically — no explicit child
     * handling is required. The rate card entries bound to a contract go with
     * it, so a kept contract keeps those as well.
     *
     * @param accountId The ID of the account whose records should be deleted
     * @param preserveContractsWithPrices When true, skip contracts that have
     *        ContractItemPrice children; when false, delete all contracts
     */
    private static void deleteContracts(Id accountId, Boolean preserveContractsWithPrices) {
        List<Contract> contracts;
        if (preserveContractsWithPrices && Schema.getGlobalDescribe().containsKey('ContractItemPrice')) {
            // Select only contracts with NO ContractItemPrice children via a
            // semi-join on the master-detail FK. Dynamic SOQL keeps this class
            // deployable on editions where Contract Pricing is unavailable.
            contracts = (List<Contract>) Database.query(
                'SELECT Id FROM Contract WHERE AccountId = :accountId ' +
                'AND Id NOT IN (SELECT ContractId FROM ContractItemPrice)');
        } else {
            // Without preserve, or without Contract Pricing (where no contract can
            // have a ContractItemPrice child, so none is priced): every contract.
            contracts = [SELECT Id FROM Contract WHERE AccountId = :accountId];
        }
        if (contracts.isEmpty()) {
            return;
        }
        // BindingObjectId is polymorphic, and a semi-join against it silently
        // matches nothing (see deleteUsageResourcePolicies), so bind the ids.
        Set<Id> contractIds = new Map<Id, Contract>(contracts).keySet();
        deleteQuietly([SELECT Id FROM BindingObjectRateCardEntry WHERE BindingObjectId IN :contractIds]);
        deleteAll(contracts);
    }

    /**
     * Deletes ALL records that directly reference assets for the account.
     * This is a comprehensive cleanup method that ensures no records are left
     * that would prevent asset deletion.
     *
     * @param accountId The ID of the account whose asset-referencing records should be deleted
     */
    private static void deleteAllRecordsReferencingAssets(Id accountId) {
        Set<Id> assetIds = accountAssetIds;
        if (assetIds.isEmpty()) {
            return;
        }

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

        Set<Id> allTueIds = new Set<Id>();
        Set<Id> allUeaIds = new Set<Id>();
        if (!usageDrained) {
            // --- 1-3. Summaries the teardown loop could not delete; they block buckets ---
            requireWalkQueries(ASSET_TAIL);
            deleteQuietly([SELECT Id FROM UsageSummary WHERE AccountId = :accountId OR AssetId IN :assetIds]);
            requireWalkQueries(ASSET_TAIL);
            deleteQuietly([SELECT Id FROM UsageRatableSummary WHERE AssetId IN :assetIds]);
            requireWalkQueries(ASSET_TAIL);
            deleteQuietly([SELECT Id FROM UsageBillingPeriodItem WHERE AccountId = :accountId OR AssetId IN :assetIds]);
            requireWalkQueries(ASSET_TAIL);
            allTueIds.addAll(new Map<Id, TransactionUsageEntitlement>(
                [SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :accountId]).keySet());
            requireWalkQueries(ASSET_TAIL);
            allUeaIds.addAll(new Map<Id, UsageEntitlementAccount>(
                [SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :accountId]).keySet());
        }
        // TUEs bound to the assets themselves; the teardown loop only follows the account.
        requireWalkQueries(ASSET_TAIL);
        allTueIds.addAll(new Map<Id, TransactionUsageEntitlement>([
            SELECT Id FROM TransactionUsageEntitlement
            WHERE AssetId IN :assetIds OR GrantBindingTargetId IN :assetIds
        ]).keySet());

        // --- 4. Delete UsageEntitlementBuckets (UEB) — blocks TUE and UEA ---
        Set<Id> bucketSearchIds = new Set<Id>(allTueIds);
        bucketSearchIds.addAll(allUeaIds);
        Set<Id> allBucketIds = new Set<Id>();
        if (!bucketSearchIds.isEmpty()) {
            // The tree under those entitlements, level by level. A bucket holding an
            // entitlement outside allTueIds (another account's), and the buckets above
            // it, stay.
            Map<Id, UsageEntitlementBucket> tree = loadBucketTree(bucketSearchIds, allTueIds, ASSET_TAIL);
            keepForeignBuckets(tree, allTueIds);
            allBucketIds.addAll(tree.keySet());
        }

        // Multi-pass bucket deletion (handles nested parent-child hierarchy)
        Integer before = allBucketIds.size();
        while (!allBucketIds.isEmpty()) {
            requireWalkQueries(ASSET_TAIL);
            List<UsageEntitlementBucket> toDelete = [SELECT Id FROM UsageEntitlementBucket WHERE Id IN :allBucketIds];
            if (toDelete.isEmpty()) {
                break;
            }
            allBucketIds.removeAll(deleteRows(toDelete, false));
            // Break if no progress was made to avoid infinite loop
            if (allBucketIds.size() == before) {
                break;
            }
            before = allBucketIds.size();
        }

        // --- 5. Delete TUEs ---
        if (!allTueIds.isEmpty()) {
            requireWalkQueries(ASSET_TAIL);
            deleteQuietly([SELECT Id FROM TransactionUsageEntitlement WHERE Id IN :allTueIds]);
        }

        // --- 6. Delete UEAs ---
        if (!allUeaIds.isEmpty()) {
            requireWalkQueries(ASSET_TAIL);
            deleteQuietly([SELECT Id FROM UsageEntitlementAccount WHERE Id IN :allUeaIds]);
        }

        // --- 7. Delete other asset references (WorkOrder, Case) ---
        deleteOtherAssetReferences(assetIds);
    }

    /**
     * Deletes the work orders and cases that reference the assets. Both are queried
     * dynamically, so the class still deploys to an org without them, and an object
     * without AssetId is skipped. Only the query can tell: live 264, Case.AssetId was
     * missing from the org, yet this class's describe still listed it. ServiceContract
     * has no AssetId -- asset coverage lives on ContractLineItem -- so it is not queried.
     */
    private static void deleteOtherAssetReferences(Set<Id> assetIds) {
        for (String objectName : new List<String>{ 'WorkOrder', 'Case' }) {
            // Skipped for a user who cannot read it: the preflight refused the run if any
            // referenced the assets.
            if (!canRead(objectName)) {
                continue;
            }
            requireQueries(1);
            List<SObject> referencing;
            try {
                referencing = Database.query('SELECT Id FROM ' + objectName + ' WHERE AssetId IN :assetIds');
            } catch (QueryException e) {
                if (!e.getMessage().contains('No such column')) {
                    throw e;
                }
                continue;
            }
            deleteQuietly(referencing);
        }
    }

    /**
     * Deletes the account's assets and their relationships.
     */
    private static void deleteAssets() {
        if (accountAssetIds.isEmpty()) {
            return;
        }
        deleteAll([
            SELECT Id FROM AssetRelationship WHERE AssetId IN :accountAssetIds OR RelatedAssetId IN :accountAssetIds
        ]);
        deleteAll([SELECT Id FROM Asset WHERE Id IN :accountAssetIds]);
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
     * @param orderData The OrderData object containing pre-queried information
     */
    private static void deleteFulfillmentLineSourceRel(OrderData orderData) {
        deleteQuietly(orderData.fulfillmentLineSourceRels);
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
     * @param orderData The OrderData object containing pre-queried information
     */
    private static void deleteFulfillmentStepSource(OrderData orderData) {
        // Skipped for a user who cannot read them: their plans, which the preflight checks,
        // would have refused the run.
        if (!canRead('FulfillmentStepSource')) {
            return;
        }
        deleteQuietly([
            SELECT Id
            FROM FulfillmentStepSource
            WHERE StepId IN :orderData.fulfillmentStepIds
            OR SourceLineItemId IN :orderData.orderItemIds
        ]);
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
     * @param orderData The OrderData object containing pre-queried information
     */
    private static void deleteFulfillmentOrderLineItem(OrderData orderData) {
        deleteQuietly(orderData.fulfillmentOrderLineItems);
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
     * @param orderData The OrderData object containing pre-queried information
     */
    private static void deleteFulfillmentOrder(OrderData orderData) {
        deleteQuietly(orderData.fulfillmentOrders);
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
     * @param orderData The OrderData object containing pre-queried information
     */
    private static void deleteFulfillmentPlan(OrderData orderData) {
        deleteQuietly(orderData.fulfillmentPlans);
    }

    /**
     * Deletes FulfillmentAsset records for a given account.
     * These records represent fulfillment assets and are directly related to:
     * - Account
     *
     * This method must be called after deleting FulfillmentOrderLineItems
     * to maintain referential integrity.
     *
     * @param orderData The OrderData object containing pre-queried information
     */
    private static void deleteFulfillmentAsset(OrderData orderData) {
        deleteQuietly(orderData.fulfillmentAssets);
    }

    /**
     * Deletes AssetFulfillmentDecomp records for a given account.
     * These records represent asset fulfillment decompositions and can be related to:
     * - FulfillmentAssets (as source or target)
     *
     * This method must be called before deleting FulfillmentAssets
     * to maintain referential integrity.
     *
     * @param orderData The OrderData object containing pre-queried information
     */
    private static void deleteAssetFulfillmentDecomp(OrderData orderData) {
        // Skipped for a user who cannot read them: the preflight refused the run if any existed.
        if (!canRead('AssetFulfillmentDecomp')) {
            return;
        }
        deleteQuietly([
            SELECT Id
            FROM AssetFulfillmentDecomp
            WHERE FulfillmentSourceAssetId IN :orderData.fulfillmentAssetIds
            OR FulfillmentTargetAssetId IN :orderData.fulfillmentAssetIds
        ]);
    }

    /**
     * Deletes BindingObjUsageRsrcPlcy records whose polymorphic BindingObjectId
     * is tied to the given Account via any of these targets:
     *  - the Account itself
     *  - an Asset with Asset.AccountId = accountId
     *  - a Contract with Contract.AccountId = accountId
     */
    private static void deleteUsageResourcePolicies(Id accountId) {
        // Collect unique policies across multiple constraint-compliant queries.
        Map<Id, BindingObjUsageRsrcPlcy> policies = new Map<Id, BindingObjUsageRsrcPlcy>(
            [SELECT Id FROM BindingObjUsageRsrcPlcy WHERE BindingObjectId = :accountId]);

        // BindingObjectId is POLYMORPHIC (Account / Asset / BindingObjectCustomExt /
        // Contract). A semi-join against a polymorphic lookup does not resolve --
        // it silently matches nothing, which is why asset deletion kept failing with
        // "associated with the following binding object usage resource policies"
        // even though this method reported success. Bind the materialised ids.
        if (!accountAssetIds.isEmpty()) {
            policies.putAll([SELECT Id FROM BindingObjUsageRsrcPlcy WHERE BindingObjectId IN :accountAssetIds]);
        }
        if (!accountContractIds.isEmpty()) {
            policies.putAll([SELECT Id FROM BindingObjUsageRsrcPlcy WHERE BindingObjectId IN :accountContractIds]);
        }
        deleteQuietly(policies.values());
    }

    /**
     * Deletes the BindingObjectRateCardEntry records bound to the Account itself.
     * Those bound to a contract are deleted with the contract (deleteContracts),
     * so contracts the reset keeps keep their rate card entries.
     */
    private static void deleteBindingObjRateCardEntries(Id accountId) {
        deleteQuietly([SELECT Id FROM BindingObjectRateCardEntry WHERE BindingObjectId = :accountId]);
    }

    /** Ends a preflight that would leave too few queries for the run it checks. */
    private class PreflightTooLargeException extends Exception {}

    /** The records of one object that block the reset for one reason. */
    private class Blocker {
        public String label;
        public String reason;
        public Integer count = 0;
        // Names of the visible records; none for hidden or unreadable ones.
        public List<String> names = new List<String>();
    }

    /**
     * The read-only check that runs before phase 1 (see the class header). It reads, in
     * system mode, the records each step would delete or change for the selected options,
     * with the steps' own filters, and records a Blocker for each that the running user
     * could not delete:
     *  - an object the user cannot read (CANNOT_READ, a count);
     *  - an object the user has no delete permission on (NO_PERMISSION, names);
     *  - a record the user cannot see (NOT_VISIBLE, a count) or cannot delete (NO_ACCESS,
     *    names), from UserRecordAccess, 200 ids a query;
     *  - an activated order without Edit Activated Orders, a lifecycle-managed asset
     *    without Access Lifecycle-Managed Assets, a posted invoice without Delete Invoice
     *    and Invoice Lines, and an invoice still processing.
     * Records reached only through one of these and deleted with it (order lines, plan and
     * fulfillment order items, step sources, files) are covered by their parent. A user
     * with Modify All Data and View All Data may read and delete every record, so for them
     * only the objects they cannot read or delete, and the permission checks, are read.
     *
     * Each query first requires the queries the run itself needs after it (one teardown
     * round and phase 2's reserve); without them the preflight stops with
     * PreflightTooLargeException and nothing is changed. Phase 1 reuses the rows read here
     * for assets, contracts, binding policies and rate card entries.
     */
    // `without sharing`, declared on the inner class itself: an inner class does not take
    // the outer class's keyword, and AccessLevel.SYSTEM_MODE leaves record sharing to the
    // class's keyword. Live 264 (runAs a Standard User), a SYSTEM_MODE query in a class
    // without a keyword returned none of the records the user could not see.
    @TestVisible
    private without sharing class Preflight {
        public List<Blocker> blockers = new List<Blocker>();
        // False only when the usage objects were read and held no record for the account.
        public Boolean hasUsage = true;
        private Map<String, List<SObject>> rows = new Map<String, List<SObject>>();
        private Map<String, Blocker> blockerByKey = new Map<String, Blocker>();
        private Map<Id, String> objectOf = new Map<Id, String>();
        private Map<Id, String> nameOf = new Map<Id, String>();
        private Map<String, String> nameFields = new Map<String, String>();
        private Boolean privileged;
        private Map<String, Object> binds = new Map<String, Object>();

        public Preflight(
            Id accountId, Boolean deleteAssets, Boolean deleteFulfillment, Boolean deleteBilling,
            Boolean deleteCollections, Boolean preserveContractsWithPrices
        ) {
            privileged = hasUserPermission('PermissionsModifyAllData') && hasUserPermission('PermissionsViewAllData');
            binds.put('accountId', accountId);

            // Assets and contracts: read for everyone, since phase 1 reuses them.
            Boolean lifecycleField = deleteAssets && typeOf('Asset').getDescribe().fields.getMap()
                .containsKey('haslifecyclemanagement');
            List<SObject> assets = load('Asset', lifecycleField ? ', HasLifecycleManagement' : '',
                'AccountId = :accountId', true, deleteAssets);
            Set<Id> assetIds = ids(assets);
            binds.put('assetIds', assetIds);
            if (lifecycleField && !hasUserPermission('PermissionsCalmSobjectAccessUser')) {
                for (SObject asset : assets) {
                    if (asset.get('HasLifecycleManagement') == true) {
                        block('Asset', NEEDS_LIFECYCLE, asset);
                    }
                }
            }
            List<SObject> contracts = load('Contract', '', 'AccountId = :accountId', true, false);
            Set<Id> contractIds = ids(contracts);
            binds.put('contractIds', contractIds);
            List<SObject> deletedContracts = contracts;
            if (preserveContractsWithPrices && typeOf('ContractItemPrice') != null && !contracts.isEmpty()) {
                requireQuery();
                Set<Id> priced = new Set<Id>();
                for (SObject price : Database.queryWithBinds(
                    'SELECT ContractId FROM ContractItemPrice WHERE ContractId IN :contractIds', binds, AccessLevel.SYSTEM_MODE
                )) {
                    priced.add((Id) price.get('ContractId'));
                }
                deletedContracts = new List<SObject>();
                for (SObject contract : contracts) {
                    if (!priced.contains(contract.Id)) {
                        deletedContracts.add(contract);
                    }
                }
            }
            check('Contract', deletedContracts);
            binds.put('deletedContractIds', ids(deletedContracts));

            // Phase 1: binding policies and rate card entries (reused), then the usage graph.
            Set<Id> bindingIds = new Set<Id>(assetIds);
            bindingIds.addAll(contractIds);
            bindingIds.add(accountId);
            binds.put('bindingIds', bindingIds);
            load('BindingObjUsageRsrcPlcy', '', 'BindingObjectId IN :bindingIds', true, true);
            load('BindingObjectRateCardEntry', '',
                'BindingObjectId = :accountId OR BindingObjectId IN :deletedContractIds', true, true);
            Boolean usage = false;
            String byAccountOrAsset = 'AccountId = :accountId OR AssetId IN :assetIds';
            usage |= !load('UsageBillingPeriodItem', '', byAccountOrAsset, false, true).isEmpty();
            usage |= !load('UsageSummary', '', byAccountOrAsset, false, true).isEmpty();
            usage |= !load('UsageRatableSummary', '', byAccountOrAsset, false, true).isEmpty();
            usage |= !load('TransactionJournal', '', 'AccountId = :accountId', false, true).isEmpty();
            Set<Id> tueIds = ids(load('TransactionUsageEntitlement', '', 'AccountId = :accountId'
                + (deleteAssets ? ' OR AssetId IN :assetIds OR GrantBindingTargetId IN :assetIds' : ''), false, true));
            binds.put('tueIds', tueIds);
            Set<Id> ueaIds = ids(load('UsageEntitlementAccount', '', 'AccountId = :accountId', false, true));
            binds.put('ueaIds', ueaIds);
            usage |= !tueIds.isEmpty() || !ueaIds.isEmpty();
            if (!tueIds.isEmpty()) {
                usage |= !load('UsageEntitlementEntry', '', 'TransactionUsageEntitlementId IN :tueIds', false, true).isEmpty();
            }
            if (!tueIds.isEmpty() || !ueaIds.isEmpty()) {
                // The account's buckets: those holding its entitlements, and three levels
                // under its entitlement accounts. A bucket holding another account's
                // entitlement is never deleted, so it is left out.
                List<SObject> buckets = new List<SObject>();
                Set<Id> parents = new Set<Id>(ueaIds);
                String own = ' AND (TransactionUsageEntitlementId = null OR TransactionUsageEntitlementId IN :tueIds)';
                binds.put('bucketParents', parents);
                buckets.addAll(query('UsageEntitlementBucket',
                    '(TransactionUsageEntitlementId IN :tueIds OR ParentId IN :bucketParents)' + own));
                for (Integer level = 2; level <= 3 && !buckets.isEmpty(); level++) {
                    Set<Id> known = ids(buckets);
                    binds.put('bucketParents', known);
                    binds.put('knownBuckets', known);
                    List<SObject> children = query('UsageEntitlementBucket',
                        'ParentId IN :bucketParents AND Id NOT IN :knownBuckets' + own);
                    if (children.isEmpty()) {
                        break;
                    }
                    buckets.addAll(children);
                }
                rows.put('UsageEntitlementBucket', buckets);
                check('UsageEntitlementBucket', buckets);
                usage |= !buckets.isEmpty();
            }
            if (!assetIds.isEmpty()) {
                usage |= !load('UsageCmtAssetRelatedObj', '', 'AssetId IN :assetIds OR RelatedObjectId IN :assetIds',
                    false, true).isEmpty();
            }
            // A privileged user's usage objects are not read; the teardown then runs as before.
            hasUsage = privileged || usage;

            if (deleteAssets && !assetIds.isEmpty()) {
                load('AssetRateCardEntry', '', 'AssetId IN :assetIds', false, true);
                load('AssetRelationship', '', 'AssetId IN :assetIds OR RelatedAssetId IN :assetIds', false, true);
                load('WorkOrder', '', 'AssetId IN :assetIds', false, true);
            }
            load('BillingScheduleGroup', '', 'BillingAccountId = :accountId', false, true);

            List<SObject> orders = load('Order', ', Status', 'AccountId = :accountId',
                !hasUserPermission('PermissionsEditActivatedOrders'), true);
            if (!hasUserPermission('PermissionsEditActivatedOrders')) {
                for (SObject o : orders) {
                    if (o.get('Status') != 'Draft') {
                        block('Order', NEEDS_EDIT_ACTIVATED, o);
                    }
                }
            }
            binds.put('orderIds', ids(orders));

            List<SObject> invoices = new List<SObject>();
            if (deleteBilling || deleteCollections || deleteFulfillment) {
                // Read for everyone when billing is deleted: the status checks need them.
                invoices = load('Invoice', ', Status, PaymentScheduleId', 'BillingAccountId = :accountId',
                    deleteBilling, deleteBilling);
            }
            binds.put('invoiceIds', ids(invoices));
            Set<Id> scheduleIds = new Set<Id>();
            if (deleteBilling) {
                for (SObject inv : invoices) {
                    String status = inv.get('Status') == null ? '' : (String) inv.get('Status');
                    if (status.endsWith('In Progress') || status == 'Processing') {
                        block('Invoice', INVOICE_IN_PROGRESS, inv);
                    } else if (status != 'Draft' && status != 'Canceled' && !canDeletePostedInvoices()) {
                        block('Invoice', INVOICE_NEEDS_PERMISSION, inv);
                    }
                    if (inv.get('PaymentScheduleId') != null) {
                        scheduleIds.add((Id) inv.get('PaymentScheduleId'));
                    }
                }
                load('DebitMemo', '', 'AccountId = :accountId AND Status NOT IN (\'Posted\', \'Void\')', false, true);
                load('CreditMemo', '', 'BillingAccountId = :accountId AND Status IN (\'Draft\', \'Canceled\', \'Posted\')',
                    false, true);
            }
            binds.put('scheduleIds', scheduleIds);

            Set<Id> planIds = new Set<Id>();
            Set<Id> disputeCaseIds = new Set<Id>();
            Set<Id> planItemIds = new Set<Id>();
            if (deleteCollections) {
                planIds = ids(load('CollectionPlan', '', 'AccountId = :accountId', false, true));
                binds.put('planIds', planIds);
                if (!planIds.isEmpty()) {
                    planItemIds = ids(load('CollectionPlanItem', '', 'CollectionPlanId IN :planIds', false, false));
                }
                for (SObject dispute : load('Dispute', ', CaseId', 'AccountId = :accountId OR InvoiceId IN :invoiceIds',
                    false, true)) {
                    if (dispute.get('CaseId') != null) {
                        disputeCaseIds.add((Id) dispute.get('CaseId'));
                    }
                }
            }
            binds.put('planIds', planIds);
            binds.put('planItemIds', planItemIds);
            binds.put('disputeCaseIds', disputeCaseIds);
            if (!scheduleIds.isEmpty() || !planIds.isEmpty()) {
                load('PaymentSchedule', '', 'Id IN :scheduleIds OR ReferenceEntityId IN :planIds '
                    + 'OR CollectionPlanItemId IN :planItemIds', false, true);
            }
            List<String> caseFilters = new List<String>();
            if (deleteAssets && !assetIds.isEmpty()) {
                caseFilters.add('AssetId IN :assetIds');
            }
            if (!planIds.isEmpty() || !disputeCaseIds.isEmpty()) {
                caseFilters.add('(AccountId = :accountId AND (SourceId IN :planIds OR Id IN :disputeCaseIds))');
            }
            if (!caseFilters.isEmpty()) {
                load('Case', '', String.join(caseFilters, ' OR '), false, true);
            }

            if (deleteFulfillment) {
                Set<Id> orderItemIds = ids(load('OrderItem', '', 'OrderId IN :orderIds', false, false));
                binds.put('orderItemIds', orderItemIds);
                Set<String> sourceIds = new Set<String>();
                for (Id sourceId : orderItemIds) {
                    sourceIds.add(sourceId);
                }
                for (Id sourceId : ids(orders)) {
                    sourceIds.add(sourceId);
                }
                binds.put('sourceIds', sourceIds);
                binds.put('summaryIds', ids(load('OrderSummary', '', 'AccountId = :accountId', false, false)));
                load('FulfillmentOrder', '', 'AccountId = :accountId OR OrderId IN :orderIds OR InvoiceId IN :invoiceIds '
                    + 'OR OrderSummaryId IN :summaryIds', false, true);
                if (!sourceIds.isEmpty()) {
                    load('FulfillmentPlan', '', 'SourceIdentifier IN :sourceIds '
                        + 'AND (SourceType = \'StandardOrder\' OR SourceType = \'OrderItem\')', false, true);
                }
                Set<Id> fulfillmentAssetIds = ids(load('FulfillmentAsset', '', 'AccountId = :accountId', false, true));
                binds.put('fulfillmentAssetIds', fulfillmentAssetIds);
                if (!fulfillmentAssetIds.isEmpty()) {
                    load('AssetFulfillmentDecomp', '', 'FulfillmentSourceAssetId IN :fulfillmentAssetIds '
                        + 'OR FulfillmentTargetAssetId IN :fulfillmentAssetIds', false, true);
                }
                if (!orderItemIds.isEmpty()) {
                    load('FulfillmentLineSourceRel', '', 'SourceLineItemId IN :orderItemIds', false, true);
                }
            }

            Set<Id> quoteIds = ids(load('Quote', '', 'QuoteAccountId = :accountId OR AccountId = :accountId', false, true));
            load('Opportunity', '', 'AccountId = :accountId', false, true);
            Set<String> documentRefs = new Set<String>();
            for (Id recordId : quoteIds) {
                documentRefs.add(recordId);
            }
            if (deleteBilling) {
                for (SObject inv : invoices) {
                    documentRefs.add(inv.Id);
                }
            }
            binds.put('documentRefs', documentRefs);
            if (!documentRefs.isEmpty()) {
                load('DocumentGenerationProcess', '', 'ReferenceObject IN :documentRefs', false, true);
            }

            readRecordAccess();
        }

        /**
         * Reads `objectName`'s records matching `filter`, in system mode, and, when
         * `checked`, records what blocks them. A privileged user's rows are read only when
         * `reused`, or when the object is one they cannot read or delete; otherwise an empty
         * list stands for them.
         */
        private List<SObject> load(String objectName, String extraFields, String filter, Boolean reused, Boolean checked) {
            List<SObject> found = new List<SObject>();
            rows.put(objectName, found);
            if (typeOf(objectName) == null) {
                return found;
            }
            if (privileged && !reused && canRead(objectName) && objectDeletable(objectName)) {
                return found;
            }
            requireQuery();
            String nameField = nameFieldOf(objectName);
            String fields = 'Id' + (nameField == null ? '' : ', ' + nameField) + extraFields;
            found = Database.queryWithBinds(
                'SELECT ' + fields + ' FROM ' + objectName + ' WHERE ' + filter, binds, AccessLevel.SYSTEM_MODE);
            rows.put(objectName, found);
            if (checked) {
                check(objectName, found);
            }
            return found;
        }

        /** One system-mode read of `objectName`, with its name field; nothing recorded. */
        private List<SObject> query(String objectName, String filter) {
            requireQuery();
            String nameField = nameFieldOf(objectName);
            return Database.queryWithBinds('SELECT Id' + (nameField == null ? '' : ', ' + nameField) + ' FROM '
                + objectName + ' WHERE ' + filter, binds, AccessLevel.SYSTEM_MODE);
        }

        /** Records what blocks `found`, the records of `objectName` the run would delete. */
        private void check(String objectName, List<SObject> found) {
            if (found.isEmpty()) {
                return;
            }
            if (!canRead(objectName)) {
                Blocker b = blocker(objectName, CANNOT_READ);
                b.count += found.size();
                return;
            }
            if (!objectDeletable(objectName)) {
                for (SObject record : found) {
                    block(objectName, NO_PERMISSION, record);
                }
                return;
            }
            if (privileged) {
                return;
            }
            for (SObject record : found) {
                objectOf.put(record.Id, objectName);
                nameOf.put(record.Id, nameOf(objectName, record));
            }
        }

        /** UserRecordAccess for every record check() kept, 200 ids a query. */
        private void readRecordAccess() {
            List<Id> recordIds = new List<Id>(objectOf.keySet());
            Id userId = UserInfo.getUserId();
            for (Integer start = 0; start < recordIds.size(); start += 200) {
                requireQuery();
                List<Id> chunk = new List<Id>();
                for (Integer i = start; i < Math.min(start + 200, recordIds.size()); i++) {
                    chunk.add(recordIds[i]);
                }
                for (UserRecordAccess access : [
                    SELECT RecordId, HasReadAccess, HasDeleteAccess FROM UserRecordAccess
                    WHERE UserId = :userId AND RecordId IN :chunk
                ]) {
                    String objectName = objectOf.get(access.RecordId);
                    if (!access.HasReadAccess) {
                        blocker(objectName, NOT_VISIBLE).count++;
                    } else if (!access.HasDeleteAccess) {
                        Blocker b = blocker(objectName, NO_ACCESS);
                        b.count++;
                        b.names.add(nameOf.get(access.RecordId));
                    }
                }
            }
        }

        private void requireQuery() {
            if (Limits.getLimitQueries() - Limits.getQueries() < 1 + QUERIES_PER_ROUND + QUERY_RESERVE) {
                throw new PreflightTooLargeException(PREFLIGHT_TOO_LARGE);
            }
        }

        private void block(String objectName, String reason, SObject record) {
            // A record of an object the user cannot read is counted under CANNOT_READ only:
            // it is never named.
            if (!canRead(objectName)) {
                return;
            }
            Blocker b = blocker(objectName, reason);
            b.count++;
            b.names.add(nameOf(objectName, record));
        }

        private Blocker blocker(String objectName, String reason) {
            String key = objectName + '|' + reason;
            if (!blockerByKey.containsKey(key)) {
                Blocker b = new Blocker();
                b.label = labelOf(typeOf(objectName));
                b.reason = reason;
                blockerByKey.put(key, b);
                blockers.add(b);
            }
            return blockerByKey.get(key);
        }

        /** The rows read for `objectName`, or an empty list. */
        public List<SObject> rowsOf(String objectName) {
            return rows.containsKey(objectName) ? rows.get(objectName) : new List<SObject>();
        }

        /** "Orders: 1 (no delete access to these records: 00000123); Opportunities: 1 (not visible ...)" */
        public String describeBlockers() {
            List<String> parts = new List<String>();
            for (Blocker b : blockers) {
                String detail = b.reason;
                if (!b.names.isEmpty()) {
                    List<String> listed = new List<String>();
                    for (Integer i = 0; i < Math.min(NAMES_LISTED, b.names.size()); i++) {
                        listed.add(b.names[i]);
                    }
                    detail += ': ' + String.join(listed, ', ');
                    if (b.names.size() > NAMES_LISTED) {
                        detail += ' and ' + (b.names.size() - NAMES_LISTED) + ' more';
                    }
                }
                parts.add(b.label + ': ' + b.count + ' (' + detail + ')');
            }
            return String.join(parts, '; ');
        }

        private String nameFieldOf(String objectName) {
            if (!nameFields.containsKey(objectName)) {
                String found;
                for (Schema.SObjectField field : typeOf(objectName).getDescribe().fields.getMap().values()) {
                    Schema.DescribeFieldResult describe = field.getDescribe();
                    if (describe.isNameField()) {
                        found = describe.getName();
                        break;
                    }
                }
                nameFields.put(objectName, found == 'Id' ? null : found);
            }
            return nameFields.get(objectName);
        }

        private String nameOf(String objectName, SObject record) {
            String nameField = nameFieldOf(objectName);
            Object value = nameField == null ? null : record.get(nameField);
            return value == null ? String.valueOf(record.Id) : String.valueOf(value);
        }

        private Set<Id> ids(List<SObject> records) {
            return new Map<Id, SObject>(records).keySet();
        }
    }
}
