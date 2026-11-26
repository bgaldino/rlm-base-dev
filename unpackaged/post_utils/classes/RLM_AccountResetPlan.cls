/**
 * RLM_AccountResetPlan
 *
 * The account reset for a user WITHOUT both Modify All Data and View All Data
 * (owner decision, todo 397: "Admins keep main's engine"). RLM_AccountUtilities, the
 * invocable, sends such a user here; a user with both runs its own engine.
 *
 * One deletion plan. The run first builds a Plan: for the selected options, the exact
 * records each step deletes or changes, read once, in system mode, with one set of
 * queries and helpers (the bucket tree walk included). The plan is checked before
 * anything changes, and the deletes then remove exactly the plan's records and
 * nothing else, so a record cannot be deleted without having been checked, and the
 * check cannot drift from the deletes.
 *
 * The check (owner decision: refuse the whole reset). If the running user cannot see
 * the account, the run is refused with nothing else said. If the user could not
 * delete every planned record, nothing is changed and the Result says the reset was
 * not run and lists why: records in an object the user cannot read, or that the user
 * cannot see, are counted; records the user can see are named, with the reason (no
 * delete permission on the object, no delete access to the record, or a permission
 * the run needs on it: Edit Activated Orders, Delete Activated Contracts, Access
 * Lifecycle-Managed Assets, Delete Invoice and Invoice Lines, Allow Revenue Records
 * Deletion), and invoices still processing are named too, as are an asset or an order
 * that a usage entitlement the reset keeps still refers to. The advice fits the
 * blocker: another user's permission or access, waiting for the invoices, or, for an
 * asset or order, Delete Assets off or the entitlement removed first. Live 264 (the salesrep persona, under System.runAs and in
 * a Login As session) a query in a class declared without sharing saw only the records
 * sharing showed that user, and a delete of a record the user could edit but not
 * delete was refused; that is why the plan is read in system mode and checked per
 * record.
 *
 * No partial runs. Every read of the plan, the per-record access reads included, is
 * bounded by the query rows and heap left, and each first requires a query to spare
 * beyond the ones kept for the decision table refresh the flow runs afterwards
 * (REFRESH_RESERVE); the check itself first requires heap for the planned rows.
 * Reaching a bound refuses the run, changing nothing, with a message that a user with
 * Modify All Data and View All Data can run it (they take RLM_AccountUtilities' engine,
 * which converges over several runs). So does a plan whose rows exceed the DML rows
 * left. The deletes then run inside one savepoint, all or nothing: every planned usage
 * row first, the asset-bound ones included, with the record alerts on the journals (its
 * constraints are circular, so they are retried round after round until a round removes
 * nothing), so no entitlement is left to block an order or asset; then collections,
 * billing, fulfillment, contracts with their rate card entries, orders, assets with
 * theirs, quotes and opportunities.
 * Every delete is all or nothing (a row a parent's delete already took counts as
 * deleted). If the platform refuses any planned row, a usage row is still there when
 * the usage teardown can do no more, anything fails, or a limit is reached part way,
 * all of it rolls back and the Result says nothing was changed and why, naming the
 * refused record. One DML statement is kept for the rollback (STATEMENTS_KEPT), which
 * counts as one; the savepoint is set before any delete, so it needs no more.
 *
 * Sharing: `without sharing`, deliberately: the plan must see records sharing hides
 * from the user, so a refusal can count them. Nothing is deleted that the check has
 * not cleared for the user. The Plan inner class declares `without sharing` itself: an
 * inner class does not take the outer class's keyword, and AccessLevel.SYSTEM_MODE
 * leaves record sharing to it.
 */
public without sharing class RLM_AccountResetPlan {
    // Usage teardown. The graph has circular delete constraints (a ratable summary
    // can be held by a usage summary and vice versa, a bucket by its children), so the
    // planned usage rows are retried round after round until a round removes nothing.
    // Six rounds has been ample; the cap only exists so a pathological graph cannot
    // spin, and reaching it rolls the run back. A round runs no queries.
    private static final Integer MAX_TEARDOWN_ROUNDS = 6;
    // Queries the plan leaves for the flow's decision table refresh, which runs after the
    // reset in the same transaction. Measured live 264 on tkdef: the refresh of the two
    // active PricingDiscovery tables took 1 query, as an admin and as the salesrep persona.
    @TestVisible
    private static final Integer REFRESH_RESERVE = 5;
    // DML statements no delete may use: the rollback counts as one (measured live 264:
    // setSavepoint and rollback each added one). The savepoint is set before any delete,
    // so the rollback is all that needs one.
    @TestVisible
    private static final Integer STATEMENTS_KEPT = 1;
    // Heap the check needs per planned row for its maps (ids, names, access), so a plan
    // too large to check is refused before they are built.
    private static final Integer CHECK_BYTES_PER_ROW = 500;
    // Ids per UserRecordAccess read: the most it accepts.
    private static final Integer ACCESS_BATCH = 200;
    // Names listed per object and reason in a refusal; the rest are counted.
    private static final Integer NAMES_LISTED = 5;

    private static final String USAGE_TOO_LARGE = 'The account has more usage records than one run can remove.';
    private static final String FOREIGN_BUCKET = 'kept: holds, or is above, another account\'s entitlement';
    private static final String HELD_BY_KEPT_BUCKET = 'kept: held by a bucket kept for another account\'s entitlement';
    private static final String DML_LIMIT = 'The reset reached the Salesforce limit on record changes in one run.';
    private static final String PAYMENTS_KEPT = 'payments are not deleted: Salesforce does not allow deleting processed payments';
    private static final String DEBIT_MEMOS_KEPT = 'posted or void; Salesforce does not allow deleting them, or canceling a posted one';

    // Refusal. Plain wording: the reset was not run.
    @TestVisible
    private static final String REFUSED = 'The reset was not run, and nothing was changed: the user running it '
        + 'cannot delete everything it would delete.';
    @TestVisible
    private static final String REFUSED_ADVICE = 'Ask a user who has the permission or access named above to run '
        + 'it (Modify All Data covers record access, not the named permissions), or have the records reassigned to '
        + 'the user running the reset.';
    @TestVisible
    private static final String TOO_LARGE_FOR_USER = 'The account has too many records for a reset by this user. A '
        + 'user with Modify All Data and View All Data can run it.';
    @TestVisible
    private static final String PLAN_TOO_LARGE = 'The reset was not run, and nothing was changed. ' + TOO_LARGE_FOR_USER;
    @TestVisible
    private static final String NO_ACCOUNT_ACCESS = 'The reset was not run, and nothing was changed: the user running '
        + 'it cannot see this account.';
    @TestVisible
    private static final String ROLLED_BACK = 'Nothing was changed; the run was rolled back.';
    @TestVisible
    private static final String NOT_YET = 'The reset was not run, and nothing was changed: some of the records it '
        + 'would delete cannot be deleted yet.';
    @TestVisible
    private static final String NOT_YET_ADVICE = 'Run the reset again once the invoices finish processing.';
    // Another account's entitlement is not named: it is that account's record, which the user
    // may not be allowed to see (the same reason a refusal never repeats the platform's message).
    @TestVisible
    private static final String ASSET_KEPT_ADVICE = 'No permission or reassignment lets the asset named above go '
        + 'while its usage entitlement is held by a bucket kept for another account\'s entitlement: run the reset '
        + 'with Delete Assets off, which keeps the asset, or have the other account\'s entitlement removed first.';
    @TestVisible
    private static final String ORDER_KEPT_ADVICE = 'No permission or reassignment lets the order named above go '
        + 'while a usage entitlement the reset keeps refers to its lines: have the other account\'s entitlement '
        + 'removed first, or ask a user with Modify All Data and View All Data to run the reset, which deletes the '
        + 'rest and reports the order as not deleted.';
    @TestVisible
    private static final String NO_PERMISSION = 'no permission to delete this kind of record';
    @TestVisible
    private static final String NO_ACCESS = 'no delete access to these records';
    @TestVisible
    private static final String NOT_VISIBLE = 'not visible to the user running the reset';
    private static final String CANNOT_READ = 'the user running the reset cannot read this kind of record';
    private static final String NEEDS_EDIT_ACTIVATED = 'activated; setting them back to Draft needs the Edit '
        + 'Activated Orders permission';
    @TestVisible
    private static final String NEEDS_DELETE_ACTIVATED_CONTRACT = 'activated; deleting them needs the Delete '
        + 'Activated Contracts permission';
    @TestVisible
    private static final String ORDER_LINE_ENTITLEMENT_KEPT = 'another account\'s usage entitlement, or one held by '
        + 'a bucket kept for another account\'s entitlement, refers to one of its order lines, so it cannot be deleted';
    @TestVisible
    private static final String ASSET_ENTITLEMENT_KEPT = 'its usage entitlement is held by a bucket kept for '
        + 'another account\'s entitlement, so it cannot be deleted';
    private static final String NEEDS_LIFECYCLE = 'lifecycle-managed; deleting them needs the Access '
        + 'Lifecycle-Managed Assets permission';
    private static final String INVOICE_NEEDS_PERMISSION = 'not Draft or Canceled; deleting them needs the '
        + 'Delete Invoice and Invoice Lines permission (permission set RLM_DeleteInvoices)';
    @TestVisible
    private static final String MEMO_NEEDS_PERMISSION = 'deleting credit memos needs the Allow Revenue Records '
        + 'Deletion permission (Billing Admin permission set)';
    @TestVisible
    private static final String INVOICE_IN_PROGRESS = 'still processing; run the reset once they finish';

    /** Ends a run early when a limit is close, before the platform throws a LimitException. */
    private class ResetStoppedException extends Exception {}

    /** The platform refused a planned row: the run rolls back. */
    private class RefusedException extends Exception {}

    /** Ends the planning, before anything changes, when the account is too large to plan in one run. */
    private class PlanTooLargeException extends Exception {}

    /** What the current run removed and did not remove. A rollback starts it over: nothing is listed. */
    private class ResetReport {
        public List<String> removedLabels = new List<String>();
        public Map<String, Integer> removed = new Map<String, Integer>();
        public List<Kept> kept = new List<Kept>();
        // Rows a delete refused, with the error and its status code. A later attempt that
        // removes the row takes it back out.
        public Map<Id, String> refused = new Map<Id, String>();
        public Map<Id, String> refusedCode = new Map<Id, String>();
    }

    /** Rows of one object not deleted for one reason. Replaced, never changed, so a shallow copy is safe. */
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

    // The plan's groups of records. The usage groups are deleted first, then the rest.
    private static final String G_POLICIES = 'policies';
    private static final String G_ACCOUNT_RATE_CARD_ENTRIES = 'accountRateCardEntries';
    private static final String G_ENTRIES = 'entries';
    private static final String G_BILLING_PERIOD_ITEMS = 'billingPeriodItems';
    private static final String G_SUMMARIES = 'summaries';
    private static final String G_RATABLE_SUMMARIES = 'ratableSummaries';
    private static final String G_JOURNALS = 'journals';
    private static final String G_JOURNAL_ALERTS = 'journalAlerts';
    private static final String G_BUCKETS = 'buckets';
    private static final String G_ENTITLEMENTS = 'entitlements';
    private static final String G_ENTITLEMENT_ACCOUNTS = 'entitlementAccounts';
    private static final String G_COMMITMENT_JUNCTIONS = 'commitmentJunctions';
    private static final String G_ASSETS = 'assets';
    private static final String G_ASSET_RATE_CARD_ENTRIES = 'assetRateCardEntries';
    private static final String G_ASSET_SOURCED_RATE_CARD_ENTRIES = 'assetSourcedRateCardEntries';
    private static final String G_ASSET_RELATIONSHIPS = 'assetRelationships';
    private static final String G_ASSET_ENTITLEMENTS = 'assetEntitlements';
    private static final String G_ASSET_ENTRIES = 'assetEntries';
    private static final String G_ASSET_BUCKETS = 'assetBuckets';
    private static final String G_WORK_ORDERS = 'workOrders';
    private static final String G_ASSET_CASES = 'assetCases';
    private static final String G_CONTRACTS = 'contracts';
    private static final String G_CONTRACT_RATE_CARD_ENTRIES = 'contractRateCardEntries';
    private static final String G_SCHEDULE_GROUPS = 'scheduleGroups';
    private static final String G_ORDERS = 'orders';
    private static final String G_INVOICES = 'invoices';
    private static final String G_DEBIT_MEMOS = 'debitMemos';
    private static final String G_CREDIT_MEMOS = 'creditMemos';
    private static final String G_INVOICE_SCHEDULES = 'invoiceSchedules';
    private static final String G_INVOICE_DOCUMENTS = 'invoiceDocuments';
    private static final String G_COLLECTION_PLANS = 'collectionPlans';
    private static final String G_PLAN_SCHEDULES = 'planSchedules';
    private static final String G_DISPUTES = 'disputes';
    private static final String G_COLLECTION_CASES = 'collectionCases';
    private static final String G_FULFILLMENT_ORDERS = 'fulfillmentOrders';
    private static final String G_FULFILLMENT_ORDER_LINES = 'fulfillmentOrderLines';
    private static final String G_FULFILLMENT_PLANS = 'fulfillmentPlans';
    private static final String G_STEP_SOURCES = 'stepSources';
    private static final String G_FULFILLMENT_ASSETS = 'fulfillmentAssets';
    private static final String G_DECOMPOSITIONS = 'decompositions';
    private static final String G_LINE_SOURCE_RELATIONS = 'lineSourceRelations';
    private static final String G_QUOTES = 'quotes';
    private static final String G_OPPORTUNITIES = 'opportunities';
    private static final String G_QUOTE_DOCUMENTS = 'quoteDocuments';
    private static final String G_FILES = 'files';

    private static ResetReport report = new ResetReport();

    // The plan of the current run.
    private static Plan plan;

    // Lets a test fail the run after it has deleted something, to prove the rollback.
    @TestVisible
    private static Exception failureForTest;

    // Lets a test shrink the teardown round cap, to reach USAGE_TOO_LARGE and the rollback.
    @TestVisible
    private static Integer maxTeardownRoundsForTest;

    // Lets a test shrink the heap the check sees, to prove a plan too large to check is refused.
    @TestVisible
    private static Integer heapLeftForTest;

    // Lets a test shrink the DML row budget, to prove a plan larger than it is refused.
    @TestVisible
    private static Integer dmlRowLimitForTest;

    // Let a test run as a user who cannot read, or has no delete permission on, these
    // objects (canRead, objectDeletable), since a test user cannot be given the usage and
    // core object access the reset also needs.
    @TestVisible
    private static Set<String> unreadableForTest = new Set<String>();
    @TestVisible
    private static Set<String> undeletableForTest = new Set<String>();

    // Lets a test stand in for missing permissions, by field name, since a test cannot
    // take a permission away from the running admin.
    @TestVisible
    private static Set<String> withoutPermissionForTest = new Set<String>();

    /**
     * Resets the account for a user without both Modify All Data and View All Data. The
     * caller (RLM_AccountUtilities.delAccountRelatedObjects) has validated the Id.
     */
    public static RLM_AccountUtilities.Result reset(Id accountId, RLM_AccountUtilities.InputVariables input) {
        startRun();
        Boolean deleteAssets = input.DeleteAssets == true;
        Boolean deleteFulfillment = input.DeleteFulfillment == true;
        Boolean deleteBilling = input.DeleteBilling == true;
        Boolean deleteCollections = input.DeleteCollectionPlans == true;
        Boolean preserveContractsWithPrices = input.PreserveContractsWithContractedPrices == true;

        // A user who cannot see the account learns nothing about what is on it. The check
        // is the run's first query, so it too leaves the refresh its queries.
        if (Limits.getLimitQueries() - Limits.getQueries() - REFRESH_RESERVE < 1) {
            return refuse(PLAN_TOO_LARGE);
        }
        if (!canSeeAccount(accountId)) {
            return refuse(NO_ACCOUNT_ACCESS);
        }

        // ------------------------------------------------------------------
        // The plan, and its check. Read only: a refusal changes nothing.
        try {
            plan = new Plan(accountId, deleteAssets, deleteFulfillment, deleteBilling, deleteCollections,
                preserveContractsWithPrices);
        } catch (PlanTooLargeException e) {
            return refuse(PLAN_TOO_LARGE);
        }
        if (!plan.blockers.isEmpty()) {
            return refuse(refusal(plan.blockers, plan.describeBlockers()));
        }
        // Every planned row is deleted once, and orders and posted credit memos are also
        // updated once, so this is what the deletes need: more than is left would stop the
        // run part way, so it is refused now instead.
        if (plan.dmlRows() > dmlRowsLeft()) {
            return refuse(PLAN_TOO_LARGE);
        }
        // Not deleted by design: another account's data, and what Salesforce never deletes.
        recordRetained(UsageEntitlementBucket.SObjectType, plan.foreignBuckets, FOREIGN_BUCKET);
        recordRetained(UsageEntitlementAccount.SObjectType, plan.keptEntitlementAccounts, FOREIGN_BUCKET);
        recordRetained(TransactionUsageEntitlement.SObjectType, plan.keptEntitlements, HELD_BY_KEPT_BUCKET);
        recordRetained(Payment.SObjectType, plan.payments, PAYMENTS_KEPT);
        if (plan.lockedDebitMemos > 0) {
            recordRetained(typeOf('DebitMemo'), plan.lockedDebitMemos, DEBIT_MEMOS_KEPT);
        }
        for (String status : plan.creditMemosByOtherStatus.keySet()) {
            recordRetained(CreditMemo.SObjectType, plan.creditMemosByOtherStatus.get(status),
                'status ' + status + ' can be neither canceled nor deleted');
        }

        // ------------------------------------------------------------------
        // The deletes, inside one savepoint: all of it is kept, or none of it.
        Savepoint sp = Database.setSavepoint();
        try {
            // The usage graph first, all of it: policies, the account's own rate card
            // entries, summaries, entitlements and their buckets (those bound to the assets
            // included), journals and commitment junctions. A row still there when a round
            // removes nothing rolls the run back.
            teardown(USAGE_TEARDOWN, true);
            // Before billing: deleting an invoice clears a dispute's link to it.
            if (deleteCollections) {
                deleteCollectionRecords();
            }
            deleteAll(plan.rowsOf(G_SCHEDULE_GROUPS));
            if (deleteBilling) {
                deleteBillingRecords();
            }
            // Fulfillment records that reference orders and order lines go first.
            if (deleteFulfillment) {
                deleteAll(plan.rowsOf(G_LINE_SOURCE_RELATIONS));
                deleteAll(plan.rowsOf(G_STEP_SOURCES));
                deleteAll(plan.rowsOf(G_FULFILLMENT_ORDER_LINES));
                deleteAll(plan.rowsOf(G_FULFILLMENT_ORDERS));
            }
            // A contract's rate card entries go with it; contracts Preserve Contracts
            // with Contracted Prices keeps are not in the plan, nor are their entries.
            deleteAll(plan.rowsOf(G_CONTRACT_RATE_CARD_ENTRIES));
            deleteAll(plan.rowsOf(G_CONTRACTS));
            // An activated order cannot be deleted, so it goes back to Draft first; an order
            // already in Draft is not updated. All or nothing.
            updateAll(plan.ordersToDraft());
            deleteAll(plan.rowsOf(G_ORDERS));
            if (deleteFulfillment) {
                deleteAll(plan.rowsOf(G_FULFILLMENT_PLANS));
                deleteAll(plan.rowsOf(G_DECOMPOSITIONS));
                deleteAll(plan.rowsOf(G_FULFILLMENT_ASSETS));
            }
            if (deleteAssets) {
                deleteAssets();
            }
            deleteAll(plan.rowsOf(G_QUOTE_DOCUMENTS));
            deleteAll(plan.rowsOf(G_FILES));
            deleteAll(plan.rowsOf(G_QUOTES));
            deleteAll(plan.rowsOf(G_OPPORTUNITIES));

            if (failureForTest != null) {
                throw failureForTest;
            }
        } catch (Exception e) {
            Database.rollback(sp);
            // Nothing was changed, so nothing is listed: the rows a completed run would have
            // kept by design (payments, another account's buckets) would read as the only
            // ones left.
            report = new ResetReport();
            // A limit reached part way (DML rows or statements, or the teardown's round cap):
            // the account is too large for this path. A refusal or failure: the platform's
            // message, with the record. Either way nothing is kept.
            String cause = e instanceof ResetStoppedException
                ? e.getMessage() + ' ' + TOO_LARGE_FOR_USER
                : e.getMessage();
            return finish(false, ROLLED_BACK + ' ' + cause);
        }
        return finish(true, null);
    }

    /**
     * A failed update (an order set back to Draft, a credit memo canceled), described from
     * its status code: the platform's message can name other records.
     */
    private static String dmlFailure(DmlException e) {
        Id rowId = e.getDmlId(0);
        return updateRefusalOf(rowId, String.valueOf(e.getDmlType(0)));
    }

    /** "Salesforce refused to change Order 00000123: a validation rule blocks the change (FIELD_CUSTOM_VALIDATION_EXCEPTION)." */
    @TestVisible
    private static String updateRefusalOf(Id rowId, String code) {
        String label = rowId == null ? 'a record' : rowId.getSObjectType().getDescribe().getLabel();
        String name = rowId != null && plan != null && plan.visibleNames.containsKey(rowId)
            ? ' ' + plan.visibleNames.get(rowId) : '';
        return 'Salesforce refused to change ' + label + name + ': ' + describeUpdateRefusal(code) + ' (' + code + ').';
    }

    /** Our description of an update's refusal: an order set back to Draft, a credit memo canceled. */
    @TestVisible
    private static String describeUpdateRefusal(String code) {
        if (code == 'FIELD_CUSTOM_VALIDATION_EXCEPTION') {
            return 'a validation rule blocks the change';
        }
        if (code == 'INSUFFICIENT_ACCESS_OR_READONLY' || code == 'INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY') {
            return 'the user running the reset does not have the access it needs';
        }
        if (code == 'ENTITY_IS_LOCKED') {
            return 'it is locked, for example by an approval';
        }
        return 'the platform refused the change';
    }

    /**
     * True when the running user can read accounts and this one. Read before the plan, so a
     * user who cannot see the account is refused with no counts of what is on it.
     */
    @TestVisible
    private static Boolean canSeeAccount(Id accountId) {
        if (!canRead('Account')) {
            return false;
        }
        Id reader = UserInfo.getUserId();
        List<UserRecordAccess> access = [
            SELECT RecordId, HasReadAccess FROM UserRecordAccess WHERE UserId = :reader AND RecordId = :accountId
        ];
        return !access.isEmpty() && access[0].HasReadAccess;
    }

    // Every planned usage row, the asset-bound ones included (with Delete Assets), deleted
    // first in one retried teardown, before any order or asset: an entitlement can refer to
    // an order line (OrderItemId) or an asset, and blocks its delete while it is there.
    // Records outside the usage graph that point at usage rows, swept from the org's
    // describe (live 264) and measured where they can be created: a record alert blocks its
    // transaction journal's delete (restricted lookup; measured), so the journals' alerts
    // are planned and go first. A commitment-rate row cascades with its ratable summary
    // (measured), and a billing period item's lookup to a usage billing period item is not
    // restricted (describe; billing period items cannot be created to measure, and the
    // restricted flag matched each of the four blocks measured). Approval, orchestration,
    // email and network records' lookups are not restricted either.
    private static final List<String> USAGE_TEARDOWN = new List<String>{
        G_POLICIES, G_ACCOUNT_RATE_CARD_ENTRIES, G_ENTRIES, G_ASSET_ENTRIES, G_BILLING_PERIOD_ITEMS, G_SUMMARIES,
        G_RATABLE_SUMMARIES, G_JOURNAL_ALERTS, G_JOURNALS, G_BUCKETS, G_ASSET_BUCKETS, G_ENTITLEMENTS,
        G_ASSET_ENTITLEMENTS, G_ENTITLEMENT_ACCOUNTS, G_COMMITMENT_JUNCTIONS
    };

    /**
     * Delete Collection Plans: the planned collection plans with their promise-to-pay
     * payment schedules, the disputes, and the cases of a plan or dispute that went.
     * Plan and dispute items go with their parents (live 264).
     */
    private static void deleteCollectionRecords() {
        deleteAll(plan.rowsOf(G_PLAN_SCHEDULES));
        deleteAll(plan.rowsOf(G_COLLECTION_PLANS));
        deleteAll(plan.rowsOf(G_DISPUTES));
        // Every plan and dispute went (a refusal rolls the run back), so all their cases go.
        deleteAll(plan.rowsOf(G_COLLECTION_CASES));
    }

    /**
     * Delete Billing: the account's Draft and Canceled debit memos, then its invoices
     * with their payment schedules, generated documents and files, then its credit
     * memos, canceling posted ones first. The plan's check refused the run if any
     * invoice is still processing, if a posted one needs Delete Invoice and Invoice
     * Lines the user lacks (live 264, the only permission that deletes a Posted
     * invoice), or if the user cannot delete credit memos (Allow Revenue Records
     * Deletion). The invoices go in ONE all-or-nothing delete that is never retried:
     * live 264, a second delete of a Posted invoice the platform had just refused, in
     * the same transaction, succeeded.
     */
    private static void deleteBillingRecords() {
        // First, so that a debit memo line adjusting an invoice line, or a debit
        // memo raised from a credit memo, is gone before either is deleted.
        deleteAll(plan.rowsOf(G_DEBIT_MEMOS));
        deleteAll(plan.rowsOf(G_INVOICES));
        deleteAll(plan.rowsOf(G_INVOICE_SCHEDULES));
        deleteAll(plan.rowsOf(G_INVOICE_DOCUMENTS));
        // A posted credit memo cannot be deleted, but a canceled one can (live 264).
        List<SObject> posted = new List<SObject>();
        for (SObject memo : plan.rowsOf(G_CREDIT_MEMOS)) {
            if (memo.get('Status') == 'Posted') {
                posted.add(new CreditMemo(Id = memo.Id, Status = 'Canceled'));
            }
        }
        updateAll(posted);
        deleteAll(plan.rowsOf(G_CREDIT_MEMOS));
    }

    /**
     * Deletes the planned assets: their rate card entries (and the binding entries sourced
     * from them), the work orders and cases that reference them, their relationships (both
     * directions) and then the assets, all or nothing. The entitlements bound to them and
     * their buckets went in the usage teardown.
     *
     * AssetRateCardEntry rows are generated when the asset is created and are NOT
     * recreated for an existing asset, so they go here, with the assets.
     */
    private static void deleteAssets() {
        deleteAll(plan.rowsOf(G_ASSET_RATE_CARD_ENTRIES));
        deleteAll(plan.rowsOf(G_ASSET_SOURCED_RATE_CARD_ENTRIES));
        deleteAll(plan.rowsOf(G_WORK_ORDERS));
        deleteAll(plan.rowsOf(G_ASSET_CASES));
        deleteAll(plan.rowsOf(G_ASSET_RELATIONSHIPS));
        deleteAll(plan.rowsOf(G_ASSETS));
    }

    /**
     * Retries the planned rows of `keys`, in order, round after round, until nothing is
     * left or a round removes nothing. The constraints between usage rows are circular, so
     * a row a round refuses may go in a later one. When a round removes nothing and rows
     * are left: on the `last` try the run rolls back, naming the refused row; otherwise
     * they are left for a later try. Still removing rows when the rounds run out rolls the
     * run back too (USAGE_TOO_LARGE).
     */
    private static void teardown(List<String> keys, Boolean last) {
        Integer maxRounds = maxTeardownRoundsForTest != null ? maxTeardownRoundsForTest : MAX_TEARDOWN_ROUNDS;
        for (Integer round = 1; round <= maxRounds; round++) {
            Integer progress = 0;
            Integer left = 0;
            for (String key : keys) {
                progress += deletePlanned(key).size();
                left += plan.rowsOf(key).size();
            }
            if (left == 0) {
                return;
            }
            if (progress == 0) {
                if (last) {
                    throw new RefusedException(refusalOf(firstLeft(keys)));
                }
                return;
            }
        }
        throw new ResetStoppedException(USAGE_TOO_LARGE);
    }

    private static Id firstLeft(List<String> keys) {
        for (String key : keys) {
            if (!plan.rowsOf(key).isEmpty()) {
                return plan.rowsOf(key)[0].Id;
            }
        }
        return null;
    }

    /**
     * "Salesforce refused to delete Usage Entitlement Bucket UEB-0001: another record still
     * refers to it (DELETE_FAILED)." The platform's own message is not repeated: it can name
     * the records that block the delete, which the user may not be allowed to see. Every
     * planned record passed the check, so the user can see it; one the user could not see
     * would be described, not named.
     */
    @TestVisible
    private static String refusalOf(Id rowId) {
        String label = rowId.getSObjectType().getDescribe().getLabel();
        String name = plan != null && plan.visibleNames.containsKey(rowId)
            ? plan.visibleNames.get(rowId) : 'a record the user cannot see';
        String code = report.refusedCode.containsKey(rowId) ? report.refusedCode.get(rowId) : null;
        return 'Salesforce refused to delete ' + label + ' ' + name + ': ' + describeRefusal(code)
            + (code == null ? '' : ' (' + code + ')') + '.';
    }

    /** Our description of a refusal's status code, in place of the platform's message. */
    @TestVisible
    private static String describeRefusal(String code) {
        if (code == 'DELETE_FAILED') {
            return 'another record still refers to it';
        }
        if (code == 'INSUFFICIENT_ACCESS_OR_READONLY' || code == 'INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY') {
            return 'the user running the reset does not have the access it needs';
        }
        if (code == 'ENTITY_IS_LOCKED') {
            return 'it is locked, for example by an approval';
        }
        return 'the platform refused the delete';
    }

    /** Deletes what is left of a planned group, best effort (the teardown's rounds), and drops what went from the plan. */
    private static Set<Id> deletePlanned(String key) {
        Set<Id> gone = deleteRows(plan.rowsOf(key), false);
        plan.remove(key, gone);
        return gone;
    }

    /**
     * The Result of a run the plan's check refused: not completed, nothing removed,
     * and the reason that lists why. Nothing was changed, so there is nothing else.
     */
    private static RLM_AccountUtilities.Result refuse(String reason) {
        RLM_AccountUtilities.Result result = new RLM_AccountUtilities.Result();
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
        plan = null;
    }

    @TestVisible
    private static RLM_AccountUtilities.Result finish(Boolean completed, String reason) {
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

        List<String> removed = new List<String>();
        for (String label : report.removedLabels) {
            removed.add(label + ': ' + report.removed.get(label));
        }
        List<String> kept = new List<String>();
        for (Kept k : report.kept) {
            kept.add(k.label + ': ' + k.count + ' (' + k.why + ')');
        }

        RLM_AccountUtilities.Result result = new RLM_AccountUtilities.Result();
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
        if (count == null || count <= 0) {
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
     * True when the org has the object and the running user can read it (describe
     * isAccessible). The plan reads every object in system mode, so its own queries do not
     * depend on this; check() uses it afterwards to count a planned record of an object the
     * user cannot read (CANNOT_READ). Measured live 264 (todo 397, commit 1aa36c4da): as the
     * salesrep persona, the reset's earlier static queries, run in the user's context,
     * failed with "sObject type 'Invoice' is not supported", and isAccessible() was false
     * for exactly the objects whose queries failed; in system mode, a filter through a
     * relationship of such an object was still not understood, which is why the plan's
     * filters use ids.
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
        'PermissionsModifyAllData', 'PermissionsViewAllData', 'PermissionsEditActivatedOrders',
        'PermissionsDeleteActivatedContract'
    };
    // Every permission the plan uses, read at its start, under its query guard.
    private static final List<String> PLAN_PERMISSIONS = new List<String>{
        'PermissionsModifyAllData', 'PermissionsBillingInvoiceSuperUser', 'PermissionsCalmSobjectAccessUser'
    };
    private static final List<String> OTHER_PERMISSIONS = new List<String>{
        'PermissionsBillingInvoiceSuperUser', 'PermissionsCalmSobjectAccessUser'
    };

    /**
     * Whether the running user has the permission, from their profile, a permission set or
     * a group. UserPermissionAccess holds the user's effective permissions, and any user may
     * read their own; a non-admin is refused PermissionSetAssignment.
     */
    @TestVisible
    private static Boolean hasUserPermission(String field) {
        if (withoutPermissionForTest.contains(field)) {
            return false;
        }
        if (userPermissions == null || userPermissionsOf != UserInfo.getUserId()) {
            userPermissionsOf = UserInfo.getUserId();
            userPermissions = new Map<String, Boolean>();
        }
        if (!userPermissions.containsKey(field)) {
            if (CORE_PERMISSIONS.contains(field)) {
                UserPermissionAccess core = [
                    SELECT PermissionsModifyAllData, PermissionsViewAllData, PermissionsEditActivatedOrders,
                        PermissionsDeleteActivatedContract
                    FROM UserPermissionAccess LIMIT 1
                ];
                userPermissions.put('PermissionsModifyAllData', core.PermissionsModifyAllData == true);
                userPermissions.put('PermissionsViewAllData', core.PermissionsViewAllData == true);
                userPermissions.put('PermissionsEditActivatedOrders', core.PermissionsEditActivatedOrders == true);
                userPermissions.put('PermissionsDeleteActivatedContract', core.PermissionsDeleteActivatedContract == true);
            } else {
                // One field per query: a release or org without this field (a Revenue Cloud
                // org without Billing has no BillingInvoiceSuperUser) reads it as false and
                // nothing else.
                List<SObject> access = new List<SObject>();
                try {
                    access = Database.query('SELECT ' + field + ' FROM UserPermissionAccess LIMIT 1');
                } catch (QueryException e) {
                    access = new List<SObject>();
                }
                userPermissions.put(field, !access.isEmpty() && access[0].get(field) == true);
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
     * What blocks deleting an invoice of this status, or null: one still processing, or
     * one not Draft or Canceled for a user without Delete Invoice and Invoice Lines.
     */
    @TestVisible
    private static String invoiceBlocker(String status) {
        String s = status == null ? '' : status;
        if (s.endsWith('In Progress') || s == 'Processing') {
            return INVOICE_IN_PROGRESS;
        }
        if (s != 'Draft' && s != 'Canceled' && !canDeletePostedInvoices()) {
            return INVOICE_NEEDS_PERMISSION;
        }
        return null;
    }

    /** What blocks setting an order of this status back to Draft, or null (live 264). */
    @TestVisible
    private static String orderBlocker(String status) {
        return status != 'Draft' && !hasUserPermission('PermissionsEditActivatedOrders') ? NEEDS_EDIT_ACTIVATED : null;
    }

    /**
     * What blocks deleting a contract of this status, or null. Measured live 264 as the
     * salesrep persona (runAs, rolled back), on an activated contract it owned: without
     * Delete Activated Contracts, UserRecordAccess.HasDeleteAccess was false and the delete
     * was refused ("insufficient access rights on object id"); with it (it depends on
     * Activate Contracts and Delete Contract), both read true and the delete succeeded. A
     * Draft contract it owned was deletable either way. The order flow activates the
     * contracts it creates (RLM_Order_Contract_Creation_and_Association).
     */
    @TestVisible
    private static String contractBlocker(String status) {
        return status == 'Activated' && !hasUserPermission('PermissionsDeleteActivatedContract')
            ? NEEDS_DELETE_ACTIVATED_CONTRACT : null;
    }

    /**
     * What blocks deleting an asset, or null: live 264, a lifecycle-managed asset needs
     * Access Lifecycle-Managed Assets ("You can't delete assets that have Lifecycle
     * Management.").
     */
    @TestVisible
    private static String assetBlocker(Object hasLifecycleManagement) {
        return hasLifecycleManagement == true && !hasUserPermission('PermissionsCalmSobjectAccessUser')
            ? NEEDS_LIFECYCLE : null;
    }

    /**
     * Why a planned record blocks the reset, or null when it does not. One reason per
     * record, in this order: a record the user cannot see is counted as not visible,
     * whatever else applies, so it is never named; then the object's delete permission
     * (for credit memos, Allow Revenue Records Deletion); then a permission the run needs
     * on the record (`special`); then the user's delete access to it.
     */
    @TestVisible
    private static String blockerReason(
        String objectName, Boolean visible, Boolean objectDeletable, String special, Boolean deletable
    ) {
        if (!visible) {
            return NOT_VISIBLE;
        }
        if (!objectDeletable) {
            return objectName == 'CreditMemo' ? MEMO_NEEDS_PERMISSION : NO_PERMISSION;
        }
        if (special != null) {
            return special;
        }
        return deletable ? null : NO_ACCESS;
    }

    // Rows the next DML statement may touch: what is left of the transaction's row
    // budget, or none once all but STATEMENTS_KEPT of its statements are spent, so the
    // rollback always has one.
    @TestVisible
    private static Integer dmlRowsLeft() {
        if (Limits.getDmlStatements() >= Limits.getLimitDmlStatements() - STATEMENTS_KEPT) {
            return 0;
        }
        Integer rowLimit = dmlRowLimitForTest != null ? dmlRowLimitForTest : Limits.getLimitDmlRows();
        return rowLimit - Limits.getDmlRows();
    }

    /**
     * Deletes the rows and records the outcome: rows that went count as removed, and a
     * row a parent's delete already took (ENTITY_IS_DELETED) counts as gone. A refused
     * row is recorded; with `strict`, the first one then throws a RefusedException, which
     * rolls the run back. The rows go in one statement with allOrNone false, so a row a
     * cascade took does not fail the others; the rollback makes the rest all or nothing.
     *
     * The 10,000-row DML limit is per TRANSACTION, not per statement: a statement that
     * would not fit in what is left stops the run with a ResetStoppedException, which
     * rolls it back, rather than a LimitException that fails the flow. The plan's DML
     * check makes that rare: it applies to the statement limit and to rows a cascade adds.
     *
     * @return The ids that are gone, including rows a parent's delete already took
     */
    private static Set<Id> deleteRows(List<SObject> records, Boolean strict) {
        Set<Id> gone = new Set<Id>();
        if (records == null || records.isEmpty()) {
            return gone;
        }
        if (records.size() > dmlRowsLeft()) {
            throw new ResetStoppedException(DML_LIMIT);
        }
        Integer removed = 0;
        Id firstRefused;
        Database.DeleteResult[] results = Database.delete(records, false);
        for (Integer i = 0; i < results.size(); i++) {
            Id rowId = records[i].Id;
            if (results[i].isSuccess()) {
                removed++;
            } else if (results[i].getErrors()[0].getStatusCode() != StatusCode.ENTITY_IS_DELETED) {
                report.refused.put(rowId, results[i].getErrors()[0].getMessage());
                report.refusedCode.put(rowId, String.valueOf(results[i].getErrors()[0].getStatusCode()));
                if (firstRefused == null) {
                    firstRefused = rowId;
                }
                continue;
            }
            gone.add(rowId);
            report.refused.remove(rowId);
            report.refusedCode.remove(rowId);
        }
        recordRemoved(records[0].getSObjectType(), removed);
        if (strict && firstRefused != null) {
            throw new RefusedException(refusalOf(firstRefused));
        }
        return gone;
    }

    /** All-or-nothing delete: a refused row rolls the run back. */
    private static void deleteAll(List<SObject> records) {
        deleteRows(records, true);
    }

    /**
     * All-or-nothing update, for a change made only on the way to a delete (an order set
     * back to Draft, a credit memo canceled): a refusal throws and rolls the run back.
     */
    private static void updateAll(List<SObject> records) {
        if (records.isEmpty()) {
            return;
        }
        if (records.size() > dmlRowsLeft()) {
            throw new ResetStoppedException(DML_LIMIT);
        }
        try {
            Database.update(records, true);
        } catch (DmlException e) {
            throw new RefusedException(dmlFailure(e));
        }
    }

    /**
     * Maps each file linked to the given records to the records it is linked to,
     * leaving out files that are also linked anywhere else (to avoid deleting
     * files shared with Opportunities, Orders, etc.). Two queries however many
     * records there are.
     */
    @TestVisible
    private static Map<Id, Set<Id>> exclusiveFiles(Set<Id> parentIds) {
        Map<Id, Set<Id>> parentsByFile = new Map<Id, Set<Id>>();
        if (parentIds.isEmpty()) {
            return parentsByFile;
        }
        // Bounded like the plan's other reads: reaching the bound ends the plan.
        Integer rowCap = readCap();
        // In system mode, so a link to a record the user cannot see still counts: a file
        // shared with such a record is not exclusive.
        for (ContentDocumentLink cdl : [
            SELECT ContentDocumentId, LinkedEntityId FROM ContentDocumentLink WHERE LinkedEntityId IN :parentIds
            WITH SYSTEM_MODE LIMIT :rowCap
        ]) {
            rowCap--;
            if (!parentsByFile.containsKey(cdl.ContentDocumentId)) {
                parentsByFile.put(cdl.ContentDocumentId, new Set<Id>());
            }
            parentsByFile.get(cdl.ContentDocumentId).add(cdl.LinkedEntityId);
        }
        if (parentsByFile.isEmpty()) {
            return parentsByFile;
        }

        if (rowCap <= 0) {
            throw new PlanTooLargeException(PLAN_TOO_LARGE);
        }
        Set<Id> fileIds = new Set<Id>(parentsByFile.keySet());
        rowCap = readCap();
        for (ContentDocumentLink cdl : [
            SELECT ContentDocumentId, LinkedEntityId, ShareType FROM ContentDocumentLink
            WHERE ContentDocumentId IN :fileIds
            WITH SYSTEM_MODE LIMIT :rowCap
        ]) {
            rowCap--;
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
        if (rowCap <= 0) {
            throw new PlanTooLargeException(PLAN_TOO_LARGE);
        }
        return parentsByFile;
    }

    /**
     * The rows the next read may return: the query rows left, and what the heap left can
     * hold (about 500 bytes a row, as read), so the read can neither throw the
     * uncatchable row limit nor fill the heap. A read that returns this many rows ends the
     * plan.
     */
    private static Integer readCap() {
        Integer rowsLeft = Limits.getLimitQueryRows() - Limits.getQueryRows();
        Integer heapRows = (Limits.getLimitHeapSize() - Limits.getHeapSize()) / 500;
        return Math.max(0, Math.min(rowsLeft, heapRows));
    }

    /** The record that blocks the reset for one reason, of one object. */
    /**
     * The refusal, from the blockers and their description, with the advice that fits each
     * kind of blocker: a permission or record access another user has (REFUSED_ADVICE); an
     * invoice still processing, which nobody can delete until it finishes (NOT_YET_ADVICE,
     * and its own wording when it is the only blocker); an asset or order another account's
     * entitlement still refers to, which no permission or reassignment fixes.
     */
    @TestVisible
    private static String refusal(List<Blocker> blockers, String described) {
        Boolean access = false;
        Boolean waiting = false;
        Boolean assetKept = false;
        Boolean orderKept = false;
        for (Blocker b : blockers) {
            if (b.reason == INVOICE_IN_PROGRESS) {
                waiting = true;
            } else if (b.reason == ASSET_ENTITLEMENT_KEPT) {
                assetKept = true;
            } else if (b.reason == ORDER_LINE_ENTITLEMENT_KEPT) {
                orderKept = true;
            } else {
                access = true;
            }
        }
        Boolean waitingOnly = waiting && !access && !assetKept && !orderKept;
        List<String> advice = new List<String>();
        if (access) {
            advice.add(REFUSED_ADVICE);
        }
        if (assetKept) {
            advice.add(ASSET_KEPT_ADVICE);
        }
        if (orderKept) {
            advice.add(ORDER_KEPT_ADVICE);
        }
        if (waiting) {
            advice.add(NOT_YET_ADVICE);
        }
        return (waitingOnly ? NOT_YET : REFUSED) + ' ' + described + '. ' + String.join(advice, ' ');
    }

    @TestVisible
    private class Blocker {
        public String label;
        public String reason;
        public Integer count = 0;
        // Names of the records the user can see; none for the rest.
        public List<String> names = new List<String>();
    }

    /**
     * The deletion plan (see the class header): for each group of records the run
     * deletes, the exact rows, read in system mode with one set of filters, and the
     * check of those rows.
     *
     * Every row is read whoever runs the reset. The check then records a Blocker for
     * each planned row the user could not delete:
     *  - in an object the user cannot read: counted (CANNOT_READ);
     *  - not visible to the user, or no UserRecordAccess row for it: counted (NOT_VISIBLE);
     *  - visible, but in an object the user may not delete (NO_PERMISSION, or
     *    MEMO_NEEDS_PERMISSION for credit memos), not deletable by the user (NO_ACCESS),
     *    or needing a permission the user lacks: named.
     * A user with Modify All Data and View All Data can see and delete every record, so
     * for them the per-record access reads are skipped; the object and permission checks
     * still run. A record is named only when the user can see it.
     *
     * Budget: each read first requires a query to spare beyond REFRESH_RESERVE
     * (requireQuery) and is bounded by the query rows and heap left (readCap); either
     * running out ends the plan with PlanTooLargeException, before anything changes.
     */
    @TestVisible
    private without sharing class Plan {

        public List<Blocker> blockers = new List<Blocker>();
        // The names of the planned records the user can see, for a refusal's message.
        public Map<Id, String> visibleNames = new Map<Id, String>();
        // Not deleted by design, counted for the Result.
        public Integer foreignBuckets = 0;
        // The account's entitlement accounts above a kept bucket, and its entitlements a
        // kept bucket holds: neither can be deleted while the bucket is there.
        public Integer keptEntitlementAccounts = 0;
        public Integer keptEntitlements = 0;
        // The account's assets a kept entitlement is bound to.
        public Set<Id> assetsOfKeptEntitlements = new Set<Id>();
        public Integer payments = 0;
        public Integer lockedDebitMemos = 0;
        public Map<String, Integer> creditMemosByOtherStatus = new Map<String, Integer>();

        private Map<String, List<SObject>> rows = new Map<String, List<SObject>>();
        private Map<String, String> objectOfGroup = new Map<String, String>();
        private Map<String, Blocker> blockerByKey = new Map<String, Blocker>();
        private Map<String, String> nameFields = new Map<String, String>();
        private Map<String, Object> binds = new Map<String, Object>();
        private Boolean privileged;
        private Id accountId;

        public Plan(
            Id accountId, Boolean deleteAssets, Boolean deleteFulfillment, Boolean deleteBilling,
            Boolean deleteCollections, Boolean preserveContractsWithPrices
        ) {
            this.accountId = accountId;
            // Every permission first, under the query guard: one query for the core ones
            // and one per other permission.
            requireQuery(1 + PLAN_PERMISSIONS.size());
            for (String permission : PLAN_PERMISSIONS) {
                hasUserPermission(permission);
            }
            privileged = hasUserPermission('PermissionsModifyAllData') && hasUserPermission('PermissionsViewAllData');
            binds.put('accountId', accountId);

            // ---------------------------------------------------- assets and contracts
            Boolean lifecycleField = typeOf('Asset').getDescribe().fields.getMap().containsKey('haslifecyclemanagement');
            List<SObject> assets = read('Asset', lifecycleField ? ', HasLifecycleManagement' : '',
                'AccountId = :accountId');
            Set<Id> assetIds = ids(assets);
            binds.put('assetIds', assetIds);
            List<SObject> contracts = read('Contract', ', Status', 'AccountId = :accountId');
            Set<Id> contractIds = ids(contracts);
            binds.put('contractIds', contractIds);
            if (preserveContractsWithPrices && typeOf('ContractItemPrice') != null && !contracts.isEmpty()) {
                // The priced contracts by a semi-join, as the engine reads them: one row a
                // contract, however many contracted prices it has.
                Set<Id> priced = ids(query('Contract', 'Id',
                    'Id IN :contractIds AND Id IN (SELECT ContractId FROM ContractItemPrice)'));
                List<SObject> deleted = new List<SObject>();
                for (SObject contract : contracts) {
                    if (!priced.contains(contract.Id)) {
                        deleted.add(contract);
                    }
                }
                contracts = deleted;
            }
            put(G_CONTRACTS, 'Contract', contracts);
            for (SObject contract : contracts) {
                String reason = contractBlocker((String) contract.get('Status'));
                if (reason != null) {
                    special('Contract', reason, contract);
                }
            }
            binds.put('deletedContractIds', ids(contracts));

            // ---------------------------------------------------- usage (deleted first)
            // Binding policies of the account, of the contracts the run deletes and, with
            // Delete Assets, of the assets: a kept contract or asset keeps its policies.
            Set<Id> bindingIds = new Set<Id>(ids(contracts));
            if (deleteAssets) {
                bindingIds.addAll(assetIds);
            }
            bindingIds.add(accountId);
            binds.put('bindingIds', bindingIds);
            put(G_POLICIES, 'BindingObjUsageRsrcPlcy',
                read('BindingObjUsageRsrcPlcy', '', 'BindingObjectId IN :bindingIds'));
            List<SObject> accountEntries = new List<SObject>();
            List<SObject> contractEntries = new List<SObject>();
            for (SObject entry : read('BindingObjectRateCardEntry', ', BindingObjectId',
                'BindingObjectId = :accountId OR BindingObjectId IN :deletedContractIds')) {
                if (entry.get('BindingObjectId') == accountId) {
                    accountEntries.add(entry);
                } else {
                    contractEntries.add(entry);
                }
            }
            // The account's with the usage; a contract's with the contract.
            put(G_ACCOUNT_RATE_CARD_ENTRIES, 'BindingObjectRateCardEntry', accountEntries);
            put(G_CONTRACT_RATE_CARD_ENTRIES, 'BindingObjectRateCardEntry', contractEntries);
            String byAccountOrAsset = 'AccountId = :accountId OR AssetId IN :assetIds';
            put(G_BILLING_PERIOD_ITEMS, 'UsageBillingPeriodItem',
                read('UsageBillingPeriodItem', '', byAccountOrAsset));
            put(G_SUMMARIES, 'UsageSummary', read('UsageSummary', '', byAccountOrAsset));
            put(G_RATABLE_SUMMARIES, 'UsageRatableSummary', read('UsageRatableSummary', '', byAccountOrAsset));
            List<SObject> journals = read('TransactionJournal', '', 'AccountId = :accountId');
            put(G_JOURNALS, 'TransactionJournal', journals);
            // A record alert on a journal blocks the journal's delete (measured live 264:
            // "associated with the following record alerts"), so it goes first.
            List<SObject> journalAlerts = new List<SObject>();
            if (!journals.isEmpty() && typeOf('RecordAlert') != null) {
                binds.put('journalIds', ids(journals));
                journalAlerts = read('RecordAlert', '', 'WhatId IN :journalIds OR ParentId IN :journalIds');
            }
            put(G_JOURNAL_ALERTS, 'RecordAlert', journalAlerts);
            List<SObject> ownEntitlements = read('TransactionUsageEntitlement', ', AssetId, GrantBindingTargetId',
                'AccountId = :accountId');
            put(G_ENTITLEMENTS, 'TransactionUsageEntitlement', ownEntitlements);
            // Another account's entitlement bound to an asset this reset deletes goes with
            // the asset.
            List<SObject> assetEntitlements = new List<SObject>();
            if (deleteAssets && !assetIds.isEmpty()) {
                assetEntitlements = read('TransactionUsageEntitlement', ', AssetId, GrantBindingTargetId',
                    '(AssetId IN :assetIds OR GrantBindingTargetId IN :assetIds) AND AccountId != :accountId');
            }
            put(G_ASSET_ENTITLEMENTS, 'TransactionUsageEntitlement', assetEntitlements);
            Set<Id> ownTueIds = ids(ownEntitlements);
            Set<Id> assetTueIds = ids(assetEntitlements);
            List<SObject> entitlementAccounts = read('UsageEntitlementAccount', '', 'AccountId = :accountId');
            put(G_ENTITLEMENT_ACCOUNTS, 'UsageEntitlementAccount', entitlementAccounts);
            Set<Id> allTueIds = new Set<Id>(ownTueIds);
            allTueIds.addAll(assetTueIds);
            binds.put('tueIds', allTueIds);
            List<SObject> entries = allTueIds.isEmpty() ? new List<SObject>() : read('UsageEntitlementEntry',
                ', TransactionUsageEntitlementId', 'TransactionUsageEntitlementId IN :tueIds');
            put(G_ENTRIES, 'UsageEntitlementEntry', byEntitlement(entries, ownTueIds, true));
            put(G_ASSET_ENTRIES, 'UsageEntitlementEntry', byEntitlement(entries, ownTueIds, false));
            planBuckets(ids(entitlementAccounts), ownTueIds, assetTueIds, deleteAssets ? assetIds : new Set<Id>());
            put(G_COMMITMENT_JUNCTIONS, 'UsageCmtAssetRelatedObj', assetIds.isEmpty() ? new List<SObject>()
                : read('UsageCmtAssetRelatedObj', '', 'AssetId IN :assetIds OR RelatedObjectId IN :assetIds'));

            // ---------------------------------------------------- assets
            if (deleteAssets) {
                put(G_ASSETS, 'Asset', assets);
                for (SObject asset : assets) {
                    if (assetsOfKeptEntitlements.contains(asset.Id)) {
                        special('Asset', ASSET_ENTITLEMENT_KEPT, asset);
                    }
                }
                if (lifecycleField) {
                    for (SObject asset : assets) {
                        String reason = assetBlocker(asset.get('HasLifecycleManagement'));
                        if (reason != null) {
                            special('Asset', reason, asset);
                        }
                    }
                }
                if (!assetIds.isEmpty()) {
                    put(G_ASSET_RATE_CARD_ENTRIES, 'AssetRateCardEntry',
                        read('AssetRateCardEntry', '', 'AssetId IN :assetIds'));
                    // Binding rate card entries sourced from an asset block its delete
                    // (measured live 264: "associated with the following binding object rate
                    // card entries"), whatever they are bound to, so they go with it; those
                    // of the account and of deleted contracts are planned already.
                    Set<Id> plannedEntries = new Set<Id>(ids(rowsOf(G_ACCOUNT_RATE_CARD_ENTRIES)));
                    plannedEntries.addAll(ids(rowsOf(G_CONTRACT_RATE_CARD_ENTRIES)));
                    binds.put('plannedEntries', plannedEntries);
                    put(G_ASSET_SOURCED_RATE_CARD_ENTRIES, 'BindingObjectRateCardEntry', read('BindingObjectRateCardEntry',
                        '', 'SourceAssetId IN :assetIds AND Id NOT IN :plannedEntries'));
                    put(G_ASSET_RELATIONSHIPS, 'AssetRelationship',
                        read('AssetRelationship', '', 'AssetId IN :assetIds OR RelatedAssetId IN :assetIds'));
                    put(G_WORK_ORDERS, 'WorkOrder', readByAsset('WorkOrder'));
                    put(G_ASSET_CASES, 'Case', readByAsset('Case'));
                }
            }

            put(G_SCHEDULE_GROUPS, 'BillingScheduleGroup',
                read('BillingScheduleGroup', '', 'BillingAccountId = :accountId'));

            // ---------------------------------------------------- orders
            List<SObject> orders = read('Order', ', Status', 'AccountId = :accountId');
            put(G_ORDERS, 'Order', orders);
            for (SObject o : orders) {
                String reason = orderBlocker((String) o.get('Status'));
                if (reason != null) {
                    special('Order', reason, o);
                }
            }
            Set<Id> orderIds = ids(orders);
            binds.put('orderIds', orderIds);
            // An order line that a usage entitlement refers to (OrderItemId) cannot be
            // deleted, nor its order (measured live 264: "associated with the following
            // transaction usage entitlements"), even when the entitlement is another
            // account's. Every entitlement the plan deletes goes before the orders (the usage
            // teardown); any other is kept, so its order is named and the run refused.
            Set<Id> orderItemIds = new Set<Id>();
            if (!orderIds.isEmpty()) {
                Map<Id, Id> orderOfLine = new Map<Id, Id>();
                for (SObject line : query('OrderItem', 'Id, OrderId', 'OrderId IN :orderIds')) {
                    orderOfLine.put(line.Id, (Id) line.get('OrderId'));
                }
                orderItemIds = orderOfLine.keySet();
                binds.put('orderItemIds', orderItemIds);
                Set<Id> entitlementsFirst = new Set<Id>(ids(rowsOf(G_ENTITLEMENTS)));
                entitlementsFirst.addAll(ids(rowsOf(G_ASSET_ENTITLEMENTS)));
                binds.put('entitlementsFirst', entitlementsFirst);
                Set<Id> blockedOrders = new Set<Id>();
                if (!orderItemIds.isEmpty()) {
                    for (SObject entitlement : query('TransactionUsageEntitlement', 'Id, OrderItemId',
                        'OrderItemId IN :orderItemIds AND Id NOT IN :entitlementsFirst')) {
                        blockedOrders.add(orderOfLine.get((Id) entitlement.get('OrderItemId')));
                    }
                }
                for (SObject o : orders) {
                    if (blockedOrders.contains(o.Id)) {
                        special('Order', ORDER_LINE_ENTITLEMENT_KEPT, o);
                    }
                }
            }

            // ---------------------------------------------------- billing
            List<SObject> invoices = new List<SObject>();
            if (deleteBilling || deleteCollections || deleteFulfillment) {
                invoices = read('Invoice', ', Status, PaymentScheduleId', 'BillingAccountId = :accountId');
            }
            Set<Id> invoiceIds = ids(invoices);
            binds.put('invoiceIds', invoiceIds);
            Set<Id> documentParents = new Set<Id>();
            if (deleteBilling) {
                put(G_INVOICES, 'Invoice', invoices);
                documentParents.addAll(invoiceIds);
                Set<Id> scheduleIds = new Set<Id>();
                for (SObject inv : invoices) {
                    String reason = invoiceBlocker((String) inv.get('Status'));
                    if (reason != null) {
                        special('Invoice', reason, inv);
                    }
                    if (inv.get('PaymentScheduleId') != null) {
                        scheduleIds.add((Id) inv.get('PaymentScheduleId'));
                    }
                }
                binds.put('scheduleIds', scheduleIds);
                put(G_INVOICE_SCHEDULES, 'PaymentSchedule', scheduleIds.isEmpty() ? new List<SObject>()
                    : read('PaymentSchedule', '', 'Id IN :scheduleIds'));
                List<SObject> debitMemos = new List<SObject>();
                if (typeOf('DebitMemo') != null) {
                    for (SObject memo : read('DebitMemo', ', Status', 'AccountId = :accountId')) {
                        if (memo.get('Status') == 'Posted' || memo.get('Status') == 'Void') {
                            lockedDebitMemos++;
                        } else {
                            debitMemos.add(memo);
                        }
                    }
                }
                put(G_DEBIT_MEMOS, 'DebitMemo', debitMemos);
                List<SObject> creditMemos = new List<SObject>();
                for (SObject memo : read('CreditMemo', ', Status', 'BillingAccountId = :accountId')) {
                    String status = (String) memo.get('Status');
                    if (status == 'Draft' || status == 'Canceled' || status == 'Posted') {
                        creditMemos.add(memo);
                    } else {
                        Integer soFar = creditMemosByOtherStatus.containsKey(status) ? creditMemosByOtherStatus.get(status) : 0;
                        creditMemosByOtherStatus.put(status, soFar + 1);
                    }
                }
                put(G_CREDIT_MEMOS, 'CreditMemo', creditMemos);
                payments = count('Payment', 'AccountId = :accountId');
            }

            // ---------------------------------------------------- collections
            if (deleteCollections) {
                List<SObject> plans = read('CollectionPlan', '', 'AccountId = :accountId');
                put(G_COLLECTION_PLANS, 'CollectionPlan', plans);
                Set<Id> planIds = ids(plans);
                binds.put('planIds', planIds);
                // A case can be both a plan's and a dispute's; put() keeps it once.
                List<SObject> collectionCases = new List<SObject>();
                if (!planIds.isEmpty()) {
                    // Plan items go with their plan; their ids find promise-to-pay schedules.
                    binds.put('planItemIds', ids(query('CollectionPlanItem', '', 'CollectionPlanId IN :planIds')));
                    put(G_PLAN_SCHEDULES, 'PaymentSchedule', read('PaymentSchedule', '',
                        'ReferenceEntityId IN :planIds OR CollectionPlanItemId IN :planItemIds'));
                    for (SObject planCase : read('Case', ', SourceId', 'SourceId IN :planIds AND AccountId = :accountId')) {
                        collectionCases.add(planCase);
                    }
                }
                if (typeOf('Dispute') != null) {
                    List<SObject> disputes = read('Dispute', ', CaseId',
                        'AccountId = :accountId OR InvoiceId IN :invoiceIds');
                    put(G_DISPUTES, 'Dispute', disputes);
                    Set<Id> disputeCaseIds = new Set<Id>();
                    for (SObject dispute : disputes) {
                        if (dispute.get('CaseId') != null) {
                            disputeCaseIds.add((Id) dispute.get('CaseId'));
                        }
                    }
                    if (!disputeCaseIds.isEmpty()) {
                        binds.put('disputeCaseIds', disputeCaseIds);
                        collectionCases.addAll(read('Case', '', 'Id IN :disputeCaseIds AND AccountId = :accountId'));
                    }
                }
                put(G_COLLECTION_CASES, 'Case', collectionCases);
            }

            // ---------------------------------------------------- fulfillment
            if (deleteFulfillment) {
                binds.put('orderItemIds', orderItemIds);
                Set<String> sourceIds = new Set<String>();
                for (Id sourceId : orderItemIds) {
                    sourceIds.add(sourceId);
                }
                for (Id sourceId : orderIds) {
                    sourceIds.add(sourceId);
                }
                binds.put('sourceIds', sourceIds);
                binds.put('summaryIds', ids(query('OrderSummary', '', 'AccountId = :accountId')));
                List<SObject> fulfillmentOrders = read('FulfillmentOrder', '', 'AccountId = :accountId '
                    + 'OR OrderId IN :orderIds OR InvoiceId IN :invoiceIds OR OrderSummaryId IN :summaryIds');
                put(G_FULFILLMENT_ORDERS, 'FulfillmentOrder', fulfillmentOrders);
                binds.put('fulfillmentOrderIds', ids(fulfillmentOrders));
                List<SObject> lines = read('FulfillmentOrderLineItem', '', 'FulfillmentOrderId IN :fulfillmentOrderIds');
                put(G_FULFILLMENT_ORDER_LINES, 'FulfillmentOrderLineItem', lines);
                binds.put('lineIds', ids(lines));
                List<SObject> fulfillmentPlans = read('FulfillmentPlan', '', 'SourceIdentifier IN :sourceIds '
                    + 'AND (SourceType = \'StandardOrder\' OR SourceType = \'OrderItem\')');
                put(G_FULFILLMENT_PLANS, 'FulfillmentPlan', fulfillmentPlans);
                binds.put('fulfillmentPlanIds', ids(fulfillmentPlans));
                binds.put('stepIds', ids(query('FulfillmentStep', '', 'FulfillmentPlanId IN :fulfillmentPlanIds')));
                put(G_STEP_SOURCES, 'FulfillmentStepSource',
                    read('FulfillmentStepSource', '', 'StepId IN :stepIds OR SourceLineItemId IN :orderItemIds'));
                List<SObject> fulfillmentAssets = read('FulfillmentAsset', '', 'AccountId = :accountId');
                put(G_FULFILLMENT_ASSETS, 'FulfillmentAsset', fulfillmentAssets);
                binds.put('fulfillmentAssetIds', ids(fulfillmentAssets));
                put(G_DECOMPOSITIONS, 'AssetFulfillmentDecomp', read('AssetFulfillmentDecomp', '',
                    'FulfillmentSourceAssetId IN :fulfillmentAssetIds OR FulfillmentTargetAssetId IN :fulfillmentAssetIds'));
                put(G_LINE_SOURCE_RELATIONS, 'FulfillmentLineSourceRel', read('FulfillmentLineSourceRel', '',
                    'SourceLineItemId IN :orderItemIds OR FulfilmentOrderLineId IN :lineIds'));
            }

            // ---------------------------------------------------- quotes, opportunities, documents
            // QuoteAccountId is the quote's own account and AccountId its opportunity's;
            // a quote can have either alone.
            List<SObject> quotes = read('Quote', '', 'QuoteAccountId = :accountId OR AccountId = :accountId');
            put(G_QUOTES, 'Quote', quotes);
            put(G_OPPORTUNITIES, 'Opportunity', read('Opportunity', '', 'AccountId = :accountId'));
            documentParents.addAll(ids(quotes));
            // DocumentGenerationProcess rows name their record in a text field, so nothing
            // cascades them; files are found through their links, and only those linked to
            // nothing else go.
            List<SObject> invoiceDocuments = new List<SObject>();
            List<SObject> quoteDocuments = new List<SObject>();
            if (!documentParents.isEmpty() && typeOf('DocumentGenerationProcess') != null) {
                Set<String> references = new Set<String>();
                for (Id parentId : documentParents) {
                    references.add(parentId);
                }
                binds.put('references', references);
                for (SObject document : read('DocumentGenerationProcess', ', ReferenceObject',
                    'ReferenceObject IN :references')) {
                    Id reference = Id.valueOf((String) document.get('ReferenceObject'));
                    if (invoiceIds.contains(reference) && deleteBilling) {
                        invoiceDocuments.add(document);
                    } else {
                        quoteDocuments.add(document);
                    }
                }
            }
            put(G_INVOICE_DOCUMENTS, 'DocumentGenerationProcess', invoiceDocuments);
            put(G_QUOTE_DOCUMENTS, 'DocumentGenerationProcess', quoteDocuments);
            List<SObject> files = new List<SObject>();
            if (!documentParents.isEmpty()) {
                requireQuery(2);
                Set<Id> fileIds = exclusiveFiles(documentParents).keySet();
                binds.put('fileIds', fileIds);
                if (!fileIds.isEmpty()) {
                    files = read('ContentDocument', ', OwnerId', 'Id IN :fileIds');
                }
            }
            put(G_FILES, 'ContentDocument', files);

            check();
        }

        /**
         * The account's buckets: those holding its entitlements (and, with Delete Assets,
         * those bound to its assets) or under its entitlement accounts, and every
         * descendant, a level per query, however deep. A bucket holding another account's
         * entitlement, and every bucket above it, is never deleted: a reset never touches
         * another account's data. Those are counted (foreignBuckets) and left out, and so
         * are the account's entitlement accounts directly above one and its entitlements
         * one holds (keptEntitlementAccounts, keptEntitlements): the platform refuses to
         * delete either while the bucket is there. Buckets holding an entitlement bound to
         * an asset go with the asset.
         */
        private void planBuckets(Set<Id> entitlementAccountIds, Set<Id> ownTueIds, Set<Id> assetTueIds, Set<Id> assetIds) {
            Set<Id> roots = new Set<Id>(entitlementAccountIds);
            Set<Id> heldBy = new Set<Id>(ownTueIds);
            heldBy.addAll(assetTueIds);
            Map<Id, SObject> buckets = new Map<Id, SObject>();
            if (!roots.isEmpty() || !heldBy.isEmpty()) {
                binds.put('bucketParents', roots);
                binds.put('heldBy', heldBy);
                buckets.putAll(read('UsageEntitlementBucket', ', ParentId, TransactionUsageEntitlementId',
                    'ParentId IN :bucketParents OR TransactionUsageEntitlementId IN :heldBy'));
                Set<Id> frontier = new Set<Id>(buckets.keySet());
                while (!frontier.isEmpty()) {
                    binds.put('bucketParents', frontier);
                    binds.put('knownBuckets', new Set<Id>(buckets.keySet()));
                    frontier = new Set<Id>();
                    for (SObject child : read('UsageEntitlementBucket', ', ParentId, TransactionUsageEntitlementId',
                        'ParentId IN :bucketParents AND Id NOT IN :knownBuckets')) {
                        buckets.put(child.Id, child);
                        frontier.add(child.Id);
                    }
                }
            }
            // An entitlement held by a bucket but not in the plan's lists is another
            // account's: the plan read all of the account's.
            Set<Id> foreign = new Set<Id>();
            for (SObject bucket : buckets.values()) {
                Id held = (Id) bucket.get('TransactionUsageEntitlementId');
                if (held == null || heldBy.contains(held)) {
                    continue;
                }
                SObject up = bucket;
                while (up != null && foreign.add(up.Id)) {
                    up = buckets.get((Id) up.get('ParentId'));
                }
            }
            foreignBuckets = foreign.size();
            Set<Id> holders = new Set<Id>();
            for (Id bucketId : foreign) {
                SObject bucket = buckets.get(bucketId);
                Id held = (Id) bucket.get('TransactionUsageEntitlementId');
                if (held != null && heldBy.contains(held)) {
                    holders.add(held);
                }
                Id parent = (Id) bucket.get('ParentId');
                if (parent != null && parent.getSObjectType() == UsageEntitlementAccount.SObjectType) {
                    holders.add(parent);
                }
            }
            // An asset that a kept entitlement is bound to cannot be deleted while the
            // entitlement is there: with Delete Assets, the check refuses the run for it.
            List<SObject> entitlements = new List<SObject>(rowsOf(G_ENTITLEMENTS));
            entitlements.addAll(rowsOf(G_ASSET_ENTITLEMENTS));
            for (SObject entitlement : entitlements) {
                if (holders.contains(entitlement.Id)) {
                    for (String field : new List<String>{ 'AssetId', 'GrantBindingTargetId' }) {
                        Id bound = (Id) entitlement.get(field);
                        if (bound != null && assetIds.contains(bound)) {
                            assetsOfKeptEntitlements.add(bound);
                        }
                    }
                }
            }
            Integer accountsBefore = rowsOf(G_ENTITLEMENT_ACCOUNTS).size();
            Integer entitlementsBefore = rowsOf(G_ENTITLEMENTS).size() + rowsOf(G_ASSET_ENTITLEMENTS).size();
            remove(G_ENTITLEMENT_ACCOUNTS, holders);
            remove(G_ENTITLEMENTS, holders);
            remove(G_ASSET_ENTITLEMENTS, holders);
            keptEntitlementAccounts = accountsBefore - rowsOf(G_ENTITLEMENT_ACCOUNTS).size();
            keptEntitlements = entitlementsBefore - rowsOf(G_ENTITLEMENTS).size() - rowsOf(G_ASSET_ENTITLEMENTS).size();
            List<SObject> own = new List<SObject>();
            List<SObject> withAssets = new List<SObject>();
            for (SObject bucket : buckets.values()) {
                if (foreign.contains(bucket.Id)) {
                    continue;
                }
                if (assetTueIds.contains((Id) bucket.get('TransactionUsageEntitlementId'))) {
                    withAssets.add(bucket);
                } else {
                    own.add(bucket);
                }
            }
            put(G_BUCKETS, 'UsageEntitlementBucket', own);
            put(G_ASSET_BUCKETS, 'UsageEntitlementBucket', withAssets);
        }

        private List<SObject> byEntitlement(List<SObject> entries, Set<Id> ownTueIds, Boolean own) {
            List<SObject> selected = new List<SObject>();
            for (SObject entry : entries) {
                if (ownTueIds.contains((Id) entry.get('TransactionUsageEntitlementId')) == own) {
                    selected.add(entry);
                }
            }
            return selected;
        }

        /**
         * The work orders or cases that reference the assets. Only the query can tell
         * whether the org has AssetId on them: live 264, Case.AssetId was missing from
         * the org although describe listed it. Without the column, none reference them.
         */
        private List<SObject> readByAsset(String objectName) {
            if (typeOf(objectName) == null) {
                return new List<SObject>();
            }
            try {
                return read(objectName, '', 'AssetId IN :assetIds');
            } catch (QueryException e) {
                if (!e.getMessage().contains('No such column')) {
                    throw e;
                }
                return new List<SObject>();
            }
        }

        /** Reads `objectName`'s records matching `filter`, with its name field, in system mode. */
        private List<SObject> read(String objectName, String extraFields, String filter) {
            if (typeOf(objectName) == null) {
                return new List<SObject>();
            }
            String nameField = nameFieldOf(objectName);
            return query(objectName, 'Id' + (nameField == null ? '' : ', ' + nameField) + extraFields, filter);
        }

        /**
         * One system-mode read. `fields` defaults to Id. The rows and heap left bound it,
         * and reaching that bound ends the plan.
         */
        private List<SObject> query(String objectName, String fields, String filter) {
            if (typeOf(objectName) == null) {
                return new List<SObject>();
            }
            requireQuery(1);
            Integer cap = readCap();
            if (cap <= 0) {
                throw new PlanTooLargeException(PLAN_TOO_LARGE);
            }
            binds.put('rowCap', cap);
            List<SObject> found = Database.queryWithBinds('SELECT ' + (String.isBlank(fields) ? 'Id' : fields)
                + ' FROM ' + objectName + ' WHERE ' + filter + ' LIMIT :rowCap', binds, AccessLevel.SYSTEM_MODE);
            if (found.size() >= cap) {
                throw new PlanTooLargeException(PLAN_TOO_LARGE);
            }
            return found;
        }

        private Integer count(String objectName, String filter) {
            if (typeOf(objectName) == null) {
                return 0;
            }
            requireQuery(1);
            return Database.countQueryWithBinds('SELECT COUNT() FROM ' + objectName + ' WHERE ' + filter, binds,
                AccessLevel.SYSTEM_MODE);
        }

        private void requireQuery(Integer needed) {
            if (Limits.getLimitQueries() - Limits.getQueries() - REFRESH_RESERVE < needed) {
                throw new PlanTooLargeException(PLAN_TOO_LARGE);
            }
        }

        /**
         * A group's rows, each once: a delete list with the same Id twice fails every row
         * of it (measured live 264: DELETE_FAILED "Duplicate id in list"), which would roll
         * the run back.
         */
        private void put(String key, String objectName, List<SObject> records) {
            Map<Id, SObject> unique = new Map<Id, SObject>();
            for (SObject record : records) {
                if (!unique.containsKey(record.Id)) {
                    unique.put(record.Id, record);
                }
            }
            rows.put(key, unique.size() == records.size() ? records : unique.values());
            objectOfGroup.put(key, objectName);
        }

        // Permission blockers found while reading, applied by check() once access is known.
        private List<SObject> specialRows = new List<SObject>();
        private Map<Id, String> specialReason = new Map<Id, String>();
        private Map<Id, String> specialObject = new Map<Id, String>();

        private void special(String objectName, String reason, SObject record) {
            specialRows.add(record);
            specialReason.put(record.Id, reason);
            specialObject.put(record.Id, objectName);
        }

        /**
         * Checks every planned row (see the class comment). Records of objects the user
         * cannot read are counted; for the rest, UserRecordAccess is read (unless the
         * user is privileged), and a record is named only when the user can see it.
         */
        private void check() {
            // Heap for the maps below first: a plan too large to check is refused.
            Integer planned = 0;
            for (List<SObject> records : rows.values()) {
                planned += records.size();
            }
            Integer heapLeft = heapLeftForTest != null ? heapLeftForTest : Limits.getLimitHeapSize() - Limits.getHeapSize();
            if (planned * CHECK_BYTES_PER_ROW > heapLeft) {
                throw new PlanTooLargeException(PLAN_TOO_LARGE);
            }
            Map<Id, String> objectOf = new Map<Id, String>();
            Map<Id, String> nameOf = new Map<Id, String>();
            for (String key : rows.keySet()) {
                String objectName = objectOfGroup.get(key);
                List<SObject> records = rows.get(key);
                if (records.isEmpty()) {
                    continue;
                }
                if (!canRead(objectName)) {
                    blocker(objectName, CANNOT_READ).count += records.size();
                    continue;
                }
                for (SObject record : records) {
                    objectOf.put(record.Id, objectName);
                    nameOf.put(record.Id, nameOf(objectName, record));
                }
            }
            Set<Id> visible = new Set<Id>();
            Set<Id> deletable = new Set<Id>();
            if (privileged) {
                visible.addAll(objectOf.keySet());
                deletable.addAll(objectOf.keySet());
            } else {
                List<Id> recordIds = new List<Id>(objectOf.keySet());
                Id reader = UserInfo.getUserId();
                for (Integer start = 0; start < recordIds.size(); start += ACCESS_BATCH) {
                    requireQuery(1);
                    List<Id> chunk = new List<Id>();
                    for (Integer i = start; i < Math.min(start + ACCESS_BATCH, recordIds.size()); i++) {
                        chunk.add(recordIds[i]);
                    }
                    // Bounded like the plan's reads: one row a record at most.
                    if (readCap() <= chunk.size()) {
                        throw new PlanTooLargeException(PLAN_TOO_LARGE);
                    }
                    for (UserRecordAccess access : [
                        SELECT RecordId, HasReadAccess, HasDeleteAccess FROM UserRecordAccess
                        WHERE UserId = :reader AND RecordId IN :chunk
                    ]) {
                        if (access.HasReadAccess) {
                            visible.add(access.RecordId);
                        }
                        if (access.HasDeleteAccess) {
                            deletable.add(access.RecordId);
                        }
                    }
                }
            }
            // A file: live 264 (runAs the salesrep persona), UserRecordAccess.HasDeleteAccess
            // was false for a file the persona owned, and deleting it succeeded; deleting
            // another user's file was refused. So a file's delete follows its owner.
            Id userId = UserInfo.getUserId();
            for (SObject file : rowsOf(G_FILES)) {
                if (privileged || file.get('OwnerId') == userId) {
                    deletable.add(file.Id);
                } else {
                    deletable.remove(file.Id);
                }
            }
            // One reason per record (blockerReason); a record with no UserRecordAccess row
            // counts as not visible.
            for (Id recordId : objectOf.keySet()) {
                String objectName = objectOf.get(recordId);
                String reason = blockerReason(objectName, visible.contains(recordId), objectDeletable(objectName),
                    specialReason.get(recordId), deletable.contains(recordId));
                if (reason == NOT_VISIBLE) {
                    blocker(objectName, NOT_VISIBLE).count++;
                    continue;
                }
                visibleNames.put(recordId, nameOf.get(recordId));
                if (reason != null) {
                    name(objectName, reason, nameOf.get(recordId));
                }
            }
        }


        private void name(String objectName, String reason, String recordName) {
            Blocker b = blocker(objectName, reason);
            b.count++;
            b.names.add(recordName);
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

        /** The planned rows of a group not deleted yet, or an empty list. */
        public List<SObject> rowsOf(String key) {
            return rows.containsKey(key) ? rows.get(key) : new List<SObject>();
        }

        /** Drops the rows that went from a group. */
        public void remove(String key, Set<Id> gone) {
            if (gone.isEmpty() || !rows.containsKey(key)) {
                return;
            }
            List<SObject> left = rows.get(key).clone();
            left.clear();
            for (SObject record : rows.get(key)) {
                if (!gone.contains(record.Id)) {
                    left.add(record);
                }
            }
            rows.put(key, left);
        }

        /** The orders that are not in Draft, as updates that set them back to it. */
        public List<SObject> ordersToDraft() {
            List<SObject> updates = new List<SObject>();
            for (SObject o : rowsOf(G_ORDERS)) {
                if (o.get('Status') != 'Draft') {
                    updates.add(new Order(Id = o.Id, Status = 'Draft'));
                }
            }
            return updates;
        }

        /** The DML rows the deletes take: every planned row once, and the updates before them. */
        public Integer dmlRows() {
            Integer total = ordersToDraft().size();
            for (String key : rows.keySet()) {
                total += rows.get(key).size();
            }
            for (SObject memo : rowsOf(G_CREDIT_MEMOS)) {
                if (memo.get('Status') == 'Posted') {
                    total++;
                }
            }
            return total;
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
