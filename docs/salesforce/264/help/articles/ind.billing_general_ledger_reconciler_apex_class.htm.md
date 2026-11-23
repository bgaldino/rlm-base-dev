---
article_id: ind.billing_general_ledger_reconciler_apex_class.htm
title: TransactionJournalReconciler Apex Class
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_reconciler_apex_class.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_general_ledger_reconcile.htm
fetched_at: 2026-11-23
---

# TransactionJournalReconciler Apex Class

TransactionJournalReconciler Apex class is used to generate failed transaction journals from the payloads saved in Request field on the Revenue Transaction Error Log records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions withthe Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
/**
 * Recreates Transaction Journals that failed to generate and were logged as
 * Revenue Transaction Error Log (RTEL) records.
 *
 * For each RTEL in the "Transaction Journal Generation" category, this class reads the journal saved in the Request field, rebuilds it, and inserts it. Journals are inserted only as complete credit and debit pairs.
 *
 * Rerunning is safe: a journal that already exists is rejected as a duplicate and reported as a failure, so no duplicate journals are created.
 */

public with sharing class TransactionJournalReconciler {

    private static final String TJ_GENERATION_CATEGORY = 'Transaction Journal Generation';

    private static final Map<String, Schema.SObjectField> TJ_FIELDS =
        Schema.SObjectType.TransactionJournal.fields.getMap();

    private static final Set<String> ENUM_KEYS = new Set<String>{
        'UsageType', 'TransactionType', 'ForeignExchangeGainOrLossType'
    };

    private static final Set<String> AMOUNT_KEYS = new Set<String>{ 'Credit', 'Debit' };

    private static final Set<String> DATE_KEYS = new Set<String>{ 'ActivityDate' };

    // Maps lookup names in the payload to their Apex Id fields.
    private static final Map<String, String> LOOKUP_KEY_TO_APEX = new Map<String, String>{
        'ReferenceTransactionRecord' => 'ReferenceTransactionRecordId',
        'LegalEntity'                => 'LegalEntityId',
        'LegalEntyAccountingPeriod'  => 'LegalEntyAccountingPeriodId',
        'GeneralLedgerAcctAsgntRule' => 'GeneralLedgerAcctAsgntRuleId',
        'GenlLdgrJournalEntryRule'   => 'GenlLdgrJournalEntryRuleId',
        'CreditGeneralLedgerAccount' => 'CreditGeneralLedgerAccountId',
        'DebitGeneralLedgerAccount'  => 'DebitGeneralLedgerAccountId'
    };

    public class Result {
        public Integer errorLogsConsidered = 0;  // RTELs with a payload
        public Integer journalsParsed = 0;   // payloads read successfully
        public Integer journalsInserted = 0; // journals created
        public Integer journalsFailed = 0;   // journals that failed to insert, including duplicates
        public List<String> skippedUniqueIdentifierBases = new List<String>(); // missing their credit or debit partner
        public List<String> errors = new List<String>();
    }

    private class PendingJournal {
        TransactionJournal journal;
        Id rtelId;
        PendingJournal(TransactionJournal journal, Id rtelId) {
            this.journal = journal;
            this.rtelId = rtelId;
        }
    }

    public static Result reconcile(Set<Id> rtelIds) {
        Result result = new Result();
        if (rtelIds == null || rtelIds.isEmpty()) {
            return result;
        }

        // 1. Load the failed RTELs.
        List<RevenueTransactionErrorLog> rtels = [
            SELECT Id, Request
            FROM RevenueTransactionErrorLog
            WHERE Id IN :rtelIds
              AND Category = :TJ_GENERATION_CATEGORY
        ];
        System.debug(LoggingLevel.INFO,
            'TransactionJournalReconciler: RTEL records queried = ' + rtels.size());

        // 2. Rebuild each journal and group credit and debit sides by their shared identifier.
        Map<String, List<PendingJournal>> byBase = new Map<String, List<PendingJournal>>();
        for (RevenueTransactionErrorLog rtel : rtels) {
            if (String.isBlank(rtel.Request)) {
                continue;
            }
            result.errorLogsConsidered++;
            try {
                TransactionJournal journal = fromPayload(rtel.Request);
                result.journalsParsed++;
                String base = uniqueIdBase(journal.UniqueIdentifier);
                if (!byBase.containsKey(base)) {
                    byBase.put(base, new List<PendingJournal>());
                }
                byBase.get(base).add(new PendingJournal(journal, rtel.Id));
            } catch (Exception e) {
                result.errors.add('RTEL ' + rtel.Id + ': ' + e.getMessage());
            }
        }

        // 3. Keep only complete credit + debit pairs.
        List<PendingJournal> toPost = new List<PendingJournal>();
        for (String base : byBase.keySet()) {
            List<PendingJournal> pendingForBase = byBase.get(base);
            Boolean hasCredit = false;
            Boolean hasDebit = false;
            for (PendingJournal pending : pendingForBase) {
                if (pending.journal.Credit != null) { hasCredit = true; }
                if (pending.journal.Debit != null) { hasDebit = true; }
            }
            if (hasCredit && hasDebit) {
                toPost.addAll(pendingForBase);
            } else {
                result.skippedUniqueIdentifierBases.add(base);
            }
        }

        // 4. Insert the journals. A failure on one journal doesn't stop the others.
        if (!toPost.isEmpty()) {
            List<TransactionJournal> journals = new List<TransactionJournal>();
            for (PendingJournal pending : toPost) {
                journals.add(pending.journal);
            }

            List<Database.SaveResult> saveResults = Database.insert(journals, false);
            for (Integer i = 0; i < saveResults.size(); i++) {
                Database.SaveResult sr = saveResults[i];
                if (sr.isSuccess()) {
                    result.journalsInserted++;
                } else {
                    result.journalsFailed++;
                    String msg = '';
                    for (Database.Error err : sr.getErrors()) {
                        msg += err.getStatusCode() + ': ' + err.getMessage() + '; ';
                    }
                    result.errors.add('Insert failed (RTEL ' + toPost[i].rtelId + '): ' + msg);
                }
            }
        }

        System.debug(LoggingLevel.INFO,
            'TransactionJournalReconciler: records queried = ' + rtels.size()
            + ', processed successfully = ' + result.journalsInserted
            + ', failed again = ' + result.journalsFailed);

        return result;
    }

    /**
     * Builds a TransactionJournal from an RTEL Request payload. Only the side named in the UniqueIdentifier (-CREDIT or -DEBIT) keeps its amount and GL account, because a journal can have only one side.
     */
    private static TransactionJournal fromPayload(String payload) {
        Map<String, Object> values = (Map<String, Object>) JSON.deserializeUntyped(payload);

        String uniqueId = (String) values.get('UniqueIdentifier');
        Boolean isCredit = uniqueId != null && uniqueId.endsWithIgnoreCase('-CREDIT');
        Boolean isDebit = uniqueId != null && uniqueId.endsWithIgnoreCase('-DEBIT');

        TransactionJournal journal = new TransactionJournal();
        for (String key : values.keySet()) {
            Object value = values.get(key);
            if (value == null) {
                continue;
            }
            if (isCredit && (key == 'Debit'
                    || key == 'DebitGeneralLedgerAccount' || key == 'DebitGeneralLedgerAccountId')) {
                continue;
            }
            if (isDebit && (key == 'Credit'
                    || key == 'CreditGeneralLedgerAccount' || key == 'CreditGeneralLedgerAccountId')) {
                continue;
            }

            if (DATE_KEYS.contains(key)) {
                // Dates are stored as epoch milliseconds.
                Long millis = (value instanceof Long) ? (Long) value : Long.valueOf(String.valueOf(value));
                putIfWritable(journal, key, Datetime.newInstance(millis).dateGmt());
            } else if (AMOUNT_KEYS.contains(key)) {
                putIfWritable(journal, key, Decimal.valueOf(String.valueOf(value)));
            } else if (ENUM_KEYS.contains(key)) {
                putIfWritable(journal, key, String.valueOf(value));
            } else if (LOOKUP_KEY_TO_APEX.containsKey(key)) {
                putIfWritable(journal, LOOKUP_KEY_TO_APEX.get(key), String.valueOf(value));
            } else {
                putIfWritable(journal, key, String.valueOf(value));
            }
        }
        return journal;
    }

    /** Sets a field only if it exists on TransactionJournal in this org. */
    private static void putIfWritable(TransactionJournal journal, String fieldApiName, Object value) {
        if (fieldApiName != null && TJ_FIELDS.containsKey(fieldApiName.toLowerCase())) {
            journal.put(fieldApiName, value);
        }
    }

    /** Removes the -CREDIT or -DEBIT suffix so both sides of a pair share the same key. */
    private static String uniqueIdBase(String uniqueIdentifier) {
        if (uniqueIdentifier == null) {
            return null;
        }
        Integer lastDash = uniqueIdentifier.lastIndexOf('-');
        return lastDash > 0 ? uniqueIdentifier.substring(0, lastDash) : uniqueIdentifier;
    }
}

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_reconciler_apex_class.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
