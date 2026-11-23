---
article_id: ind.billing_general_ledger_reconciler_batch_apex_class.htm
title: TransactionJournalBatchReconciler Apex Class
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_reconciler_batch_apex_class.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_general_ledger_reconcile.htm
fetched_at: 2026-11-23
---

# TransactionJournalBatchReconciler Apex Class

Runs TransactionJournalReconciler in batches so you can reconcile large numbers of RTELs across batches.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions withthe Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
/**
 * Runs TransactionJournalReconciler in batches so that you can reconcile a large number of RTELs without hitting Apex governor limits. Deploy TransactionJournalReconciler first.
 *
 * The credit and debit sides of a journal are always reconciled together, even when they land in different batches. Any side whose partner isn't found is reported as unpaired.
 * Track progress in Setup > Apex Jobs. Final totals are written to the debug log.
 */
public with sharing class TransactionJournalBatchReconciler
        implements Database.Batchable<SObject>, Database.Stateful {

    private static final String TJ_GENERATION_CATEGORY = 'Transaction Journal Generation';

    // Limits how many error messages are kept in memory.
    private static final Integer MAX_ERRORS_KEPT = 200;

    private final Set<Id> rtelIds;

    // Sides waiting for their partner, keyed by shared identifier.
    private Map<String, List<Id>> pendingCredits = new Map<String, List<Id>>();
    private Map<String, List<Id>> pendingDebits = new Map<String, List<Id>>();

    private Integer errorLogsConsidered = 0;
    private Integer journalsParsed = 0;
    private Integer journalsInserted = 0;
    private Integer journalsFailed = 0;
    private Integer errorsTotal = 0;
    private List<String> skippedUniqueIdentifierBases = new List<String>();
    private List<String> errors = new List<String>();

    public TransactionJournalBatchReconciler() {
        this(null);
    }

    public TransactionJournalBatchReconciler(Set<Id> rtelIds) {
        this.rtelIds = rtelIds;
    }

    public Database.QueryLocator start(Database.BatchableContext bc) {
        if (rtelIds != null) {
            return Database.getQueryLocator([
                SELECT Id, Request
                FROM RevenueTransactionErrorLog
                WHERE Id IN :rtelIds
                  AND Category = :TJ_GENERATION_CATEGORY
                ORDER BY Id
            ]);
        }
        return Database.getQueryLocator([
            SELECT Id, Request
            FROM RevenueTransactionErrorLog
            WHERE Category = :TJ_GENERATION_CATEGORY
            ORDER BY Id
        ]);
    }

    public void execute(Database.BatchableContext bc, List<RevenueTransactionErrorLog> scope) {
        List<Id> readyToReconcile = new List<Id>();
        Set<String> touchedBases = new Set<String>();

        // Sort each RTEL into credit or debit. Anything else goes straight to the
        // reconciler, which reports it.
        for (RevenueTransactionErrorLog rtel : scope) {
            if (String.isBlank(rtel.Request)) {
                continue;
            }
            String uniqueId = readUniqueIdentifier(rtel.Request);
            Boolean isCredit = uniqueId != null && uniqueId.endsWithIgnoreCase('-CREDIT');
            Boolean isDebit = uniqueId != null && uniqueId.endsWithIgnoreCase('-DEBIT');
            if (!isCredit && !isDebit) {
                readyToReconcile.add(rtel.Id);
                continue;
            }
            String base = uniqueIdBase(uniqueId);
            touchedBases.add(base);
            Map<String, List<Id>> sideMap = isCredit ? pendingCredits : pendingDebits;
            if (!sideMap.containsKey(base)) {
                sideMap.put(base, new List<Id>());
            }
            sideMap.get(base).add(rtel.Id);
        }

        // Send a pair only once both its credit and debit sides have been found.
        for (String base : touchedBases) {
            if (pendingCredits.containsKey(base) && pendingDebits.containsKey(base)) {
                readyToReconcile.addAll(pendingCredits.remove(base));
                readyToReconcile.addAll(pendingDebits.remove(base));
            }
        }

        if (readyToReconcile.isEmpty()) {
            return;
        }

        TransactionJournalReconciler.Result r =
            TransactionJournalReconciler.reconcile(new Set<Id>(readyToReconcile));

        errorLogsConsidered += r.errorLogsConsidered;
        journalsParsed += r.journalsParsed;
        journalsInserted += r.journalsInserted;
        journalsFailed += r.journalsFailed;
        skippedUniqueIdentifierBases.addAll(r.skippedUniqueIdentifierBases);
        errorsTotal += r.errors.size();
        for (String err : r.errors) {
            if (errors.size() >= MAX_ERRORS_KEPT) {
                break;
            }
            errors.add(err);
        }
    }

    public void finish(Database.BatchableContext bc) {
        // Anything still waiting never found its partner.
        Set<String> unpaired = new Set<String>(pendingCredits.keySet());
        unpaired.addAll(pendingDebits.keySet());
        skippedUniqueIdentifierBases.addAll(unpaired);

        AsyncApexJob job = [
            SELECT Status, NumberOfErrors, JobItemsProcessed, TotalJobItems
            FROM AsyncApexJob
            WHERE Id = :bc.getJobId()
        ];

        System.debug(LoggingLevel.INFO,
            'TransactionJournalBatchReconciler: job status = ' + job.Status
            + ', batches = ' + job.JobItemsProcessed + '/' + job.TotalJobItems
            + ', batch failures = ' + job.NumberOfErrors
            + ', rtels considered = ' + errorLogsConsidered
            + ', journals parsed = ' + journalsParsed
            + ', processed successfully = ' + journalsInserted
            + ', failed again = ' + journalsFailed
            + ', unpaired skipped = ' + skippedUniqueIdentifierBases.size()
            + ', error messages = ' + errorsTotal
            + (errorsTotal > errors.size() ? ' (first ' + errors.size() + ' kept)' : ''));
        for (String base : skippedUniqueIdentifierBases) {
            System.debug(LoggingLevel.WARN, 'TransactionJournalBatchReconciler: unpaired ' + base);
        }
        for (String err : errors) {
            System.debug(LoggingLevel.ERROR, 'TransactionJournalBatchReconciler: ' + err);
        }
    }

    /** Reads UniqueIdentifier from the payload, or returns null if it can't be read. */
    private static String readUniqueIdentifier(String payload) {
        try {
            Map<String, Object> values = (Map<String, Object>) JSON.deserializeUntyped(payload);
            Object uniqueId = values.get('UniqueIdentifier');
            return uniqueId == null ? null : String.valueOf(uniqueId);
        } catch (Exception e) {
            return null;
        }
    }

    /** Removes the -CREDIT or -DEBIT suffix. */
    private static String uniqueIdBase(String uniqueIdentifier) {
        Integer lastDash = uniqueIdentifier.lastIndexOf('-');
        return lastDash > 0 ? uniqueIdentifier.substring(0, lastDash) : uniqueIdentifier;
    }
}

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_reconciler_batch_apex_class.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
