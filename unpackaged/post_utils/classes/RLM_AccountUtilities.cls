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
 * Object access: running without sharing does not reach an object the running
 * user cannot read. A query on Invoice by the sales rep persona, who has no billing
 * access, fails with "sObject type 'Invoice' is not supported" even here (live
 * 264), and so did one on every other object that user cannot read. So the
 * billing, collections, fulfillment and asset-reference steps read an object only
 * when the user can (canRead), and the Result lists each object a step skipped for
 * that reason as not checked. A user without billing access can therefore reset an
 * account; its billing records stay, and the Result says they were not checked.
 * The usage teardown and the order, contract, asset, quote and opportunity deletes
 * are not gated: the reset needs them, and a user who cannot read them gets the
 * platform's error as the reason.
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
 * Live 264 (todo 397), as the salesrep persona, that is not the whole story: the
 * platform still refused to delete an admin-owned order the persona could edit but
 * not delete ("insufficient access rights on object id"), and an admin-owned renewal
 * opportunity under Private sharing was not found at all. So orders, contracts, credit
 * memos, assets, quotes and opportunities are checked against the user's delete access
 * before anything changes or deletes them (keepWhatUserCannotDelete), and a record the
 * user cannot delete is kept and reported, the record itself unchanged. Records that
 * depend on it may still go: a kept order's fulfillment records and billing schedule
 * groups, and the usage records and binding policies of a kept asset or contract, are
 * found through the account, not through the kept record. A record the user cannot see is counted in system mode after a completed run
 * and reported as kept (reportHiddenRecords); only the count is read.
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
    // (phase 1's lookups before the loop take 4 to 6 of the 100 queries, and a round
    // needs 59 left to start), and the next run carries on.
    //
    // TEARDOWN_BATCH is a per-QUERY ceiling only -- it does NOT bound the
    // transaction. The 10,000-row DML limit is per transaction and this loop
    // issues nine deletes per round, so the real guard is the remaining-budget
    // clamp inside deleteRows(), which stops the run with a Result instead of
    // a LimitException.
    private static final Integer MAX_TEARDOWN_ROUNDS = 6;
    private static final Integer TEARDOWN_BATCH = 2000;

    // The queries one teardown round issues, and what is kept back for phase 2. Phase 2's
    // fixed queries total at most 48 (counted from the code, with every option on and
    // data in every branch): 31 before the asset step (order data 10, collections 5,
    // schedule groups 1, billing 9, fulfillment 2, contracts 3, orders 1; the delete
    // access reads are one per 200 records, and a read after the first is guarded), the
    // asset step's lookup of entitlements bound to the assets 1 and its other lookups 9,
    // quotes and opportunities 6 = 47 on the drained path, plus the journal query, which
    // only the undrained path runs = 48. 29 is what an account with no such data measures.
    // QUERY_RESERVE covers the 48 and the usage retries. A round starts only while both
    // are left; otherwise a large usage graph would spend phase 2's queries and end in a
    // LimitException. A test holds the measured 29 and the reserve against the 48.
    private static final Integer QUERIES_PER_ROUND = 9;
    @TestVisible
    private static final Integer QUERY_RESERVE = 50;
    @TestVisible
    private static final Integer PHASE_TWO_FIXED_MAX = 48;
    // The bucket walks (usage retries, the asset step's usage block) issue a number of
    // queries that grows with the tree. Each walk query first requires the queries that
    // can follow it before the next guard or the end of phase 2, counted from the code:
    //  - RETRY_TAIL, for the usage retries: at most 31 follow the journal guard (journal 1,
    //    collections 5, schedule groups 1, billing 9, fulfillment 2, contracts 3, orders 1,
    //    the asset step with no assets 3, quotes and opportunities 6). 34 keeps three spare.
    //  - ASSET_TAIL, for the asset step: at most 15 follow its last guard (other asset
    //    references 2, resource policies 3, rate card entries 1, assets 3, quotes and
    //    opportunities 6). 18 keeps three spare.
    // No walk can end in a LimitException. Sizing the guards by position stops a run with a
    // "run again" reason a little less often than one flat figure would; either way a stopped
    // run converges, because phase 1's progress persists. These figures must grow with any
    // query added after a guard; the tests cannot catch growth in the data-dependent branches.
    @TestVisible
    private static final Integer RETRY_TAIL = 34;
    @TestVisible
    private static final Integer ASSET_TAIL = 18;
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
    private static final String INVOICE_NEEDS_PERMISSION = 'not Draft or Canceled, and deleting them needs the '
        + 'Delete Invoice and Invoice Lines permission (permission set RLM_DeleteInvoices)';
    private static final String MEMO_NEEDS_PERMISSION = 'deleting them needs the Allow Revenue Records Deletion '
        + 'permission (Billing Admin permission set)';
    private static final String INVOICE_IN_PROGRESS = 'still processing; run the reset again once they finish';
    private static final String PAYMENTS_KEPT = 'payments are not deleted: Salesforce does not allow deleting processed payments';
    private static final String MEMO_ON_KEPT_INVOICE = 'applied to an invoice that was kept';
    private static final String DEBIT_MEMOS_KEPT = 'posted or void; Salesforce does not allow deleting them, or canceling a posted one';
    private static final String NO_DELETE_ACCESS = 'the user running the reset cannot delete them: they belong '
        + 'to another user and sharing does not let this user delete them; they were left unchanged';
    private static final String NO_DELETE_PERMISSION = 'the user running the reset does not have permission to '
        + 'delete this kind of record; they were left unchanged';
    private static final String ACCESS_CHECK_TOO_LARGE = 'The account has too many records for one run to check '
        + 'which of them the user running the reset may delete, and another run would stop at the same point. '
        + 'A user with Modify All Data skips that check.';
    private static final String NOT_VISIBLE = 'not visible to the user running the reset; they were left unchanged';
    private static final String INCOMPLETE_HIDDEN = 'Records not visible to the user running the reset may remain: '
        + 'the query limit was reached while counting them';
    private static final String SKIPPED_WITH = 'not checked: the step that deletes them also needs records the user '
        + 'running the reset has no access to';
    private static final String NOT_CHECKED = 'not checked: the user running the reset has no access to them';

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

        @InvocableVariable(label='Retained' description='Records the reset kept, by object, with the reason.')
        public String retainedSummary;
    }

    /** Ends a run early when a limit is close, before the platform throws a LimitException. */
    private class ResetStoppedException extends Exception {}

    /**
     * Ends a run that has more records than one run can check the user's delete access
     * on. Not a ResetStoppedException: another run would stop at the same point.
     */
    private class AccessCheckTooLargeException extends Exception {}

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
        // Labels of the objects a step skipped because the running user cannot read
        // them, in the order the steps met them.
        public List<String> unchecked = new List<String>();
        // Labels of readable objects a step skipped with ones the user cannot read.
        public List<String> skippedWith = new List<String>();
        // True when the count of records hidden from the user stopped before it finished.
        public Boolean incompleteHidden = false;

        public ResetReport copy() {
            ResetReport c = new ResetReport();
            c.removedLabels = removedLabels.clone();
            c.removed = removed.clone();
            c.kept = kept.clone();
            c.refused = refused.clone();
            c.foreignBuckets = foreignBuckets.clone();
            c.incompleteBuckets = incompleteBuckets;
            c.unchecked = unchecked.clone();
            c.incompleteHidden = incompleteHidden;
            c.skippedWith = skippedWith.clone();
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
    // always ends the loop first (a round needs 59 queries left, and 100 allow four or five, depending on the
    // 4 to 6 queries phase 1 spends on assets and contracts before the loop), so
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

    // Lets a test run as a user who cannot read these objects (canRead), since a test
    // user cannot be given the usage and core object access the reset also needs.
    @TestVisible
    private static Set<String> unreadableForTest = new Set<String>();

    // Lets a test set how many records of an object the running user cannot see
    // (hiddenCount), since a test cannot rely on the org's sharing settings.
    @TestVisible
    private static Map<String, Integer> hiddenForTest;

    // Lets a test decide which records the running user may delete (deletableByUser),
    // since a test cannot share a record to a user with edit but not delete access.
    @TestVisible
    private static Set<Id> deleteAccessForTest;

    /**
     * The account's orders, invoices and fulfillment records, queried once at the
     * start of phase 2 and shared by the steps that delete them. Invoices are
     * queried only for a step that uses them, and the fulfillment graph only when it
     * is going to be deleted; each only as far as the running user can read it.
     */
    private class OrderData {
        public List<Order> orders;
        public Set<Id> orderIds;
        public Set<Id> orderItemIds;
        // Status and PaymentScheduleId are for Delete Billing; the Ids also find the
        // fulfillment orders and disputes raised against an invoice. Empty when no
        // step asked for them or the running user cannot read invoices.
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
            // Not for a run that deletes neither billing, collections nor fulfillment, and
            // not for a user who cannot read invoices: that query fails, and with it the
            // whole reset. Delete Billing reports invoices it could not read; the other
            // two only look up by invoice, so they look up without them.
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
         * relations reference order items and line items. An object the running
         * user cannot read is skipped, and reported when the reset deletes it.
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
            if (readOrNote('FulfillmentOrder')) {
                // Order summaries only find fulfillment orders; they are not deleted.
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
            if (readOrNote('FulfillmentPlan')) {
                this.fulfillmentPlans = [
                    SELECT Id
                    FROM FulfillmentPlan
                    WHERE SourceIdentifier IN :sourceIdentifiers
                    AND (SourceType = 'StandardOrder' OR SourceType = 'OrderItem')
                ];
                // Steps only find step sources; they go with their plan.
                if (canRead('FulfillmentStep')) {
                    Set<Id> planIds = new Map<Id, FulfillmentPlan>(this.fulfillmentPlans).keySet();
                    this.fulfillmentStepIds = new Map<Id, FulfillmentStep>(
                        [SELECT Id FROM FulfillmentStep WHERE FulfillmentPlanId IN :planIds]).keySet();
                }
            }
            if (readOrNote('FulfillmentAsset')) {
                this.fulfillmentAssets = [SELECT Id FROM FulfillmentAsset WHERE AccountId = :accountId];
                this.fulfillmentAssetIds = new Map<Id, FulfillmentAsset>(this.fulfillmentAssets).keySet();
            }
            Set<Id> lineItemIds = new Set<Id>();
            if (readOrNote('FulfillmentOrderLineItem')) {
                this.fulfillmentOrderLineItems = [
                    SELECT Id FROM FulfillmentOrderLineItem WHERE FulfillmentOrderId IN :fulfillmentOrderIds
                ];
                lineItemIds = new Map<Id, FulfillmentOrderLineItem>(this.fulfillmentOrderLineItems).keySet();
            }
            if (readOrNote('FulfillmentLineSourceRel')) {
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
            accountAssetIds = new Map<Id, Asset>([SELECT Id FROM Asset WHERE AccountId = :accountId]).keySet();
            accountContractIds = new Map<Id, Contract>(
                [SELECT Id FROM Contract WHERE AccountId = :accountId]).keySet();

            deleteUsageResourcePolicies(accountId);
            deleteBindingObjRateCardEntries(accountId);

            // The summary graph must go FIRST. A UsageEntitlementEntry holds its
            // UsageSummary, and a bucket cannot be deleted while entitlement entries
            // still reference it -- so tearing down buckets before the summaries
            // (the previous order) fails on any account whose usage was ever rated.
            deleteUsageSummaryGraph(accountId);

            // Gated on deleteAssets, like the asset deletion itself further down.
            // AssetRateCardEntry rows are generated when the asset is created and are
            // NOT recreated for an existing asset, so removing them while KEEPING the
            // asset leaves a usage asset that can never rate again.
            if (deleteAssets) {
                deleteAssetRateCardEntries();
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
            List<Opportunity> accountOpportunities = [SELECT Id FROM Opportunity WHERE AccountId = :accountId];
            // Those the user cannot delete are kept, rather than failing the deletes below.
            Set<Id> allowed = deletableByUser(idsToCheck(new List<List<SObject>>{ accountQuotes, accountOpportunities }));
            accountQuotes = (List<Quote>) keepUndeletable(accountQuotes, allowed);
            accountOpportunities = (List<Opportunity>) keepUndeletable(accountOpportunities, allowed);
            // Delete quote-linked ContentDocuments before quotes are removed
            deleteQuoteDocuments(accountQuotes);
            deleteAll(accountQuotes);
            deleteAll(accountOpportunities);

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
        reportHiddenRecords(accountId, new Set<String>(hiddenCheckScope(
            deleteAssets, deleteFulfillment, deleteBilling, deleteCollections)), preserveContractsWithPrices);
        return finish(true, null);
    }

    @TestVisible
    private static void startRun() {
        report = new ResetReport();
        describedTypes = null;
        userPermissions = null;
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

    @TestVisible
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

        if (report.incompleteHidden) {
            kept.add(INCOMPLETE_HIDDEN);
        }
        if (report.incompleteBuckets) {
            kept.add(INCOMPLETE_BUCKETS);
        }
        if (!report.unchecked.isEmpty()) {
            kept.add(String.join(report.unchecked, ', ') + ': ' + NOT_CHECKED);
        }
        if (!report.skippedWith.isEmpty()) {
            kept.add(String.join(report.skippedWith, ', ') + ': ' + SKIPPED_WITH);
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
     * True when the org has the object and the running user can read it. A query on
     * an object the user cannot read fails even without sharing (see the class
     * header). Live 264, as the sales rep persona, isAccessible() was false for
     * exactly the objects whose queries failed and true for every one that worked.
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
     * canRead, and when the org has the object but the user cannot read it, records
     * it as not checked, so the Result says it was skipped. An object the org does
     * not have is skipped silently: there is nothing of it to delete.
     */
    private static Boolean readOrNote(String objectName) {
        if (canRead(objectName)) {
            return true;
        }
        Schema.SObjectType type = typeOf(objectName);
        if (type != null && !report.unchecked.contains(labelOf(type))) {
            report.unchecked.add(labelOf(type));
        }
        return false;
    }

    /**
     * The account-scoped objects whose records the reset deletes with these options. A
     * record reached only through one of these (lines, steps, buckets, entries, files,
     * generated documents, cases, work orders) is not counted on its own: a child of a
     * hidden parent stays with it, and the parent's count covers it.
     */
    private static List<String> hiddenCheckScope(
        Boolean deleteAssets, Boolean deleteFulfillment, Boolean deleteBilling, Boolean deleteCollections
    ) {
        List<String> scope = new List<String>{
            'TransactionUsageEntitlement', 'UsageEntitlementAccount', 'UsageSummary', 'UsageRatableSummary',
            'UsageBillingPeriodItem', 'TransactionJournal', 'BindingObjUsageRsrcPlcy', 'BindingObjectRateCardEntry',
            'BillingScheduleGroup', 'Contract', 'Order', 'Quote', 'Opportunity'
        };
        if (deleteAssets) {
            scope.add('Asset');
        }
        if (deleteFulfillment) {
            scope.addAll(new List<String>{ 'FulfillmentOrder', 'FulfillmentAsset' });
        }
        if (deleteBilling) {
            scope.addAll(new List<String>{ 'Invoice', 'CreditMemo', 'DebitMemo', 'Payment' });
        }
        if (deleteCollections) {
            scope.addAll(new List<String>{ 'CollectionPlan', 'Dispute' });
        }
        return scope;
    }

    // How each object in hiddenCheckScope finds the account's records, as the reset's
    // own queries do. Ordered as the reset meets them, so the Result lists them in order.
    private static final List<List<String>> ACCOUNT_FILTERS = new List<List<String>>{
        new List<String>{ 'TransactionUsageEntitlement', 'AccountId = :accountId' },
        new List<String>{ 'UsageEntitlementAccount', 'AccountId = :accountId' },
        new List<String>{ 'UsageSummary', 'AccountId = :accountId' },
        new List<String>{ 'UsageRatableSummary', 'AccountId = :accountId' },
        new List<String>{ 'UsageBillingPeriodItem', 'AccountId = :accountId' },
        new List<String>{ 'TransactionJournal', 'AccountId = :accountId' },
        new List<String>{ 'BindingObjUsageRsrcPlcy', 'BindingObjectId = :accountId' },
        new List<String>{ 'BindingObjectRateCardEntry', 'BindingObjectId = :accountId' },
        new List<String>{ 'CollectionPlan', 'AccountId = :accountId' },
        new List<String>{ 'Dispute', 'AccountId = :accountId' },
        new List<String>{ 'BillingScheduleGroup', 'BillingAccountId = :accountId' },
        new List<String>{ 'DebitMemo', 'AccountId = :accountId' },
        new List<String>{ 'Invoice', 'BillingAccountId = :accountId' },
        new List<String>{ 'CreditMemo', 'BillingAccountId = :accountId' },
        new List<String>{ 'Payment', 'AccountId = :accountId' },
        new List<String>{ 'FulfillmentOrder', 'AccountId = :accountId' },
        new List<String>{ 'FulfillmentAsset', 'AccountId = :accountId' },
        new List<String>{ 'Contract', 'AccountId = :accountId' },
        new List<String>{ 'Order', 'AccountId = :accountId' },
        new List<String>{ 'Asset', 'AccountId = :accountId' },
        new List<String>{ 'Quote', '(QuoteAccountId = :accountId OR AccountId = :accountId)' },
        new List<String>{ 'Opportunity', 'AccountId = :accountId' }
    };

    /**
     * After a completed run: counts, per object, the account's records still there that
     * the running user cannot see, and reports them as kept. Live 264 the salesrep
     * persona's reset did not find an admin-owned renewal opportunity under Private
     * sharing, even though this class runs without sharing, and said nothing about it;
     * a count WITH SYSTEM_MODE did find it. Only counts are read; no id reaches the user.
     *
     * Skipped for a user with View All Data, who sees every record. Otherwise it reads
     * the objects' sharing models once and counts only the objects whose records sharing
     * can hide (Private, or Controlled by Parent): two queries each, the system-mode count
     * and the count this class sees. An object the user cannot read is already reported
     * as not checked. This runs after phase 2, outside the counted phase-2 budget
     * (PHASE_TWO_FIXED_MAX), and spends only what is left: when too few queries remain it
     * stops, and the Result says the count is incomplete.
     */
    @TestVisible
    private static void reportHiddenRecords(Id accountId, Set<String> scope, Boolean preserveContractsWithPrices) {
        if (hiddenForTest == null && hasUserPermission('PermissionsViewAllData')) {
            return;
        }
        List<List<String>> readable = new List<List<String>>();
        List<String> readableNames = new List<String>();
        for (List<String> objectAndFilter : ACCOUNT_FILTERS) {
            if (scope.contains(objectAndFilter[0]) && canRead(objectAndFilter[0])) {
                readable.add(objectAndFilter);
                readableNames.add(objectAndFilter[0]);
            }
        }
        try {
            Set<String> hideable = hideableObjects(readableNames);
            for (List<String> objectAndFilter : readable) {
                String objectName = objectAndFilter[0];
                if (!hideable.contains(objectName)) {
                    continue;
                }
                String filter = objectAndFilter[1];
                if (objectName == 'Contract' && preserveContractsWithPrices && typeOf('ContractItemPrice') != null) {
                    // Contracts that option keeps are not the reset's to report.
                    filter += ' AND Id NOT IN (SELECT ContractId FROM ContractItemPrice)';
                }
                recordRetained(typeOf(objectName), hiddenCount(objectName, filter, accountId), NOT_VISIBLE);
            }
        } catch (Exception e) {
            // After a completed phase 2, so nothing here may fail the run: a throw from
            // the invocable would roll the whole reset back.
            report.incompleteHidden = true;
        }
    }

    /**
     * The objects among `objectNames` whose sharing model can hide a record from a user
     * who can read the object: Private and Controlled by Parent. One query.
     */
    private static Set<String> hideableObjects(List<String> objectNames) {
        Set<String> hideable = new Set<String>();
        if (objectNames.isEmpty()) {
            return hideable;
        }
        if (hiddenForTest != null) {
            hideable.addAll(hiddenForTest.keySet());
            return hideable;
        }
        requireQueries(1);
        for (EntityDefinition entity : [
            SELECT QualifiedApiName, InternalSharingModel FROM EntityDefinition WHERE QualifiedApiName IN :objectNames
        ]) {
            if (entity.InternalSharingModel == 'Private' || entity.InternalSharingModel == 'ControlledByParent') {
                hideable.add(entity.QualifiedApiName);
            }
        }
        return hideable;
    }

    /**
     * How many of the account's `objectName` records the running user cannot see: the
     * system-mode count less the count this class sees, which is what its deletes saw.
     * Stops the count, not the run, when its two queries are not left.
     */
    @TestVisible
    private static Integer hiddenCount(String objectName, String filter, Id accountId) {
        if (hiddenForTest != null) {
            return hiddenForTest.containsKey(objectName) ? hiddenForTest.get(objectName) : 0;
        }
        requireQueries(2);
        String soql = 'SELECT COUNT() FROM ' + objectName + ' WHERE ' + filter;
        Integer total = Database.countQuery(soql, AccessLevel.SYSTEM_MODE);
        Integer seen = Database.countQuery(soql);
        return Math.max(0, total - seen);
    }

    /**
     * The records the running user may delete; the rest are reported as kept and the
     * records themselves are left unchanged. Call it before changing a record on the way
     * to deleting it (an order set back to Draft, a credit memo canceled), and before an
     * all-or-nothing delete. Live 264, the salesrep persona's reset set an activated order
     * it did not own back to Draft, and the delete was then refused ("insufficient access
     * rights on object id"): running without sharing does not lift that, and sharing gave
     * the user edit on the order, not delete.
     *
     * @return A list of the same type as `records`
     */
    @TestVisible
    private static List<SObject> keepWhatUserCannotDelete(List<SObject> records) {
        return keepUndeletable(records, deletableByUser(idsToCheck(new List<List<SObject>>{ records })));
    }

    /**
     * The ids to look up in deletableByUser: those of records whose object the user may
     * delete at all. Records of an object the user may not delete are kept anyway
     * (keepUndeletable), so reading their access would spend a query for nothing.
     */
    private static Set<Id> idsToCheck(List<List<SObject>> lists) {
        Set<Id> ids = new Set<Id>();
        for (List<SObject> records : lists) {
            if (!records.isEmpty() && objectIsDeletable(records[0].getSObjectType())) {
                ids.addAll(new Map<Id, SObject>(records).keySet());
            }
        }
        return ids;
    }

    /**
     * Two checks, as the platform makes them. The object first: a user without delete
     * permission on it keeps every record, whoever owns them. Live 264 that is also what
     * reflects Allow Revenue Records Deletion for credit memos: describe's isDeletable()
     * was false without it and true with it, while UserRecordAccess.HasDeleteAccess did
     * not change. Then each record, against `allowed` (deletableByUser).
     */
    private static List<SObject> keepUndeletable(List<SObject> records, Set<Id> allowed) {
        if (records.isEmpty()) {
            return records;
        }
        Schema.SObjectType type = records[0].getSObjectType();
        List<SObject> deletable = records.clone();
        deletable.clear();
        if (!objectIsDeletable(type)) {
            recordRetained(type, records.size(), NO_DELETE_PERMISSION);
            return deletable;
        }
        for (SObject record : records) {
            if (allowed.contains(record.Id)) {
                deletable.add(record);
            }
        }
        recordRetained(type, records.size() - deletable.size(), NO_DELETE_ACCESS);
        return deletable;
    }

    private static Boolean objectIsDeletable(Schema.SObjectType type) {
        return deleteAccessForTest != null || type.getDescribe().isDeletable();
    }

    /**
     * The ids the running user may delete, from UserRecordAccess.HasDeleteAccess, which
     * holds what the platform enforces on the delete. A user with Modify All Data may
     * delete them all, so that costs no query beyond the permission read. UserRecordAccess
     * takes 200 ids a query. Each call site counts its first read in PHASE_TWO_FIXED_MAX;
     * a later one needs RETRY_TAIL more queries left, and without them the run stops with
     * AccessCheckTooLargeException. That stop does not say to run again: phase 2 is all or
     * nothing, so another run would stop at the same point.
     */
    @TestVisible
    private static Set<Id> deletableByUser(Set<Id> recordIds) {
        if (deleteAccessForTest != null) {
            Set<Id> allowed = new Set<Id>(recordIds);
            allowed.retainAll(deleteAccessForTest);
            return allowed;
        }
        if (recordIds.isEmpty() || hasUserPermission('PermissionsModifyAllData')) {
            return recordIds;
        }
        Id userId = UserInfo.getUserId();
        List<Id> ids = new List<Id>(recordIds);
        Set<Id> allowed = new Set<Id>();
        for (Integer start = 0; start < ids.size(); start += 200) {
            if (start > 0 && Limits.getLimitQueries() - Limits.getQueries() < 1 + RETRY_TAIL) {
                throw new AccessCheckTooLargeException(ACCESS_CHECK_TOO_LARGE);
            }
            List<Id> chunk = new List<Id>();
            for (Integer i = start; i < Math.min(start + 200, ids.size()); i++) {
                chunk.add(ids[i]);
            }
            for (UserRecordAccess access : [
                SELECT RecordId, HasDeleteAccess FROM UserRecordAccess WHERE UserId = :userId AND RecordId IN :chunk
            ]) {
                if (access.HasDeleteAccess) {
                    allowed.add(access.RecordId);
                }
            }
        }
        return allowed;
    }

    /**
     * readOrNote for each object, so every one the user cannot read is reported. When
     * any of them cannot be read the group is skipped, and the readable ones skipped with
     * it are reported too (report.skippedWith).
     */
    private static Boolean readAllOrNote(List<String> objectNames) {
        Boolean all = true;
        List<String> readable = new List<String>();
        for (String objectName : objectNames) {
            if (readOrNote(objectName)) {
                readable.add(objectName);
            } else {
                all = false;
            }
        }
        if (!all) {
            for (String objectName : readable) {
                String label = labelOf(typeOf(objectName));
                if (!report.skippedWith.contains(label)) {
                    report.skippedWith.add(label);
                }
            }
        }
        return all;
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
     * back to Draft, a credit memo canceled): any refusal throws and rolls back phase 2,
     * so a record is never left changed but kept.
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
     * or Billing Dispute Management. Plans and disputes are skipped, and reported,
     * for a user who cannot read them or their cases; disputes raised against the
     * account's invoices are found only when the user can read invoices.
     */
    private static void deleteCollectionRecords(Id accountId, List<Invoice> invoices) {
        Set<Id> caseIds = new Set<Id>();
        if (typeOf('CollectionPlan') != null
            && readAllOrNote(new List<String>{ 'CollectionPlan', 'CollectionPlanItem', 'PaymentSchedule', 'Case' })) {
            List<SObject> plans = Database.query('SELECT Id FROM CollectionPlan WHERE AccountId = :accountId');
            Set<Id> planIds = new Map<Id, SObject>(plans).keySet();
            if (!planIds.isEmpty()) {
                // Bound, not a semi-join: SOQL does not allow a semi-join inside OR.
                Set<Id> itemIds = new Map<Id, SObject>(Database.query(
                    'SELECT Id FROM CollectionPlanItem WHERE CollectionPlanId IN :planIds')).keySet();
                deleteQuietly(Database.query('SELECT Id FROM PaymentSchedule WHERE ReferenceEntityId IN :planIds '
                    + 'OR CollectionPlanItemId IN :itemIds'));
                Map<Id, Set<Id>> casesByPlan = new Map<Id, Set<Id>>();
                for (SObject planCase : Database.query(
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
        if (typeOf('Dispute') != null && readAllOrNote(new List<String>{ 'Dispute', 'Case' })) {
            Set<Id> invoiceIds = new Map<Id, Invoice>(invoices).keySet();
            List<SObject> disputes = Database.query('SELECT Id, CaseId, Case.AccountId FROM Dispute '
                + 'WHERE AccountId = :accountId OR InvoiceId IN :invoiceIds');
            Set<Id> gone = deleteRows(disputes, false);
            for (SObject dispute : disputes) {
                SObject disputeCase = dispute.getSObject('Case');
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
     * or void debit memos, are left in place.
     *
     * Permissions, measured live on 264 (todo 397):
     *  - Posted invoices need "Delete Invoice and Invoice Lines" (BillingInvoiceSuperUser,
     *    from RLM_DeleteInvoices). Without it only Draft and Canceled invoices go, and
     *    the rest are reported as retained. Invoices still processing stay either way.
     *  - Draft and Canceled invoices need that permission or "Allow Revenue Records
     *    Deletion" (DeleteRevenueRecords, in the managed Billing Admin set); without
     *    either the platform refuses them, and the refusal is reported.
     *  - Credit memos need Allow Revenue Records Deletion (deleteCreditMemos).
     * Allow Revenue Records Deletion does NOT let a Posted invoice be deleted, so it
     * does not replace Delete Invoice and Invoice Lines.
     *
     * Posted invoices are attempted only for a user who has the permission, and the
     * invoices go in ONE delete call that is never retried. Do not add a retry or a
     * fallback attempt: an invoice the platform refuses must stay refused. Live 264, a
     * second delete of a Posted invoice the platform had just refused, in the same
     * transaction, by a user with only Allow Revenue Records Deletion, succeeded.
     *
     * Deleting an invoice takes its lines, taxes, billing period items, credit
     * memo and payment applications, and billing journals with it. It does not
     * take its payment schedule, files or DocumentGenerationProcess rows, which
     * are deleted here.
     *
     * Each kind of record is handled only when the running user can read it; the
     * rest are reported as not checked. A user who cannot read invoices cannot read
     * credit memo applications either (that read depends on invoice read), so the
     * credit memos, which need the kept invoices, are skipped with them.
     */
    private static void deleteBillingRecords(Id accountId, OrderData orderData) {
        // First, so that a debit memo line adjusting an invoice line, or a debit
        // memo raised from a credit memo, is gone before either is deleted.
        deleteDebitMemos(accountId);

        Set<Id> keptInvoiceIds = readOrNote('Invoice') ? deleteInvoices(orderData.invoices) : null;
        if (readAllOrNote(new List<String>{ 'CreditMemo', 'CreditMemoInvApplication' }) && keptInvoiceIds != null) {
            deleteCreditMemos(accountId, keptInvoiceIds);
        }
        if (readOrNote('Payment')) {
            recordRetained(Payment.SObjectType, [SELECT COUNT() FROM Payment WHERE AccountId = :accountId], PAYMENTS_KEPT);
        }
    }

    /**
     * Deletes the invoices Delete Billing may delete, with their payment schedules,
     * generated documents and the files nothing else shares.
     *
     * @return The ids of the invoices that were kept
     */
    private static Set<Id> deleteInvoices(List<Invoice> invoices) {
        List<Invoice> deletable = new List<Invoice>();
        List<Invoice> needPermission = new List<Invoice>();
        Integer processing = 0;
        for (Invoice inv : invoices) {
            String status = inv.Status == null ? '' : inv.Status;
            if (status == 'Draft' || status == 'Canceled') {
                deletable.add(inv);
            } else if (status.endsWith('In Progress') || status == 'Processing') {
                processing++;
            } else {
                needPermission.add(inv);
            }
        }
        recordRetained(Invoice.SObjectType, processing, INVOICE_IN_PROGRESS);
        if (!needPermission.isEmpty()) {
            if (canDeletePostedInvoices()) {
                deletable.addAll(needPermission);
            } else {
                recordRetained(Invoice.SObjectType, needPermission.size(), INVOICE_NEEDS_PERMISSION);
            }
        }

        // Collected first: the delete takes the files' links with it.
        Map<Id, Set<Id>> files = exclusiveFiles(new Map<Id, Invoice>(deletable).keySet());
        Set<Id> deleted = deleteRows(deletable, false);

        Set<Id> keptInvoiceIds = new Set<Id>();
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
        if (!schedules.isEmpty() && readOrNote('PaymentSchedule')) {
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
        return keptInvoiceIds;
    }

    /**
     * True when the running user has BillingInvoiceSuperUser ("Delete Invoice and
     * Invoice Lines"), from their profile, a permission set or a group. Live 264 it
     * is the only permission that lets a Posted invoice be deleted, settled or not;
     * Allow Revenue Records Deletion alone is refused with "You can only delete the
     * invoice if it is in Draft or Canceled status."
     */
    @TestVisible
    private static Boolean canDeletePostedInvoices() {
        return hasUserPermission('PermissionsBillingInvoiceSuperUser');
    }

    /**
     * True when the running user has DeleteRevenueRecords ("Allow Revenue Records
     * Deletion", in the managed Billing Admin permission set). Live 264 it is what
     * lets a Draft or Canceled credit memo be deleted; Delete Invoice and Invoice
     * Lines does not ("DML operation DELETE not allowed on CreditMemo"). It also
     * lets Draft and Canceled invoices be deleted, as Delete Invoice and Invoice
     * Lines does, but not Posted ones.
     */
    @TestVisible
    private static Boolean canDeleteRevenueRecords() {
        return hasUserPermission('PermissionsDeleteRevenueRecords');
    }

    // The running user's billing delete permissions, read once per user.
    private static Map<String, Boolean> userPermissions;
    private static Id userPermissionsOf;

    /**
     * Whether the running user has the permission, from their profile, a permission
     * set or a group. UserPermissionAccess holds the user's effective permissions,
     * and any user may read their own; a non-admin is refused PermissionSetAssignment.
     * Both permissions are read in one query, so asking for the second costs none.
     * Dynamic, so a release without either field reads both as false instead of
     * failing to compile.
     */
    private static Boolean hasUserPermission(String field) {
        if (userPermissions == null || userPermissionsOf != UserInfo.getUserId()) {
            userPermissionsOf = UserInfo.getUserId();
            userPermissions = new Map<String, Boolean>();
            List<String> fields = new List<String>{
                'PermissionsBillingInvoiceSuperUser', 'PermissionsDeleteRevenueRecords', 'PermissionsModifyAllData',
                'PermissionsViewAllData'
            };
            List<SObject> access = new List<SObject>();
            try {
                access = Database.query('SELECT ' + String.join(fields, ', ') + ' FROM UserPermissionAccess');
            } catch (QueryException e) {
                access = new List<SObject>();
            }
            for (String name : fields) {
                userPermissions.put(name, !access.isEmpty() && access[0].get(name) == true);
            }
        }
        return userPermissions.get(field) == true;
    }

    /**
     * A posted credit memo cannot be deleted, but it can be canceled and a canceled
     * one deleted, which takes its lines and journals with it (live 264). Memos
     * applied to an invoice that was kept are left alone: canceling one would
     * change that invoice's balance.
     *
     * Deleting a credit memo, Draft and Canceled included, needs Allow Revenue
     * Records Deletion (canDeleteRevenueRecords). Without it none is canceled or
     * deleted: canceling a memo that then cannot be deleted would change it and
     * still keep it.
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
        if ((!deletable.isEmpty() || !posted.isEmpty()) && !canDeleteRevenueRecords()) {
            recordRetained(CreditMemo.SObjectType, deletable.size() + posted.size(), MEMO_NEEDS_PERMISSION);
            return;
        }
        // A posted memo the user cannot delete must not be canceled. One access read for both.
        List<CreditMemo> candidates = new List<CreditMemo>(deletable);
        candidates.addAll(posted);
        Set<Id> allowed = new Map<Id, CreditMemo>((List<CreditMemo>) keepWhatUserCannotDelete(candidates)).keySet();
        deletable = onlyIds(deletable, allowed);
        posted = onlyIds(posted, allowed);
        // All or nothing, as for orders: no memo is left canceled but not deleted.
        updateAll(posted);
        for (CreditMemo canceled : posted) {
            deletable.add(new CreditMemo(Id = canceled.Id));
        }
        deleteAll(deletable);
    }

    private static List<CreditMemo> onlyIds(List<CreditMemo> memos, Set<Id> ids) {
        List<CreditMemo> kept = new List<CreditMemo>();
        for (CreditMemo memo : memos) {
            if (ids.contains(memo.Id)) {
                kept.add(memo);
            }
        }
        return kept;
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
        if (!readOrNote('DebitMemo')) {
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
        if (recordIds.isEmpty()) {
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
        // First: an order the user cannot delete must not be set back to Draft.
        List<Order> orders = (List<Order>) keepWhatUserCannotDelete(orderData.orders);
        if (orders.isEmpty()) {
            return;
        }
        // All or nothing: any refusal now fails the run with the platform's message and
        // rolls phase 2 back, so no order is left set back to Draft but not deleted.
        for (Order o : orders) {
            o.Status = 'Draft';
        }
        updateAll(orders);
        deleteAll(orders);
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
        if (!readOrNote('BillingScheduleGroup')) {
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
        // A contract the user cannot delete is kept, with its rate card entries,
        // rather than failing the all-or-nothing delete below.
        contracts = (List<Contract>) keepWhatUserCannotDelete(contracts);
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
     * One the running user cannot read is skipped and reported.
     */
    private static void deleteOtherAssetReferences(Set<Id> assetIds) {
        for (String objectName : new List<String>{ 'WorkOrder', 'Case' }) {
            if (!readOrNote(objectName)) {
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
        List<AssetRelationship> relationships = [
            SELECT Id, AssetId FROM AssetRelationship WHERE AssetId IN :accountAssetIds
        ];
        List<Asset> assets = [SELECT Id FROM Asset WHERE Id IN :accountAssetIds];
        // Those the user cannot delete are kept, rather than failing the deletes below;
        // a kept asset keeps its relationships. One access read for both.
        Set<Id> allowed = deletableByUser(idsToCheck(new List<List<SObject>>{ relationships, assets }));
        assets = (List<Asset>) keepUndeletable(assets, allowed);
        Set<Id> deletableAssets = new Map<Id, Asset>(assets).keySet();
        List<AssetRelationship> ofDeletableAssets = new List<AssetRelationship>();
        for (AssetRelationship relationship : relationships) {
            if (deletableAssets.contains(relationship.AssetId)) {
                ofDeletableAssets.add(relationship);
            }
        }
        deleteAll(keepUndeletable(ofDeletableAssets, allowed));
        deleteAll(assets);
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
        if (!readOrNote('FulfillmentStepSource')) {
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
        if (!readOrNote('AssetFulfillmentDecomp')) {
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
}
