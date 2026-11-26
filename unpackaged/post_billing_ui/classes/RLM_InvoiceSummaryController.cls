public with sharing class RLM_InvoiceSummaryController {

    public class InvoiceSummaryData {
        @AuraEnabled public Decimal totalDue;
        @AuraEnabled public Integer totalInvoices;
        @AuraEnabled public Date periodStart;
        @AuraEnabled public Date periodEnd;

        @AuraEnabled public Decimal currentAmount;
        @AuraEnabled public Integer currentCount;

        @AuraEnabled public Decimal debitAmount;
        @AuraEnabled public Integer debitCount;

        @AuraEnabled public Decimal disputeAmount;
        @AuraEnabled public Integer disputeCount;

        @AuraEnabled public Decimal overdueAmount;
        @AuraEnabled public Integer overdueCount;

        @AuraEnabled public Decimal promiseToPayAmount;
        @AuraEnabled public Integer promiseToPayCount;

        @AuraEnabled public Decimal paidAmount;
        @AuraEnabled public Integer paidCount;

        @AuraEnabled public Decimal cashCollected;
        @AuraEnabled public Integer openInvoices;
    }

    @AuraEnabled(cacheable=true)
    public static InvoiceSummaryData getInvoiceSummary(Id accountId) {
        InvoiceSummaryData data = new InvoiceSummaryData();
        Date today = Date.today();

        data.totalDue = 0;
        data.currentAmount = 0;
        data.currentCount = 0;
        data.debitAmount = 0;
        data.debitCount = 0;
        data.disputeAmount = 0;
        data.disputeCount = 0;
        data.overdueAmount = 0;
        data.overdueCount = 0;
        data.promiseToPayAmount = 0;
        data.promiseToPayCount = 0;
        data.paidAmount = 0;
        data.paidCount = 0;
        data.cashCollected = 0;
        data.openInvoices = 0;

        // Every amount here is converted into the running user's default currency at the standard
        // (CurrencyType) rates. RLM_OnAccountBillingController differs: it converts its SUM()
        // balances into the account's currency, at dated rates where advanced currency management
        // has them, else standard rates.
        Boolean isMultiCurrency = UserInfo.isMultiCurrencyOrganization();
        String targetCurrency = UserInfo.getDefaultCurrency();
        Map<String, Decimal> convRates = new Map<String, Decimal>();

        // The rates and the open invoices are what every figure on the card needs: a refused or
        // failed read of either refuses with a fixed sentence (the platform text goes to the debug
        // log), the same sentences as RLM_OnAccountBillingController. Every other read below is one
        // part of the card, which a refused read leaves unavailable (null) instead.
        if (isMultiCurrency) {
            try {
                for (SObject ct : Database.query(
                    // Every currency, active or not: a record keeps the currency it was created in.
                    'SELECT IsoCode, ConversionRate FROM CurrencyType',
                    AccessLevel.USER_MODE
                )) {
                    convRates.put((String)ct.get('IsoCode'), (Decimal)ct.get('ConversionRate'));
                }
            } catch (Exception e) {
                throw RLM_AuraErrors.failed(RATES_UNREADABLE, 'RLM_InvoiceSummaryController.getInvoiceSummary rates', e);
            }
        }

        // ── 1. Posted invoices with outstanding balance ─────────
        String invQuery = 'SELECT Id, Balance, DueDate, Status, SettlementStatus';
        if (isMultiCurrency) invQuery += ', CurrencyIsoCode';
        invQuery += ' FROM Invoice WHERE BillingAccountId = :accountId AND Status = \'Posted\' AND Balance > 0 AND SettlementStatus != \'Settled\'';
        List<SObject> invoices;
        try {
            invoices = Database.query(invQuery, AccessLevel.USER_MODE);
        } catch (Exception e) {
            throw RLM_AuraErrors.failed(INVOICES_UNREADABLE, 'RLM_InvoiceSummaryController.getInvoiceSummary invoices', e);
        }

        // ── 2. Disputes via open Cases ──────────────────────────
        // Query open cases for the account, then get Dispute records
        // linked to those cases. Sum DisputedAmount converted to the running user's currency.
        Set<Id> caseIds = openCaseIds(accountId);
        if (caseIds == null) {
            data.disputeAmount = null;
            data.disputeCount = null;
        } else {
            addDisputes(data, caseIds, isMultiCurrency, targetCurrency, convRates);
        }

        // ── 3. Debit Memos — posted for this account ────────────
        String dmQuery = 'SELECT Id, TotalAmount';
        if (isMultiCurrency) dmQuery += ', CurrencyIsoCode';
        // Not yet on a posted invoice: once it is, that invoice's balance counts it.
        dmQuery += ' FROM DebitMemo WHERE AccountId = :accountId AND Status = \'Posted\''
            + ' AND InvoiceGenerationStatus != \'Posted Invoice Generated\'';
        // A refused or failed read leaves the debit memo amount and count, and the total due that
        // includes them, null (shown as unavailable), not zero and not a failed card.
        try {
            for (SObject dm : Database.query(dmQuery, AccessLevel.USER_MODE)) {
                Decimal amt = (Decimal)dm.get('TotalAmount');
                if (amt == null || amt <= 0) continue;
                if (isMultiCurrency) {
                    amt = convertCurrency(amt, (String)dm.get('CurrencyIsoCode'), targetCurrency, convRates);
                }
                data.debitAmount += amt;
                data.debitCount++;
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'RLM_InvoiceSummaryController debit memos unavailable: '
                + e.getTypeName() + ': ' + e.getMessage());
            data.debitAmount = null;
            data.debitCount = null;
        }

        // ── 4. Promise to Pay — PSIs via CollectionPlan chain ───
        addPromisesToPay(data, accountId, isMultiCurrency, targetCurrency, convRates);

        // ── 5. Classify invoices ────────────────────────────────
        classifyInvoices(invoices, data, today, isMultiCurrency, targetCurrency, convRates);

        data.totalDue = data.debitAmount != null ? data.totalDue + data.debitAmount : null;

        // ── 6. Paid — invoices fully settled in last 30 days ────
        // Count is # of fully-settled invoices in window.
        // Amount uses NetPaymentsApplied (actual cash applied to those invoices).
        String paidInvQuery = 'SELECT ' + paidReadFields;
        if (isMultiCurrency) paidInvQuery += ', CurrencyIsoCode';
        paidInvQuery += ' FROM Invoice WHERE BillingAccountId = :accountId'
                     + ' AND Status = \'Posted\''
                     + ' AND SettlementStatus = \'Settled\''
                     + ' AND FullSettlementDate = LAST_N_DAYS:30';
        // A refused or failed read (or a currency with no rate) leaves the paid amount and count
        // unavailable (null), not zero and not a failed card.
        try {
            for (SObject inv : Database.query(paidInvQuery, AccessLevel.USER_MODE)) {
                Decimal applied = (Decimal)inv.get('NetPaymentsApplied');
                applied = applied != null ? applied : 0;
                if (isMultiCurrency) {
                    applied = convertCurrency(applied, (String)inv.get('CurrencyIsoCode'), targetCurrency, convRates);
                }
                data.paidAmount += applied;
                data.paidCount++;
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'RLM_InvoiceSummaryController paid invoices unavailable: '
                + e.getTypeName() + ': ' + e.getMessage());
            data.paidAmount = null;
            data.paidCount = null;
        }

        return data;
    }

    // The fields the paid-invoice read selects (CurrencyIsoCode is added in a multi-currency org).
    // Not final, so a test can name a field the org lacks and reach the read's failure path.
    @TestVisible
    private static String paidReadFields = 'Id, NetPaymentsApplied';

    @TestVisible
    private static final String RATES_UNREADABLE =
        'Unable to read the currency conversion rates, so this account\'s balances are not shown. Contact your administrator.';
    @TestVisible
    private static final String INVOICES_UNREADABLE =
        'Unable to read this account\'s invoices, so its balances are not shown. Contact your administrator.';

    // The account's open cases, read in USER_MODE; null when the read is refused or fails, so the
    // disputes counted through them are unavailable rather than the whole card failing. Measured on
    // a 264 org (2026-11-26): for a user without Case read, the inline WITH USER_MODE form of this
    // query raised QueryException "Variable does not exist: tmpVar1", which reached the card as raw
    // text.
    @TestVisible
    private static Set<Id> openCaseIds(Id accountId) {
        Set<Id> caseIds = new Set<Id>();
        try {
            for (SObject c : Database.query(
                'SELECT Id FROM Case WHERE AccountId = :accountId AND IsClosed = false', AccessLevel.USER_MODE
            )) {
                caseIds.add(c.Id);
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'RLM_InvoiceSummaryController open cases unavailable: '
                + e.getTypeName() + ': ' + e.getMessage());
            return null;
        }
        return caseIds;
    }

    // The Dispute fields the dispute query reads (CurrencyIsoCode is added in a multi-currency org).
    // Not final, so a test can name a field the org lacks.
    @TestVisible
    private static Set<String> disputeReadFields = new Set<String>{ 'CaseId', 'DisputedAmount' };

    // Disputes on the given open cases, summed into the running user's default currency (the
    // summary's target currency). An org without the billing dispute feature (no Dispute object, or
    // any of the fields this query reads missing) has no disputes: a real zero. A refused
    // or failed read leaves the amount and count null (shown as unavailable), never a zero that
    // reads as "no disputes" (owner rule, pack 445).
    @TestVisible
    private static void addDisputes(InvoiceSummaryData data, Set<Id> caseIds, Boolean isMultiCurrency,
            String targetCurrency, Map<String, Decimal> convRates) {
        Set<String> readFields = new Set<String>(disputeReadFields);
        if (isMultiCurrency) {
            readFields.add('CurrencyIsoCode');
        }
        if (caseIds.isEmpty() || !disputeHasFields(readFields)) {
            return;
        }
        try {
            String dispQuery = 'SELECT Id, DisputedAmount';
            if (isMultiCurrency) {
                dispQuery += ', CurrencyIsoCode';
            }
            dispQuery += ' FROM Dispute WHERE CaseId IN :caseIds';
            for (SObject d : Database.query(dispQuery, AccessLevel.USER_MODE)) {
                Decimal amt = (Decimal)d.get('DisputedAmount');
                if (amt == null || amt <= 0) continue;
                if (isMultiCurrency) {
                    amt = convertCurrency(amt, (String)d.get('CurrencyIsoCode'), targetCurrency, convRates);
                }
                data.disputeAmount += amt;
                data.disputeCount++;
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'RLM_InvoiceSummaryController disputes unavailable: '
                + e.getTypeName() + ': ' + e.getMessage());
            data.disputeAmount = null;
            data.disputeCount = null;
        }
    }

    // Promise to pay: payment schedule items under the account's collection plans. An org without
    // collections (no CollectionPlan or CollectionPlanItem object, or either link field missing) has
    // none: a real zero. A user who cannot read collection plans (a billing role without the
    // Collections and Recovery Specialist permission, which RLM_BillingCollectionsRead grants with
    // the Billing Advanced license), or whose read fails, gets null (shown as unavailable): the account
    // may have promises the user cannot see, so zero would read as "no promises".
    @TestVisible
    private static void addPromisesToPay(InvoiceSummaryData data, Id accountId, Boolean isMultiCurrency,
            String targetCurrency, Map<String, Decimal> convRates) {
        if (!collectionPlansPresent()) {
            return;
        }
        if (!canReadCollectionPlans()) {
            data.promiseToPayAmount = null;
            data.promiseToPayCount = null;
            return;
        }
        try {
            String psiQuery = 'SELECT Id, RequestedAmount, Status';
            if (isMultiCurrency) psiQuery += ', CurrencyIsoCode';
            psiQuery += ' FROM PaymentScheduleItem'
                + ' WHERE PaymentSchedule.CollectionPlanItemId != null'
                + ' AND PaymentSchedule.CollectionPlanItem.CollectionPlan.AccountId = \'' + String.escapeSingleQuotes(String.valueOf(accountId)) + '\''
                + ' AND Status NOT IN (\'Processed\', \'Canceled\')';
            for (SObject psi : Database.query(psiQuery, AccessLevel.USER_MODE)) {
                Decimal amt = (Decimal)psi.get('RequestedAmount');
                if (amt == null || amt <= 0) continue;
                if (isMultiCurrency) {
                    amt = convertCurrency(amt, (String)psi.get('CurrencyIsoCode'), targetCurrency, convRates);
                }
                data.promiseToPayAmount += amt;
                data.promiseToPayCount++;
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'RLM_InvoiceSummaryController promises to pay unavailable: '
                + e.getTypeName() + ': ' + e.getMessage());
            data.promiseToPayAmount = null;
            data.promiseToPayCount = null;
        }
    }

    /**
     * Classify posted invoices into current/overdue buckets and derive the billing-period
     * window. Extracted as a test seam so the projection can be unit-tested with synthetic
     * in-memory invoices (Invoice is system-managed and not insertable in tests).
     */
    @TestVisible
    private static void classifyInvoices(
        List<SObject> invoices, InvoiceSummaryData data, Date today,
        Boolean isMultiCurrency, String targetCurrency, Map<String, Decimal> convRates
    ) {
        Date minDate = null;
        Date maxDate = null;

        for (SObject inv : invoices) {
            Decimal bal = (Decimal)inv.get('Balance');
            Date dueDate = (Date)inv.get('DueDate');
            bal = bal != null ? bal : 0;

            if (isMultiCurrency) {
                String invCurr = (String)inv.get('CurrencyIsoCode');
                bal = convertCurrency(bal, invCurr, targetCurrency, convRates);
            }

            if (dueDate != null) {
                if (minDate == null || dueDate < minDate) minDate = dueDate;
                if (maxDate == null || dueDate > maxDate) maxDate = dueDate;
            }

            data.totalDue += bal;
            data.openInvoices++;

            if (dueDate != null && dueDate < today) {
                data.overdueAmount += bal;
                data.overdueCount++;
            } else {
                data.currentAmount += bal;
                data.currentCount++;
            }
        }

        data.totalInvoices = invoices.size();
        data.periodStart = minDate;
        data.periodEnd = maxDate != null ? maxDate : today;
    }

    // A currency with no rate is never converted at 1, which would show a foreign amount as if it
    // were in the user's currency. Inside the dispute, debit memo, promise-to-pay and paid-invoice
    // steps the throw makes that part unavailable (their catch); only for the open invoices does it
    // fail the summary, with this fixed sentence.
    @TestVisible
    private static Decimal convertCurrency(Decimal amount, String fromCurr, String toCurr, Map<String, Decimal> rates) {
        if (fromCurr == toCurr || amount == 0) return amount;
        Decimal fromRate = rates.get(fromCurr);
        Decimal toRate = rates.get(toCurr);
        if (fromRate == null || toRate == null) {
            throw RLM_AuraErrors.handled(RATE_MISSING);
        }
        return amount.divide(fromRate, 10, RoundingMode.HALF_UP) * toRate;
    }

    @TestVisible
    private static final String RATE_MISSING =
        'Unable to convert this account\'s amounts: a currency has no conversion rate. Contact your administrator.';

    // Whether the org has the collections objects and the two link fields the promise-to-pay
    // query filters on, whatever the running user can read.
    private static Boolean collectionPlansPresent() {
        Map<String, Schema.SObjectType> types = globalDescribe();
        if (!types.containsKey('CollectionPlan') || !types.containsKey('CollectionPlanItem')) {
            return false;
        }
        return Schema.SObjectType.PaymentSchedule.fields.getMap().containsKey('CollectionPlanItemId')
            && types.get('CollectionPlan').getDescribe().fields.getMap().containsKey('AccountId');
    }

    // Whether this user can run the promise-to-pay query: the collections objects and link fields
    // exist, and the user has object access to both collections objects.
    @TestVisible
    private static Boolean canReadCollectionPlans() {
        if (!collectionPlansPresent()) {
            return false;
        }
        Map<String, Schema.SObjectType> types = globalDescribe();
        for (String name : new List<String>{ 'CollectionPlan', 'CollectionPlanItem' }) {
            if (!types.get(name).getDescribe().isAccessible()) {
                return false;
            }
        }
        return true;
    }

    // Schema.getGlobalDescribe() is costly and the page asks several times: describe once per transaction.
    private static Map<String, Schema.SObjectType> describedTypes;
    private static Map<String, Schema.SObjectType> globalDescribe() {
        if (describedTypes == null) {
            describedTypes = Schema.getGlobalDescribe();
        }
        return describedTypes;
    }

    /**
     * True only when the Dispute object exists AND exposes every named field in
     * this org. Dispute and its CaseId/InvoiceId lookups are license-gated billing
     * extensions absent from a baseline build, so callers must gate dynamic SOQL
     * on this before referencing those fields.
     */
    private static Boolean disputeHasFields(Set<String> fieldNames) {
        if (!globalDescribe().containsKey('Dispute')) {
            return false;
        }
        Map<String, Schema.SObjectField> dFields =
            globalDescribe().get('Dispute').getDescribe().fields.getMap();
        for (String f : fieldNames) {
            if (!dFields.containsKey(f)) {
                return false;
            }
        }
        return true;
    }
}