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
    // spin. In practice QUERY_RESERVE ends a run first, after five rounds, and the
    // next run carries on.
    //
    // TEARDOWN_BATCH is a per-QUERY ceiling only -- it does NOT bound the
    // transaction. The 10,000-row DML limit is per transaction and this loop
    // issues nine deletes per round, so the real guard is the remaining-budget
    // clamp inside deleteRows(), which stops the run with a Result instead of
    // a LimitException.
    private static final Integer MAX_TEARDOWN_ROUNDS = 6;
    private static final Integer TEARDOWN_BATCH = 2000;

    // The queries one teardown round issues, and the queries phase 2 needs once
    // the usage graph is gone (about 45 with every option on). A round starts only
    // while both are left; otherwise a large usage graph would spend phase 2's
    // queries and end in a LimitException.
    private static final Integer QUERIES_PER_ROUND = 9;
    private static final Integer QUERY_RESERVE = 50;

    private static final String RUN_AGAIN = 'Run the reset again; it continues from where this run stopped.';
    private static final String USAGE_TOO_LARGE = 'The account has more usage records than one run can remove.';
    private static final String DML_LIMIT = 'The reset reached the Salesforce limit on record changes in one run.';
    private static final String QUERY_LIMIT = 'The reset reached the Salesforce limit on queries in one run.';
    private static final String INVOICE_NEEDS_PERMISSION = 'not Draft or Canceled, and deleting them needs the '
        + 'Delete Invoice and Invoice Lines permission (permission set RLM_DeleteInvoices)';
    private static final String INVOICE_IN_PROGRESS = 'still processing; run the reset again once they finish';
    private static final String PAYMENTS_KEPT = 'payments are not deleted: Salesforce does not allow deleting processed payments';
    private static final String MEMO_ON_KEPT_INVOICE = 'applied to an invoice that was kept';
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

        @InvocableVariable(label='Retained' description='Records the reset kept, by object, with the reason.')
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

        public ResetReport copy() {
            ResetReport c = new ResetReport();
            c.removedLabels = removedLabels.clone();
            c.removed = removed.clone();
            c.kept = kept.clone();
            c.refused = refused.clone();
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

    // Lets a test shrink the DML row budget, to prove a run that runs out stops cleanly.
    @TestVisible
    private static Integer dmlRowLimitForTest;

    /**
     * The account's orders, invoices and fulfillment records, queried once at the
     * start of phase 2 and shared by the steps that delete them. The fulfillment
     * graph is queried only when it is going to be deleted.
     */
    private class OrderData {
        public List<Order> orders;
        public Set<Id> orderIds;
        public Set<Id> orderItemIds;
        // Status and PaymentScheduleId are for Delete Billing; the Ids also find the
        // fulfillment orders raised against an invoice.
        public List<Invoice> invoices;

        public List<FulfillmentOrder> fulfillmentOrders = new List<FulfillmentOrder>();
        public List<FulfillmentPlan> fulfillmentPlans = new List<FulfillmentPlan>();
        public Set<Id> fulfillmentStepIds = new Set<Id>();
        public List<FulfillmentAsset> fulfillmentAssets = new List<FulfillmentAsset>();
        public Set<Id> fulfillmentAssetIds = new Set<Id>();
        public List<FulfillmentOrderLineItem> fulfillmentOrderLineItems = new List<FulfillmentOrderLineItem>();
        public List<FulfillmentLineSourceRel> fulfillmentLineSourceRels = new List<FulfillmentLineSourceRel>();

        public OrderData(Id accountId, Boolean withFulfillment) {
            this.orders = [SELECT Id FROM Order WHERE AccountId = :accountId];
            this.orderIds = new Map<Id, Order>(this.orders).keySet();
            this.orderItemIds = new Map<Id, OrderItem>(
                [SELECT Id FROM OrderItem WHERE Order.AccountId = :accountId]).keySet();
            this.invoices = [
                SELECT Id, Status, PaymentScheduleId FROM Invoice WHERE BillingAccountId = :accountId
            ];
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
            Set<Id> summaryIds = new Map<Id, OrderSummary>(
                [SELECT Id FROM OrderSummary WHERE AccountId = :accountId]).keySet();

            this.fulfillmentOrders = [
                SELECT Id
                FROM FulfillmentOrder
                WHERE AccountId = :accountId
                OR OrderId IN :this.orderIds
                OR InvoiceId IN :invoiceIds
                OR OrderSummaryId IN :summaryIds
            ];
            this.fulfillmentPlans = [
                SELECT Id
                FROM FulfillmentPlan
                WHERE SourceIdentifier IN :sourceIdentifiers
                AND (SourceType = 'StandardOrder' OR SourceType = 'OrderItem')
            ];
            Set<Id> planIds = new Map<Id, FulfillmentPlan>(this.fulfillmentPlans).keySet();
            this.fulfillmentStepIds = new Map<Id, FulfillmentStep>(
                [SELECT Id FROM FulfillmentStep WHERE FulfillmentPlanId IN :planIds]).keySet();
            this.fulfillmentAssets = [SELECT Id FROM FulfillmentAsset WHERE AccountId = :accountId];
            this.fulfillmentAssetIds = new Map<Id, FulfillmentAsset>(this.fulfillmentAssets).keySet();
            Set<Id> fulfillmentOrderIds = new Map<Id, FulfillmentOrder>(this.fulfillmentOrders).keySet();
            this.fulfillmentOrderLineItems = [
                SELECT Id FROM FulfillmentOrderLineItem WHERE FulfillmentOrderId IN :fulfillmentOrderIds
            ];
            Set<Id> lineItemIds = new Map<Id, FulfillmentOrderLineItem>(this.fulfillmentOrderLineItems).keySet();
            this.fulfillmentLineSourceRels = [
                SELECT Id
                FROM FulfillmentLineSourceRel
                WHERE SourceLineItemId IN :this.orderItemIds
                OR FulfilmentOrderLineId IN :lineItemIds
            ];
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
        ResetReport afterPhaseOne = report.copy();
        try {
            OrderData orderData = new OrderData(accountId, deleteFulfillment);

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
                deleteBillingRecords(accountId, orderData.invoices);
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
            // Delete quote-linked ContentDocuments before quotes are removed
            deleteQuoteDocuments(accountQuotes);
            deleteAll(accountQuotes);
            deleteAll([SELECT Id FROM Opportunity WHERE AccountId = :accountId]);

            if (phaseTwoFailureForTest != null) {
                throw phaseTwoFailureForTest;
            }
        } catch (Exception e) {
            Database.rollback(sp);
            report = afterPhaseOne;
            String cause = e instanceof ResetStoppedException ? e.getMessage() + ' ' + RUN_AGAIN : e.getMessage();
            return finish(false, 'Only usage records were deleted; everything else was rolled back. ' + cause);
        }
        return finish(true, null);
    }

    private static void startRun() {
        report = new ResetReport();
        accountAssetIds = new Set<Id>();
        accountContractIds = new Set<Id>();
        usageDrained = false;
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
     * Updates with allOrNone=false. A row that refuses is reported as retained,
     * with `failure` and the error as the reason; pass null when a later delete
     * reports it instead.
     *
     * @return The ids that were updated
     */
    private static Set<Id> updateRows(List<SObject> records, String failure) {
        Set<Id> updated = new Set<Id>();
        if (records.isEmpty()) {
            return updated;
        }
        if (records.size() > dmlRowsLeft()) {
            throw new ResetStoppedException(DML_LIMIT);
        }
        Database.SaveResult[] results = Database.update(records, false);
        for (Integer i = 0; i < results.size(); i++) {
            if (results[i].isSuccess()) {
                updated.add(records[i].Id);
            } else if (failure != null) {
                recordRetained(records[i].getSObjectType(), 1,
                    failure + ': ' + results[i].getErrors()[0].getMessage());
            }
        }
        return updated;
    }

    /** Stops the run while it still can, instead of letting the next query throw a LimitException. */
    private static void requireQueries(Integer needed) {
        if (Limits.getLimitQueries() - Limits.getQueries() < needed) {
            throw new ResetStoppedException(QUERY_LIMIT);
        }
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
        Map<String, Schema.SObjectType> types = Schema.getGlobalDescribe();
        Set<Id> caseIds = new Set<Id>();
        if (types.containsKey('CollectionPlan')) {
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
        if (types.containsKey('Dispute')) {
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
     * Posted invoices need the "Delete Invoice and Invoice Lines" permission
     * (BillingInvoiceSuperUser, from RLM_DeleteInvoices). Without it only Draft
     * and Canceled invoices go, and the rest are reported as retained. Invoices
     * that are still processing stay either way.
     *
     * Posted invoices are attempted only for a user who has the permission, and the
     * invoices go in ONE delete call that is never retried. Do not add a retry or a
     * fallback attempt: an invoice the platform refuses must stay refused.
     *
     * Deleting an invoice takes its lines, taxes, billing period items, credit
     * memo and payment applications, and billing journals with it. It does not
     * take its payment schedule, files or DocumentGenerationProcess rows, which
     * are deleted here.
     */
    private static void deleteBillingRecords(Id accountId, List<Invoice> invoices) {
        // First, so that a debit memo line adjusting an invoice line, or a debit
        // memo raised from a credit memo, is gone before either is deleted.
        deleteDebitMemos(accountId);

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
        List<PaymentSchedule> paymentSchedules = new List<PaymentSchedule>();
        for (Id scheduleId : schedules) {
            paymentSchedules.add(new PaymentSchedule(Id = scheduleId));
        }
        deleteQuietly(paymentSchedules);

        deleteGeneratedDocuments(deleted);
        Set<Id> orphanedFiles = new Set<Id>();
        for (Id fileId : files.keySet()) {
            if (deleted.containsAll(files.get(fileId))) {
                orphanedFiles.add(fileId);
            }
        }
        deleteFiles(orphanedFiles);

        deleteCreditMemos(accountId, keptInvoiceIds);
        recordRetained(Payment.SObjectType, [SELECT COUNT() FROM Payment WHERE AccountId = :accountId], PAYMENTS_KEPT);
    }

    /**
     * True when the running user has BillingInvoiceSuperUser ("Delete Invoice and
     * Invoice Lines"), from their profile, a permission set or a group.
     * UserPermissionAccess holds the user's effective permissions, and any user may
     * read their own; a non-admin is refused PermissionSetAssignment. Dynamic, so a
     * release without the field reads as false instead of failing to compile.
     */
    @TestVisible
    private static Boolean canDeletePostedInvoices() {
        List<SObject> access;
        try {
            access = Database.query('SELECT PermissionsBillingInvoiceSuperUser FROM UserPermissionAccess');
        } catch (QueryException e) {
            return false;
        }
        return !access.isEmpty() && access[0].get('PermissionsBillingInvoiceSuperUser') == true;
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
        for (Id canceledId : updateRows(posted, 'could not be canceled')) {
            deletable.add(new CreditMemo(Id = canceledId));
        }
        deleteQuietly(deletable);
    }

    /**
     * Deletes the account's debit memos, which takes their lines with them. A
     * posted debit memo can be voided but not canceled, and Salesforce refuses to
     * delete a posted or void one even with Delete Invoice and Invoice Lines (live
     * 264), so those are kept and reported. Queried dynamically, so the class does
     * not depend on DebitMemo to deploy.
     */
    private static void deleteDebitMemos(Id accountId) {
        Schema.SObjectType memoType = Schema.getGlobalDescribe().get('DebitMemo');
        if (memoType == null) {
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
        if (orderData.orders.isEmpty()) {
            return;
        }
        for (Order o : orderData.orders) {
            o.Status = 'Draft';
        }
        updateRows(orderData.orders, null);
        deleteQuietly(orderData.orders);
    }

    /**
     * Deletes the Usage Entitlement Buckets under the given entitlements (TUEs or
     * UEAs), leaves first: a bucket cannot go while it has children. For TUE
     * buckets, the TUE a leaf bucket holds is deleted just before the bucket.
     *
     * @param entitlementIds Set of entitlement IDs (TUE or UEA)
     * @param queryType Either 'TransactionUsageEntitlement' or 'UsageEntitlementAccount'
     */
    private static void deleteUsageEntitlementBucketsBottomUp(Set<Id> entitlementIds, String queryType) {
        Boolean forTues = queryType == 'TransactionUsageEntitlement';
        List<UsageEntitlementBucket> found;
        if (forTues) {
            found = [
                SELECT Id, TransactionUsageEntitlementId, ParentId
                FROM UsageEntitlementBucket
                WHERE TransactionUsageEntitlementId IN :entitlementIds
                OR ParentId IN :entitlementIds
            ];
        } else {
            found = [
                SELECT Id, TransactionUsageEntitlementId, ParentId
                FROM UsageEntitlementBucket
                WHERE ParentId IN :entitlementIds
            ];
        }
        if (found.isEmpty()) {
            return;
        }

        // Every descendant, one level per query.
        Map<Id, UsageEntitlementBucket> buckets = new Map<Id, UsageEntitlementBucket>(found);
        Set<Id> frontier = new Set<Id>(buckets.keySet());
        while (!frontier.isEmpty()) {
            requireQueries(1);
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
                    if (forTues && leaf.TransactionUsageEntitlementId != null) {
                        heldTues.add(leaf.TransactionUsageEntitlementId);
                    }
                }
            }
            if (leaves.isEmpty()) {
                break;
            }
            if (!heldTues.isEmpty()) {
                requireQueries(1);
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
        Set<Id> tueIds = new Map<Id, TransactionUsageEntitlement>(
            [SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :accountId]).keySet();
        if (tueIds.isEmpty()) {
            return;
        }
        // Buckets first, bottom-up; that also deletes the TUEs the buckets hold.
        deleteUsageEntitlementBucketsBottomUp(tueIds, 'TransactionUsageEntitlement');
        requireQueries(1);
        deleteQuietly([SELECT Id FROM TransactionUsageEntitlement WHERE Id IN :tueIds]);
    }

    /**
     * Deletes Usage Entitlement Accounts (UEA) and their related Usage Entitlement Buckets (UEB)
     * for a given account.
     *
     * @param accountId The ID of the account whose UEAs should be deleted
     */
    private static void deleteUsageEntitlementAccount(Id accountId) {
        Set<Id> ueaIds = new Map<Id, UsageEntitlementAccount>(
            [SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :accountId]).keySet();
        if (ueaIds.isEmpty()) {
            return;
        }
        deleteUsageEntitlementBucketsBottomUp(ueaIds, 'UsageEntitlementAccount');
        requireQueries(1);
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
        for (Integer round = 1; round <= MAX_TEARDOWN_ROUNDS; round++) {
            if (Limits.getLimitQueries() - Limits.getQueries() < QUERIES_PER_ROUND + QUERY_RESERVE) {
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
        throw new ResetStoppedException(USAGE_TOO_LARGE);
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
            deleteQuietly([SELECT Id FROM UsageSummary WHERE AccountId = :accountId OR AssetId IN :assetIds]);
            deleteQuietly([SELECT Id FROM UsageRatableSummary WHERE AssetId IN :assetIds]);
            deleteQuietly([SELECT Id FROM UsageBillingPeriodItem WHERE AccountId = :accountId OR AssetId IN :assetIds]);
            allTueIds.addAll(new Map<Id, TransactionUsageEntitlement>(
                [SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :accountId]).keySet());
            allUeaIds.addAll(new Map<Id, UsageEntitlementAccount>(
                [SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :accountId]).keySet());
        }
        // TUEs bound to the assets themselves; the teardown loop only follows the account.
        allTueIds.addAll(new Map<Id, TransactionUsageEntitlement>([
            SELECT Id FROM TransactionUsageEntitlement
            WHERE AssetId IN :assetIds OR GrantBindingTargetId IN :assetIds
        ]).keySet());

        // --- 4. Delete UsageEntitlementBuckets (UEB) — blocks TUE and UEA ---
        Set<Id> bucketSearchIds = new Set<Id>(allTueIds);
        bucketSearchIds.addAll(allUeaIds);
        Set<Id> allBucketIds = new Set<Id>();
        if (!bucketSearchIds.isEmpty()) {
            allBucketIds.addAll(new Map<Id, UsageEntitlementBucket>([
                SELECT Id FROM UsageEntitlementBucket
                WHERE TransactionUsageEntitlementId IN :allTueIds
                OR ParentId IN :bucketSearchIds
            ]).keySet());
            // Recursively find child buckets until no new descendants are discovered
            Set<Id> frontier = new Set<Id>(allBucketIds);
            while (!frontier.isEmpty()) {
                requireQueries(1);
                Set<Id> next = new Map<Id, UsageEntitlementBucket>([
                    SELECT Id FROM UsageEntitlementBucket WHERE ParentId IN :frontier AND Id NOT IN :allBucketIds
                ]).keySet();
                allBucketIds.addAll(next);
                frontier = next;
            }
        }

        // Multi-pass bucket deletion (handles nested parent-child hierarchy)
        Integer before = allBucketIds.size();
        while (!allBucketIds.isEmpty()) {
            requireQueries(1);
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
            requireQueries(1);
            deleteQuietly([SELECT Id FROM TransactionUsageEntitlement WHERE Id IN :allTueIds]);
        }

        // --- 6. Delete UEAs ---
        if (!allUeaIds.isEmpty()) {
            requireQueries(1);
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
        Map<String, Schema.SObjectType> types = Schema.getGlobalDescribe();
        for (String objectName : new List<String>{ 'WorkOrder', 'Case' }) {
            if (!types.containsKey(objectName)) {
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
        deleteAll([SELECT Id FROM AssetRelationship WHERE AssetId IN :accountAssetIds]);
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
