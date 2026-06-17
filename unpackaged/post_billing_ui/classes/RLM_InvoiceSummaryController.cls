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

        // Convert all amounts to running user's currency (matches
        // RLM_OnAccountBillingController which relies on SUM() auto-conversion)
        Boolean isMultiCurrency = UserInfo.isMultiCurrencyOrganization();
        String targetCurrency = UserInfo.getDefaultCurrency();
        Map<String, Decimal> convRates = new Map<String, Decimal>();

        if (isMultiCurrency) {
            for (SObject ct : Database.query(
                'SELECT IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true'
            )) {
                convRates.put((String)ct.get('IsoCode'), (Decimal)ct.get('ConversionRate'));
            }
        }

        // ── 1. Posted invoices with outstanding balance ─────────
        String invQuery = 'SELECT Id, Balance, DueDate, Status, SettlementStatus';
        if (isMultiCurrency) invQuery += ', CurrencyIsoCode';
        invQuery += ' FROM Invoice WHERE BillingAccountId = :accountId AND Status = \'Posted\' AND Balance > 0 AND SettlementStatus != \'Settled\'';
        List<SObject> invoices = Database.query(invQuery);

        // ── 2. Disputes via open Cases ──────────────────────────
        // Query open cases for the account, then get Dispute records
        // linked to those cases. Sum DisputedAmount converted to account currency.
        Set<Id> caseIds = new Set<Id>();
        for (Case c : [SELECT Id FROM Case WHERE AccountId = :accountId AND IsClosed = false]) {
            caseIds.add(c.Id);
        }

        Set<Id> disputedInvoiceIds = new Set<Id>();
        Map<Id, Decimal> disputeByInvoice = new Map<Id, Decimal>();

        if (!caseIds.isEmpty()) {
            String dispQuery = 'SELECT Id, DisputedAmount, InvoiceId';
            if (isMultiCurrency) {
                dispQuery += ', CurrencyIsoCode';
            }
            dispQuery += ' FROM Dispute WHERE CaseId IN :caseIds';

            for (SObject d : Database.query(dispQuery)) {
                Decimal amt = (Decimal)d.get('DisputedAmount');
                if (amt == null || amt <= 0) continue;

                // Convert to account currency if multi-currency
                if (isMultiCurrency) {
                    String dispCurr = (String)d.get('CurrencyIsoCode');
                    amt = convertCurrency(amt, dispCurr, targetCurrency, convRates);
                }

                data.disputeAmount += amt;
                data.disputeCount++;

                Id invId = (Id)d.get('InvoiceId');
                if (invId != null) {
                    disputedInvoiceIds.add(invId);
                    Decimal prev = disputeByInvoice.containsKey(invId) ? disputeByInvoice.get(invId) : 0;
                    disputeByInvoice.put(invId, prev + amt);
                }
            }
        }

        // ── 3. Debit Memos — posted for this account ────────────
        String dmQuery = 'SELECT Id, TotalAmount';
        if (isMultiCurrency) dmQuery += ', CurrencyIsoCode';
        dmQuery += ' FROM DebitMemo WHERE AccountId = :accountId AND Status = \'Posted\'';
        for (SObject dm : Database.query(dmQuery)) {
            Decimal amt = (Decimal)dm.get('TotalAmount');
            if (amt == null || amt <= 0) continue;
            if (isMultiCurrency) {
                amt = convertCurrency(amt, (String)dm.get('CurrencyIsoCode'), targetCurrency, convRates);
            }
            data.debitAmount += amt;
            data.debitCount++;
        }

        // ── 4. Promise to Pay — PSIs via CollectionPlan chain ───
        String psiQuery = 'SELECT Id, RequestedAmount, Status';
        if (isMultiCurrency) psiQuery += ', CurrencyIsoCode';
        psiQuery += ' FROM PaymentScheduleItem'
            + ' WHERE PaymentSchedule.CollectionPlanItemId != null'
            + ' AND PaymentSchedule.CollectionPlanItem.CollectionPlan.AccountId = \'' + String.escapeSingleQuotes(String.valueOf(accountId)) + '\''
            + ' AND Status NOT IN (\'Processed\', \'Canceled\')';
        for (SObject psi : Database.query(psiQuery)) {
            Decimal amt = (Decimal)psi.get('RequestedAmount');
            if (amt == null || amt <= 0) continue;
            if (isMultiCurrency) {
                amt = convertCurrency(amt, (String)psi.get('CurrencyIsoCode'), targetCurrency, convRates);
            }
            data.promiseToPayAmount += amt;
            data.promiseToPayCount++;
        }

        // ── 5. Classify invoices ────────────────────────────────
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

        data.totalDue += data.debitAmount;

        data.totalInvoices = invoices.size();
        data.periodStart = minDate;
        data.periodEnd = maxDate != null ? maxDate : today;

        // ── 6. Paid — invoices fully settled in last 30 days ────
        // Count is # of fully-settled invoices in window.
        // Amount uses NetPaymentsApplied (actual cash applied to those invoices).
        String paidInvQuery = 'SELECT Id, NetPaymentsApplied';
        if (isMultiCurrency) paidInvQuery += ', CurrencyIsoCode';
        paidInvQuery += ' FROM Invoice WHERE BillingAccountId = :accountId'
                     + ' AND Status = \'Posted\''
                     + ' AND SettlementStatus = \'Settled\''
                     + ' AND FullSettlementDate = LAST_N_DAYS:30';
        for (SObject inv : Database.query(paidInvQuery)) {
            Decimal applied = (Decimal)inv.get('NetPaymentsApplied');
            applied = applied != null ? applied : 0;
            if (isMultiCurrency) {
                applied = convertCurrency(applied, (String)inv.get('CurrencyIsoCode'), targetCurrency, convRates);
            }
            data.paidAmount += applied;
            data.paidCount++;
        }

        return data;
    }

    private static Decimal convertCurrency(Decimal amount, String fromCurr, String toCurr, Map<String, Decimal> rates) {
        if (fromCurr == toCurr || amount == 0) return amount;
        Decimal fromRate = rates.containsKey(fromCurr) ? rates.get(fromCurr) : 1;
        Decimal toRate = rates.containsKey(toCurr) ? rates.get(toCurr) : 1;
        return amount.divide(fromRate, 10, RoundingMode.HALF_UP) * toRate;
    }
}