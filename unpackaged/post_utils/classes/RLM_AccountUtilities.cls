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
 * One deletion plan (todo 397). The run first builds a Plan: for the selected
 * options, the exact records each step deletes or changes, read once, in system
 * mode, with one set of queries and helpers (the bucket tree walk included). The
 * plan is checked before anything changes, and the phases then delete exactly the
 * plan's records and nothing else, so a record cannot be deleted without having
 * been checked, and the check cannot drift from the deletes.
 *
 * The check (owner decision: refuse the whole reset). If the running user could not
 * delete every planned record, nothing is changed and the Result says the reset was
 * not run and lists why: records in an object the user cannot read, or that the
 * user cannot see, are counted; records the user can see are named, with the reason
 * (no delete permission on the object, no delete access to the record, or a
 * permission the run needs on it: Edit Activated Orders, Access Lifecycle-Managed
 * Assets, Delete Invoice and Invoice Lines, Allow Revenue Records Deletion), and
 * invoices still processing are named too. Live 264 (the salesrep persona, under
 * System.runAs and in a Login As session) a query in this class saw only the
 * records sharing showed that user, although the class is declared without
 * sharing, and a delete of a record the user could edit but not delete was
 * refused; that is why the plan is read in system mode and checked per record.
 *
 * When nothing blocks, the run has two phases:
 *  1. The usage graph, BEFORE the savepoint, so its progress survives a later
 *     failure: binding policies, the account's own rate card entries, usage
 *     summaries, entitlements and their buckets, rated journals and commitment
 *     junctions. The constraints between them are circular, so the planned rows
 *     are retried round after round until a round removes nothing.
 *  2. Everything else, inside a savepoint: collections, billing, fulfillment,
 *     contracts (with their rate card entries), orders, assets (with their rate card
 *     entries, relationships, bound entitlements, work orders and cases), quotes and
 *     opportunities. If any of it fails, all of it rolls back and the Result says
 *     why. Orders (set back to Draft), credit memos (canceled), invoices, contracts,
 *     assets, quotes and opportunities go all or nothing; the rest best-effort, a
 *     refused row reported with the platform's message.
 *
 * Only the plan reads data, so the query budget is the plan's: each of its reads
 * first requires a query to spare, and each is bounded by the rows left, so an
 * account too large to plan stops cleanly before anything changes. Every delete is
 * clamped to the DML rows left (deleteRows); running short ends the run with a
 * Result that asks for another run.
 *
 * ⚠ Sharing: `without sharing`, declared deliberately rather than left implicit.
 * The invocable's job is to clear an account's ENTIRE related graph so a demo
 * account can be rebuilt, and that graph routinely contains records owned by
 * other users — the integration user, an admin, another persona. A reset that
 * deleted only the records its user could see would silently leave the rest,
 * producing a half-reset account that looks successful: worse than refusing,
 * which is what the check now does. The repo's Apex rules permit `without
 * sharing` for exactly this case provided the reason is documented, which is
 * what this note is. Access is controlled at the grant: the class is reachable
 * only through RLM_UtilitiesPermset, which is assigned deliberately and kept
 * separate from the component permission sets for this reason. The Plan inner
 * class declares `without sharing` itself: an inner class does not take the outer
 * class's keyword, and AccessLevel.SYSTEM_MODE leaves record sharing to it.
 *
 * @author John Rozsits, Brian Galdino, Anthropic Claude 4 Sonnet
 * @date 2025-06-10
 */
public without sharing class RLM_AccountUtilities {
    // Usage teardown. The graph has circular delete constraints (a ratable summary
    // can be held by a usage summary and vice versa, a bucket by its children), so
    // phase 1 retries the planned rows round after round and stops when a round
    // removes nothing. Six rounds has been ample; the cap only exists so a
    // pathological graph cannot spin. A round runs no queries.
    private static final Integer MAX_TEARDOWN_ROUNDS = 6;
    // Rows the plan reads per usage object in one run. More than this and the run
    // deletes what it planned and asks for another run, which plans the rest. For a user
    // without Modify All Data and View All Data the batch is smaller, so the per-record
    // access reads (200 ids a query) for eleven usage objects fit in the queries left:
    // eleven batches of 400 take 22 reads.
    private static final Integer TEARDOWN_BATCH = 2000;
    private static final Integer CHECKED_TEARDOWN_BATCH = 400;
    // Lets a test shrink the usage batch, to prove a run that reads only part of the usage converges.
    @TestVisible
    private static Integer usageBatchForTest;
    // Ids per UserRecordAccess read: the most it accepts.
    private static final Integer ACCESS_BATCH = 200;
    // Names listed per object and reason in a refusal; the rest are counted.
    private static final Integer NAMES_LISTED = 5;

    private static final String RUN_AGAIN = 'Run the reset again; it continues from where this run stopped.';
    private static final String USAGE_TOO_LARGE = 'The account has more usage records than one run can remove.';
    private static final String FOREIGN_BUCKET = 'kept: holds, or is above, another account\'s entitlement';
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
    private static final String PLAN_TOO_LARGE = 'The reset was not run, and nothing was changed: the account has '
        + 'too many records to check in one run. Running it again as the same user stops at the same point; a user '
        + 'with Modify All Data and View All Data needs far fewer queries for the check.';
    @TestVisible
    private static final String NOT_YET = 'The reset was not run, and nothing was changed: some of the records it '
        + 'would delete cannot be deleted yet.';
    @TestVisible
    private static final String NOT_YET_ADVICE = 'Run the reset again once the invoices finish processing.';
    @TestVisible
    private static final String NO_PERMISSION = 'no permission to delete this kind of record';
    @TestVisible
    private static final String NO_ACCESS = 'no delete access to these records';
    @TestVisible
    private static final String NOT_VISIBLE = 'not visible to the user running the reset';
    private static final String CANNOT_READ = 'the user running the reset cannot read this kind of record';
    private static final String NEEDS_EDIT_ACTIVATED = 'activated; setting them back to Draft needs the Edit '
        + 'Activated Orders permission';
    private static final String NEEDS_LIFECYCLE = 'lifecycle-managed; deleting them needs the Access '
        + 'Lifecycle-Managed Assets permission';
    private static final String INVOICE_NEEDS_PERMISSION = 'not Draft or Canceled; deleting them needs the '
        + 'Delete Invoice and Invoice Lines permission (permission set RLM_DeleteInvoices)';
    @TestVisible
    private static final String MEMO_NEEDS_PERMISSION = 'deleting credit memos needs the Allow Revenue Records '
        + 'Deletion permission (Billing Admin permission set)';
    @TestVisible
    private static final String INVOICE_IN_PROGRESS = 'still processing; run the reset once they finish';

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
     * What the reset did. When `completed` is false the run was refused, stopped
     * early or failed, and `reason` says why. `cleared` is true only when the run
     * completed and every record it was asked to delete is gone.
     */
    public class Result {
        @InvocableVariable(label='Completed' description='True when every reset step ran.')
        public Boolean completed;

        @InvocableVariable(label='Cleared' description='True when the reset completed and left nothing behind.')
        public Boolean cleared;

        @InvocableVariable(label='Reason' description='Why the reset did not run, or stopped, when it did not complete.')
        public String reason;

        @InvocableVariable(label='Removed' description='Records the reset deleted, by object.')
        public String removedSummary;

        @InvocableVariable(label='Retained' description='Records the reset did not delete, by object, with the reason.')
        public String retainedSummary;
    }

    /** Ends a run early when a limit is close, before the platform throws a LimitException. */
    private class ResetStoppedException extends Exception {}

    /** Ends the planning, before anything changes, when the account is too large to plan in one run. */
    private class PlanTooLargeException extends Exception {}

    /**
     * What the current run removed and did not remove. Copied before phase 2, so a
     * rollback can restore what phase 1 actually did.
     */
    private class ResetReport {
        public List<String> removedLabels = new List<String>();
        public Map<String, Integer> removed = new Map<String, Integer>();
        public List<Kept> kept = new List<Kept>();
        // Rows a delete refused, with the error. A later attempt that removes the
        // row takes it back out.
        public Map<Id, String> refused = new Map<Id, String>();

        public ResetReport copy() {
            ResetReport c = new ResetReport();
            c.removedLabels = removedLabels.clone();
            c.removed = removed.clone();
            c.kept = kept.clone();
            c.refused = refused.clone();
            return c;
        }
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

    // The plan's groups of records. Phase 1 deletes the usage groups; phase 2 the rest.
    private static final String G_POLICIES = 'policies';
    private static final String G_ACCOUNT_RATE_CARD_ENTRIES = 'accountRateCardEntries';
    private static final String G_ENTRIES = 'entries';
    private static final String G_BILLING_PERIOD_ITEMS = 'billingPeriodItems';
    private static final String G_SUMMARIES = 'summaries';
    private static final String G_RATABLE_SUMMARIES = 'ratableSummaries';
    private static final String G_JOURNALS = 'journals';
    private static final String G_BUCKETS = 'buckets';
    private static final String G_ENTITLEMENTS = 'entitlements';
    private static final String G_ENTITLEMENT_ACCOUNTS = 'entitlementAccounts';
    private static final String G_COMMITMENT_JUNCTIONS = 'commitmentJunctions';
    private static final String G_ASSETS = 'assets';
    private static final String G_ASSET_RATE_CARD_ENTRIES = 'assetRateCardEntries';
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

    // Lets a test fail phase 2 after it has deleted something, to prove the rollback.
    @TestVisible
    private static Exception phaseTwoFailureForTest;

    // Lets a test shrink the teardown round cap, to reach USAGE_TOO_LARGE.
    @TestVisible
    private static Integer maxTeardownRoundsForTest;

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

    // Lets a test stand in for missing permissions, by field name, since a test cannot
    // take a permission away from the running admin.
    @TestVisible
    private static Set<String> withoutPermissionForTest = new Set<String>();

    /**
     * Main Method
     * Entry point for the account reset; see the class header.
     *
     * @param request One InputVariables: the account, and which records to delete
     * @return One Result for the request, or none for an empty request
     */
    @InvocableMethod(label='Reset Account Related Objects' description='Deletes the records built on an account so it can be sold to again, and reports what it removed and what it did not; refuses, changing nothing, when the user cannot delete them all')
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
        Boolean deleteCollections = input.DeleteCollectionPlans == true;
        Boolean preserveContractsWithPrices = input.PreserveContractsWithContractedPrices == true;

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
        // Not deleted by design: another account's data, and what Salesforce never deletes.
        recordRetained(UsageEntitlementBucket.SObjectType, plan.foreignBuckets, FOREIGN_BUCKET);
        recordRetained(Payment.SObjectType, plan.payments, PAYMENTS_KEPT);
        if (plan.lockedDebitMemos > 0) {
            recordRetained(typeOf('DebitMemo'), plan.lockedDebitMemos, DEBIT_MEMOS_KEPT);
        }
        for (String status : plan.creditMemosByOtherStatus.keySet()) {
            recordRetained(CreditMemo.SObjectType, plan.creditMemosByOtherStatus.get(status),
                'status ' + status + ' can be neither canceled nor deleted');
        }

        // ------------------------------------------------------------------
        // Phase 1: the usage graph, BEFORE the savepoint, deliberately. It is
        // convergent -- a rerun simply finds fewer rows -- and its progress MUST
        // survive a later failure: inside the savepoint, one exception anywhere
        // below would roll back every usage row removed here, and the reset could
        // never converge. A failure here is returned as a Result rather than thrown:
        // a thrown exception fails the flow, which rolls back the whole transaction.
        try {
            teardown(new List<String>{
                G_POLICIES, G_ACCOUNT_RATE_CARD_ENTRIES, G_ENTRIES, G_BILLING_PERIOD_ITEMS, G_SUMMARIES,
                G_RATABLE_SUMMARIES, G_JOURNALS, G_BUCKETS, G_ENTITLEMENTS, G_ENTITLEMENT_ACCOUNTS,
                G_COMMITMENT_JUNCTIONS
            });
            if (plan.usageTruncated) {
                // The plan read only part of the usage. Whatever it read goes now, the
                // entitlements bound to the assets included (normally phase 2's): an asset
                // cannot go while unread ones remain, so each run must make progress here.
                teardown(new List<String>{ G_ASSET_ENTRIES, G_ASSET_BUCKETS, G_ASSET_ENTITLEMENTS });
                throw new ResetStoppedException(USAGE_TOO_LARGE);
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
        ResetReport afterPhaseOne = report.copy();
        try {
            // Before billing: deleting an invoice clears a dispute's link to it.
            if (deleteCollections) {
                deleteCollectionRecords();
            }
            deletePlanned(G_SCHEDULE_GROUPS);
            if (deleteBilling) {
                deleteBillingRecords();
            }
            // Fulfillment records that reference orders and order lines go first.
            if (deleteFulfillment) {
                deletePlanned(G_LINE_SOURCE_RELATIONS);
                deletePlanned(G_STEP_SOURCES);
                deletePlanned(G_FULFILLMENT_ORDER_LINES);
                deletePlanned(G_FULFILLMENT_ORDERS);
            }
            // A contract's rate card entries go with it; contracts Preserve Contracts
            // with Contracted Prices keeps are not in the plan, nor are their entries.
            deletePlanned(G_CONTRACT_RATE_CARD_ENTRIES);
            deleteAll(plan.rowsOf(G_CONTRACTS));
            // An activated order cannot be deleted, so orders go back to Draft first;
            // all or nothing, so none is left changed but kept.
            List<SObject> orders = plan.rowsOf(G_ORDERS);
            for (SObject o : orders) {
                o.put('Status', 'Draft');
            }
            updateAll(orders);
            deleteAll(orders);
            if (deleteFulfillment) {
                deletePlanned(G_FULFILLMENT_PLANS);
                deletePlanned(G_DECOMPOSITIONS);
                deletePlanned(G_FULFILLMENT_ASSETS);
            }
            if (deleteAssets) {
                deleteAssets();
            } else if (!plan.usageDrained()) {
                // What phase 1 could not delete gets one more try, now that phase 2
                // has removed what may have held it.
                teardown(PHASE_ONE_LEFTOVERS);
            }
            deletePlanned(G_QUOTE_DOCUMENTS);
            deletePlanned(G_FILES);
            deleteAll(plan.rowsOf(G_QUOTES));
            deleteAll(plan.rowsOf(G_OPPORTUNITIES));

            if (phaseTwoFailureForTest != null) {
                throw phaseTwoFailureForTest;
            }
        } catch (Exception e) {
            Database.rollback(sp);
            report = afterPhaseOne;
            String cause = e instanceof ResetStoppedException ? e.getMessage() + ' ' + RUN_AGAIN : e.getMessage();
            String kept = report.removedLabels.isEmpty()
                ? 'Nothing was deleted; the run was rolled back. '
                : 'Only what the usage cleanup deleted stays deleted (see Removed); everything else was rolled back. ';
            return finish(false, kept + cause);
        }
        return finish(true, null);
    }

    // Phase 1's usage objects, retried in phase 2 when phase 1 left rows behind.
    private static final List<String> PHASE_ONE_LEFTOVERS = new List<String>{
        G_POLICIES, G_ACCOUNT_RATE_CARD_ENTRIES, G_ENTRIES, G_BILLING_PERIOD_ITEMS, G_SUMMARIES,
        G_RATABLE_SUMMARIES, G_JOURNALS, G_BUCKETS, G_ENTITLEMENTS, G_ENTITLEMENT_ACCOUNTS,
        G_COMMITMENT_JUNCTIONS
    };

    /**
     * Delete Collection Plans: the planned collection plans with their promise-to-pay
     * payment schedules, the disputes, and the cases of a plan or dispute that went.
     * Plan and dispute items go with their parents (live 264).
     */
    private static void deleteCollectionRecords() {
        deletePlanned(G_PLAN_SCHEDULES);
        Set<Id> gone = deletePlanned(G_COLLECTION_PLANS);
        gone.addAll(deletePlanned(G_DISPUTES));
        List<SObject> cases = new List<SObject>();
        for (SObject planCase : plan.rowsOf(G_COLLECTION_CASES)) {
            if (gone.contains(plan.caseParent.get(planCase.Id))) {
                cases.add(planCase);
            }
        }
        deleteQuietly(cases);
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
        deletePlanned(G_DEBIT_MEMOS);
        deleteAll(plan.rowsOf(G_INVOICES));
        deletePlanned(G_INVOICE_SCHEDULES);
        deletePlanned(G_INVOICE_DOCUMENTS);
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
     * Deletes the planned assets: their rate card entries, the entitlements bound to
     * them and their buckets (another account's entitlement bound to an asset this
     * reset deletes goes with it), what phase 1 could not delete, the work orders and
     * cases that reference them, their relationships (both directions) and then the
     * assets, all or nothing.
     *
     * AssetRateCardEntry rows are generated when the asset is created and are NOT
     * recreated for an existing asset, so they go here, in phase 2, with the assets:
     * a rollback restores both.
     */
    private static void deleteAssets() {
        deletePlanned(G_ASSET_RATE_CARD_ENTRIES);
        List<String> usage = new List<String>{ G_ASSET_ENTRIES, G_ASSET_BUCKETS, G_ASSET_ENTITLEMENTS };
        usage.addAll(PHASE_ONE_LEFTOVERS);
        teardown(usage);
        deletePlanned(G_WORK_ORDERS);
        deletePlanned(G_ASSET_CASES);
        deleteAll(plan.rowsOf(G_ASSET_RELATIONSHIPS));
        deleteAll(plan.rowsOf(G_ASSETS));
    }

    /**
     * Retries the planned rows of `keys`, in order, round after round, until a round
     * removes nothing or nothing is left. A row a round refuses is recorded; a later
     * round that removes it takes it back out. Still removing rows when the rounds
     * run out stops the run: the rows deleted so far are real progress.
     */
    private static void teardown(List<String> keys) {
        Integer maxRounds = maxTeardownRoundsForTest != null ? maxTeardownRoundsForTest : MAX_TEARDOWN_ROUNDS;
        for (Integer round = 1; round <= maxRounds; round++) {
            Integer progress = 0;
            Integer left = 0;
            for (String key : keys) {
                progress += deletePlanned(key).size();
                left += plan.rowsOf(key).size();
            }
            if (progress == 0 || left == 0) {
                return;
            }
        }
        for (String key : keys) {
            if (!plan.rowsOf(key).isEmpty()) {
                throw new ResetStoppedException(USAGE_TOO_LARGE);
            }
        }
    }

    /** Deletes what is left of a planned group, best effort, and drops what went from the plan. */
    private static Set<Id> deletePlanned(String key) {
        Set<Id> gone = deleteRows(plan.rowsOf(key), false);
        plan.remove(key, gone);
        return gone;
    }

    /**
     * The Result of a run the plan's check refused: not completed, nothing removed,
     * and the reason that lists why. Nothing was changed, so there is nothing else.
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
        plan = null;
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

        List<String> removed = new List<String>();
        for (String label : report.removedLabels) {
            removed.add(label + ': ' + report.removed.get(label));
        }
        List<String> kept = new List<String>();
        for (Kept k : report.kept) {
            kept.add(k.label + ': ' + k.count + ' (' + k.why + ')');
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
                    SELECT PermissionsModifyAllData, PermissionsViewAllData, PermissionsEditActivatedOrders
                    FROM UserPermissionAccess LIMIT 1
                ];
                userPermissions.put('PermissionsModifyAllData', core.PermissionsModifyAllData == true);
                userPermissions.put('PermissionsViewAllData', core.PermissionsViewAllData == true);
                userPermissions.put('PermissionsEditActivatedOrders', core.PermissionsEditActivatedOrders == true);
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
     * The 10,000-row DML limit is per TRANSACTION, not per statement, so the list is
     * clamped to the remaining budget here -- one clamp covers every call site.
     * Running out deletes what fits and then stops the run with a
     * ResetStoppedException, rather than a LimitException that rolls back all the
     * progress made.
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
                continue;
            }
            gone.add(rowId);
            report.refused.remove(rowId);
        }
        recordRemoved(records[0].getSObjectType(), removed);
        if (trimmed) {
            throw new ResetStoppedException(DML_LIMIT);
        }
        return gone;
    }

    /** Best-effort delete: a refusal is recorded, not thrown. */
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
     * plan (or, for a usage batch, marks it truncated).
     */
    private static Integer readCap() {
        Integer rowsLeft = Limits.getLimitQueryRows() - Limits.getQueryRows();
        Integer heapRows = (Limits.getLimitHeapSize() - Limits.getHeapSize()) / 500;
        return Math.max(0, Math.min(rowsLeft, heapRows));
    }

    /** The record that blocks the reset for one reason, of one object. */
    /**
     * The refusal, from the blockers and their description. An invoice still processing is
     * not about who runs the reset: nobody can delete it until it finishes, so a refusal
     * for that alone gets its own wording and advice.
     */
    @TestVisible
    private static String refusal(List<Blocker> blockers, String described) {
        Boolean waiting = false;
        Boolean waitingOnly = !blockers.isEmpty();
        for (Blocker b : blockers) {
            if (b.reason == INVOICE_IN_PROGRESS) {
                waiting = true;
            } else {
                waitingOnly = false;
            }
        }
        return (waitingOnly ? NOT_YET : REFUSED) + ' ' + described + '. '
            + (waitingOnly ? NOT_YET_ADVICE : REFUSED_ADVICE + (waiting ? ' ' + NOT_YET_ADVICE : ''));
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
     * Budget: each read first requires a query to spare (requireQuery) and is bounded by
     * the query rows left (rowCap); either running out ends the plan with
     * PlanTooLargeException, before anything changes. Usage objects are read
     * TEARDOWN_BATCH rows at a time: with more, the run deletes the planned rows and
     * asks for another run.
     */
    @TestVisible
    private without sharing class Plan {
        private final List<String> USAGE_GROUPS = new List<String>{
            G_ENTRIES, G_BILLING_PERIOD_ITEMS, G_SUMMARIES, G_RATABLE_SUMMARIES, G_JOURNALS, G_BUCKETS, G_ENTITLEMENTS,
            G_ENTITLEMENT_ACCOUNTS, G_COMMITMENT_JUNCTIONS, G_POLICIES, G_ACCOUNT_RATE_CARD_ENTRIES
        };

        public List<Blocker> blockers = new List<Blocker>();
        // Not deleted by design, counted for the Result.
        public Integer foreignBuckets = 0;
        public Integer payments = 0;
        public Integer lockedDebitMemos = 0;
        public Map<String, Integer> creditMemosByOtherStatus = new Map<String, Integer>();
        // The plan or dispute each collection case belongs to.
        public Map<Id, Id> caseParent = new Map<Id, Id>();
        // True when a usage object had more rows than one run plans.
        public Boolean usageTruncated = false;
        // Rows per usage object this run reads (TEARDOWN_BATCH or CHECKED_TEARDOWN_BATCH).
        private Integer batch;

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
            batch = usageBatchForTest != null ? usageBatchForTest : privileged ? TEARDOWN_BATCH : CHECKED_TEARDOWN_BATCH;
            binds.put('accountId', accountId);

            // ---------------------------------------------------- assets and contracts
            Boolean lifecycleField = typeOf('Asset').getDescribe().fields.getMap().containsKey('haslifecyclemanagement');
            List<SObject> assets = read('Asset', lifecycleField ? ', HasLifecycleManagement' : '',
                'AccountId = :accountId', null);
            Set<Id> assetIds = ids(assets);
            binds.put('assetIds', assetIds);
            List<SObject> contracts = read('Contract', '', 'AccountId = :accountId', null);
            Set<Id> contractIds = ids(contracts);
            binds.put('contractIds', contractIds);
            if (preserveContractsWithPrices && typeOf('ContractItemPrice') != null && !contracts.isEmpty()) {
                Set<Id> priced = new Set<Id>();
                for (SObject price : query('ContractItemPrice', 'ContractId', 'ContractId IN :contractIds', null)) {
                    priced.add((Id) price.get('ContractId'));
                }
                List<SObject> deleted = new List<SObject>();
                for (SObject contract : contracts) {
                    if (!priced.contains(contract.Id)) {
                        deleted.add(contract);
                    }
                }
                contracts = deleted;
            }
            put(G_CONTRACTS, 'Contract', contracts);
            binds.put('deletedContractIds', ids(contracts));

            // ---------------------------------------------------- usage (phase 1)
            // Binding policies of the account, of the contracts the run deletes and, with
            // Delete Assets, of the assets: a kept contract or asset keeps its policies.
            Set<Id> bindingIds = new Set<Id>(ids(contracts));
            if (deleteAssets) {
                bindingIds.addAll(assetIds);
            }
            bindingIds.add(accountId);
            binds.put('bindingIds', bindingIds);
            put(G_POLICIES, 'BindingObjUsageRsrcPlcy',
                read('BindingObjUsageRsrcPlcy', '', 'BindingObjectId IN :bindingIds', null));
            List<SObject> accountEntries = new List<SObject>();
            List<SObject> contractEntries = new List<SObject>();
            for (SObject entry : read('BindingObjectRateCardEntry', ', BindingObjectId',
                'BindingObjectId = :accountId OR BindingObjectId IN :deletedContractIds', null)) {
                if (entry.get('BindingObjectId') == accountId) {
                    accountEntries.add(entry);
                } else {
                    contractEntries.add(entry);
                }
            }
            // The account's in phase 1; a contract's with the contract, in phase 2, so a
            // rollback restores them together.
            put(G_ACCOUNT_RATE_CARD_ENTRIES, 'BindingObjectRateCardEntry', accountEntries);
            put(G_CONTRACT_RATE_CARD_ENTRIES, 'BindingObjectRateCardEntry', contractEntries);
            String byAccountOrAsset = 'AccountId = :accountId OR AssetId IN :assetIds';
            put(G_BILLING_PERIOD_ITEMS, 'UsageBillingPeriodItem',
                read('UsageBillingPeriodItem', '', byAccountOrAsset, batch));
            put(G_SUMMARIES, 'UsageSummary', read('UsageSummary', '', byAccountOrAsset, batch));
            put(G_RATABLE_SUMMARIES, 'UsageRatableSummary', read('UsageRatableSummary', '', byAccountOrAsset, batch));
            put(G_JOURNALS, 'TransactionJournal', read('TransactionJournal', '', 'AccountId = :accountId', batch));
            List<SObject> ownEntitlements = read('TransactionUsageEntitlement', '', 'AccountId = :accountId', batch);
            put(G_ENTITLEMENTS, 'TransactionUsageEntitlement', ownEntitlements);
            // Another account's entitlement bound to an asset this reset deletes goes with
            // the asset, in phase 2.
            List<SObject> assetEntitlements = new List<SObject>();
            if (deleteAssets && !assetIds.isEmpty()) {
                assetEntitlements = read('TransactionUsageEntitlement', '', '(AssetId IN :assetIds '
                    + 'OR GrantBindingTargetId IN :assetIds) AND AccountId != :accountId', batch);
            }
            put(G_ASSET_ENTITLEMENTS, 'TransactionUsageEntitlement', assetEntitlements);
            Set<Id> ownTueIds = ids(ownEntitlements);
            Set<Id> assetTueIds = ids(assetEntitlements);
            List<SObject> entitlementAccounts = read('UsageEntitlementAccount', '', 'AccountId = :accountId', batch);
            put(G_ENTITLEMENT_ACCOUNTS, 'UsageEntitlementAccount', entitlementAccounts);
            Set<Id> allTueIds = new Set<Id>(ownTueIds);
            allTueIds.addAll(assetTueIds);
            binds.put('tueIds', allTueIds);
            List<SObject> entries = allTueIds.isEmpty() ? new List<SObject>() : read('UsageEntitlementEntry',
                ', TransactionUsageEntitlementId', 'TransactionUsageEntitlementId IN :tueIds', batch);
            put(G_ENTRIES, 'UsageEntitlementEntry', byEntitlement(entries, ownTueIds, true));
            put(G_ASSET_ENTRIES, 'UsageEntitlementEntry', byEntitlement(entries, ownTueIds, false));
            planBuckets(ids(entitlementAccounts), ownTueIds, assetTueIds, deleteAssets ? assetIds : new Set<Id>());
            put(G_COMMITMENT_JUNCTIONS, 'UsageCmtAssetRelatedObj', assetIds.isEmpty() ? new List<SObject>()
                : read('UsageCmtAssetRelatedObj', '', 'AssetId IN :assetIds OR RelatedObjectId IN :assetIds', batch));

            // ---------------------------------------------------- assets (phase 2)
            if (deleteAssets) {
                put(G_ASSETS, 'Asset', assets);
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
                        read('AssetRateCardEntry', '', 'AssetId IN :assetIds', null));
                    put(G_ASSET_RELATIONSHIPS, 'AssetRelationship',
                        read('AssetRelationship', '', 'AssetId IN :assetIds OR RelatedAssetId IN :assetIds', null));
                    put(G_WORK_ORDERS, 'WorkOrder', readByAsset('WorkOrder'));
                    put(G_ASSET_CASES, 'Case', readByAsset('Case'));
                }
            }

            put(G_SCHEDULE_GROUPS, 'BillingScheduleGroup',
                read('BillingScheduleGroup', '', 'BillingAccountId = :accountId', null));

            // ---------------------------------------------------- orders
            List<SObject> orders = read('Order', ', Status', 'AccountId = :accountId', null);
            put(G_ORDERS, 'Order', orders);
            for (SObject o : orders) {
                String reason = orderBlocker((String) o.get('Status'));
                if (reason != null) {
                    special('Order', reason, o);
                }
            }
            Set<Id> orderIds = ids(orders);
            binds.put('orderIds', orderIds);

            // ---------------------------------------------------- billing
            List<SObject> invoices = new List<SObject>();
            if (deleteBilling || deleteCollections || deleteFulfillment) {
                invoices = read('Invoice', ', Status, PaymentScheduleId', 'BillingAccountId = :accountId', null);
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
                    : read('PaymentSchedule', '', 'Id IN :scheduleIds', null));
                List<SObject> debitMemos = new List<SObject>();
                if (typeOf('DebitMemo') != null) {
                    for (SObject memo : read('DebitMemo', ', Status', 'AccountId = :accountId', null)) {
                        if (memo.get('Status') == 'Posted' || memo.get('Status') == 'Void') {
                            lockedDebitMemos++;
                        } else {
                            debitMemos.add(memo);
                        }
                    }
                }
                put(G_DEBIT_MEMOS, 'DebitMemo', debitMemos);
                List<SObject> creditMemos = new List<SObject>();
                for (SObject memo : read('CreditMemo', ', Status', 'BillingAccountId = :accountId', null)) {
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
                List<SObject> plans = read('CollectionPlan', '', 'AccountId = :accountId', null);
                put(G_COLLECTION_PLANS, 'CollectionPlan', plans);
                Set<Id> planIds = ids(plans);
                binds.put('planIds', planIds);
                List<SObject> collectionCases = new List<SObject>();
                if (!planIds.isEmpty()) {
                    // Plan items go with their plan; their ids find promise-to-pay schedules.
                    binds.put('planItemIds', ids(query('CollectionPlanItem', '', 'CollectionPlanId IN :planIds', null)));
                    put(G_PLAN_SCHEDULES, 'PaymentSchedule', read('PaymentSchedule', '',
                        'ReferenceEntityId IN :planIds OR CollectionPlanItemId IN :planItemIds', null));
                    for (SObject planCase : read('Case', ', SourceId', 'SourceId IN :planIds AND AccountId = :accountId',
                        null)) {
                        caseParent.put(planCase.Id, (Id) planCase.get('SourceId'));
                        collectionCases.add(planCase);
                    }
                }
                if (typeOf('Dispute') != null) {
                    List<SObject> disputes = read('Dispute', ', CaseId',
                        'AccountId = :accountId OR InvoiceId IN :invoiceIds', null);
                    put(G_DISPUTES, 'Dispute', disputes);
                    Map<Id, Id> disputeOfCase = new Map<Id, Id>();
                    for (SObject dispute : disputes) {
                        if (dispute.get('CaseId') != null) {
                            disputeOfCase.put((Id) dispute.get('CaseId'), dispute.Id);
                        }
                    }
                    if (!disputeOfCase.isEmpty()) {
                        Set<Id> disputeCaseIds = disputeOfCase.keySet();
                        binds.put('disputeCaseIds', disputeCaseIds);
                        for (SObject disputeCase : read('Case', '', 'Id IN :disputeCaseIds AND AccountId = :accountId',
                            null)) {
                            caseParent.put(disputeCase.Id, disputeOfCase.get(disputeCase.Id));
                            collectionCases.add(disputeCase);
                        }
                    }
                }
                put(G_COLLECTION_CASES, 'Case', collectionCases);
            }

            // ---------------------------------------------------- fulfillment
            if (deleteFulfillment) {
                Set<Id> orderItemIds = ids(query('OrderItem', '', 'OrderId IN :orderIds', null));
                binds.put('orderItemIds', orderItemIds);
                Set<String> sourceIds = new Set<String>();
                for (Id sourceId : orderItemIds) {
                    sourceIds.add(sourceId);
                }
                for (Id sourceId : orderIds) {
                    sourceIds.add(sourceId);
                }
                binds.put('sourceIds', sourceIds);
                binds.put('summaryIds', ids(query('OrderSummary', '', 'AccountId = :accountId', null)));
                List<SObject> fulfillmentOrders = read('FulfillmentOrder', '', 'AccountId = :accountId '
                    + 'OR OrderId IN :orderIds OR InvoiceId IN :invoiceIds OR OrderSummaryId IN :summaryIds', null);
                put(G_FULFILLMENT_ORDERS, 'FulfillmentOrder', fulfillmentOrders);
                binds.put('fulfillmentOrderIds', ids(fulfillmentOrders));
                List<SObject> lines = read('FulfillmentOrderLineItem', '', 'FulfillmentOrderId IN :fulfillmentOrderIds', null);
                put(G_FULFILLMENT_ORDER_LINES, 'FulfillmentOrderLineItem', lines);
                binds.put('lineIds', ids(lines));
                List<SObject> fulfillmentPlans = read('FulfillmentPlan', '', 'SourceIdentifier IN :sourceIds '
                    + 'AND (SourceType = \'StandardOrder\' OR SourceType = \'OrderItem\')', null);
                put(G_FULFILLMENT_PLANS, 'FulfillmentPlan', fulfillmentPlans);
                binds.put('fulfillmentPlanIds', ids(fulfillmentPlans));
                binds.put('stepIds', ids(query('FulfillmentStep', '', 'FulfillmentPlanId IN :fulfillmentPlanIds', null)));
                put(G_STEP_SOURCES, 'FulfillmentStepSource',
                    read('FulfillmentStepSource', '', 'StepId IN :stepIds OR SourceLineItemId IN :orderItemIds', null));
                List<SObject> fulfillmentAssets = read('FulfillmentAsset', '', 'AccountId = :accountId', null);
                put(G_FULFILLMENT_ASSETS, 'FulfillmentAsset', fulfillmentAssets);
                binds.put('fulfillmentAssetIds', ids(fulfillmentAssets));
                put(G_DECOMPOSITIONS, 'AssetFulfillmentDecomp', read('AssetFulfillmentDecomp', '',
                    'FulfillmentSourceAssetId IN :fulfillmentAssetIds OR FulfillmentTargetAssetId IN :fulfillmentAssetIds',
                    null));
                put(G_LINE_SOURCE_RELATIONS, 'FulfillmentLineSourceRel', read('FulfillmentLineSourceRel', '',
                    'SourceLineItemId IN :orderItemIds OR FulfilmentOrderLineId IN :lineIds', null));
            }

            // ---------------------------------------------------- quotes, opportunities, documents
            // QuoteAccountId is the quote's own account and AccountId its opportunity's;
            // a quote can have either alone.
            List<SObject> quotes = read('Quote', '', 'QuoteAccountId = :accountId OR AccountId = :accountId', null);
            put(G_QUOTES, 'Quote', quotes);
            put(G_OPPORTUNITIES, 'Opportunity', read('Opportunity', '', 'AccountId = :accountId', null));
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
                    'ReferenceObject IN :references', null)) {
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
                    files = read('ContentDocument', ', OwnerId', 'Id IN :fileIds', null);
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
         * another account's data. Those are counted (foreignBuckets) and left out.
         * Buckets holding an entitlement bound to an asset go in phase 2, with the asset.
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
                    'ParentId IN :bucketParents OR TransactionUsageEntitlementId IN :heldBy', batch));
                Set<Id> frontier = new Set<Id>(buckets.keySet());
                while (!frontier.isEmpty() && !usageTruncated) {
                    binds.put('bucketParents', frontier);
                    binds.put('knownBuckets', new Set<Id>(buckets.keySet()));
                    frontier = new Set<Id>();
                    for (SObject child : read('UsageEntitlementBucket', ', ParentId, TransactionUsageEntitlementId',
                        'ParentId IN :bucketParents AND Id NOT IN :knownBuckets', batch)) {
                        buckets.put(child.Id, child);
                        frontier.add(child.Id);
                    }
                }
            }
            // An entitlement held by a bucket but not in the plan's lists is another
            // account's, unless the lists were cut at their batch: then it may be one of the
            // account's own not read this run. Read whose each one is, so a bucket is reported
            // as another account's only when it is; one of the account's own waits for the
            // next run.
            Set<Id> unknown = new Set<Id>();
            for (SObject bucket : buckets.values()) {
                Id held = (Id) bucket.get('TransactionUsageEntitlementId');
                if (held != null && !heldBy.contains(held)) {
                    unknown.add(held);
                }
            }
            Set<Id> othersEntitlements = new Set<Id>(unknown);
            if (!unknown.isEmpty() && usageTruncated) {
                binds.put('unknownEntitlements', unknown);
                binds.put('assetIds', assetIds);
                for (SObject entitlement : query('TransactionUsageEntitlement', 'Id, AccountId, AssetId, GrantBindingTargetId',
                    'Id IN :unknownEntitlements', null)) {
                    Boolean ours = entitlement.get('AccountId') == accountId
                        || assetIds.contains((Id) entitlement.get('AssetId'))
                        || assetIds.contains((Id) entitlement.get('GrantBindingTargetId'));
                    if (ours) {
                        othersEntitlements.remove(entitlement.Id);
                    }
                }
            }
            Set<Id> foreign = new Set<Id>();
            Set<Id> notThisRun = new Set<Id>();
            for (SObject bucket : buckets.values()) {
                Id held = (Id) bucket.get('TransactionUsageEntitlementId');
                if (held == null || heldBy.contains(held)) {
                    continue;
                }
                Set<Id> chain = othersEntitlements.contains(held) ? foreign : notThisRun;
                SObject up = bucket;
                while (up != null && chain.add(up.Id)) {
                    up = buckets.get((Id) up.get('ParentId'));
                }
            }
            notThisRun.removeAll(foreign);
            foreign.addAll(notThisRun);
            foreignBuckets = foreign.size() - notThisRun.size();
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
                return read(objectName, '', 'AssetId IN :assetIds', null);
            } catch (QueryException e) {
                if (!e.getMessage().contains('No such column')) {
                    throw e;
                }
                return new List<SObject>();
            }
        }

        /** Reads `objectName`'s records matching `filter`, with its name field, in system mode. */
        private List<SObject> read(String objectName, String extraFields, String filter, Integer batch) {
            if (typeOf(objectName) == null) {
                return new List<SObject>();
            }
            String nameField = nameFieldOf(objectName);
            return query(objectName, 'Id' + (nameField == null ? '' : ', ' + nameField) + extraFields, filter, batch);
        }

        /**
         * One system-mode read. `fields` defaults to Id. With `batch`, at most that many
         * rows, and more marks the usage as truncated; without, the rows left in the
         * transaction bound it, and reaching that bound ends the plan.
         */
        private List<SObject> query(String objectName, String fields, String filter, Integer batch) {
            if (typeOf(objectName) == null) {
                return new List<SObject>();
            }
            requireQuery(1);
            Integer rowsLeft = readCap();
            Integer cap = batch != null ? Math.min(batch + 1, rowsLeft) : rowsLeft;
            if (cap <= 0) {
                throw new PlanTooLargeException(PLAN_TOO_LARGE);
            }
            binds.put('rowCap', cap);
            List<SObject> found = Database.queryWithBinds('SELECT ' + (String.isBlank(fields) ? 'Id' : fields)
                + ' FROM ' + objectName + ' WHERE ' + filter + ' LIMIT :rowCap', binds, AccessLevel.SYSTEM_MODE);
            if (found.size() >= cap) {
                if (batch == null || cap < batch + 1) {
                    throw new PlanTooLargeException(PLAN_TOO_LARGE);
                }
                usageTruncated = true;
                found.remove(found.size() - 1);
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
            if (Limits.getLimitQueries() - Limits.getQueries() < needed) {
                throw new PlanTooLargeException(PLAN_TOO_LARGE);
            }
        }

        private void put(String key, String objectName, List<SObject> records) {
            rows.put(key, records);
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
                } else if (reason != null) {
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

        /** True when phase 1 deleted every planned usage row. */
        public Boolean usageDrained() {
            for (String key : USAGE_GROUPS) {
                if (!rowsOf(key).isEmpty()) {
                    return false;
                }
            }
            return true;
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
