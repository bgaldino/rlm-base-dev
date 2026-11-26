public with sharing class RLM_OnAccountBillingController {

    @AuraEnabled(cacheable=true)
    public static Map<String, Object> getBillingSummary(Id accountId) {
        Map<String, Object> result = new Map<String, Object>();
        if (accountId == null) {
            return result;
        }

        Boolean isMultiCurrency = UserInfo.isMultiCurrencyOrganization();
        String accountCurrency = 'USD';
        Map<String, Decimal> standardRates = new Map<String, Decimal>();
        Map<String, Decimal> datedRates = new Map<String, Decimal>();

        if (isMultiCurrency) {
            accountCurrency = currencyOf(accountId);
            standardRates = loadStandardRates();
            datedRates = loadDatedRates();
            if (datedRates.isEmpty()) {
                datedRates = standardRates;
            }
        }

        result.put('currencyIsoCode', accountCurrency);
        result.put('isMultiCurrency', isMultiCurrency);

        Decimal invoiceBalance = queryAggregate(
            'Invoice', 'Balance', 'BillingAccountId',
            'Status = \'Posted\' AND Balance != 0',
            accountId, accountCurrency, standardRates, datedRates, isMultiCurrency
        );
        result.put('invoiceBalance', invoiceBalance);

        Decimal debitMemoBalance = queryAggregate(
            'DebitMemo', 'TotalChargeAmount', 'AccountId',
            // Not yet on a posted invoice: once it is, the invoice balance above counts it.
            'Status = \'Posted\' AND TotalChargeAmount != 0'
                + ' AND InvoiceGenerationStatus != \'Posted Invoice Generated\'',
            accountId, accountCurrency, standardRates, datedRates, isMultiCurrency
        );
        result.put('debitMemoBalance', debitMemoBalance);

        Decimal creditMemoBalance = queryAggregate(
            'CreditMemo', 'Balance', 'BillingAccountId',
            'Status = \'Posted\' AND Balance != 0',
            accountId, accountCurrency, standardRates, datedRates, isMultiCurrency
        );
        result.put('creditMemoBalance', creditMemoBalance);

        Decimal paymentBalance = queryAggregate(
            'Payment', 'Balance', 'AccountId',
            'Status = \'Processed\' AND Balance != 0',
            accountId, accountCurrency, standardRates, datedRates, isMultiCurrency
        );
        result.put('paymentBalance', paymentBalance);

        Decimal refundBalance = queryAggregate(
            'Refund', 'Balance', 'AccountId',
            'Status = \'Processed\' AND Balance != 0',
            accountId, accountCurrency, standardRates, datedRates, isMultiCurrency
        );
        result.put('refundBalance', refundBalance);

        // A balance whose read was refused is null (shown as unavailable), and so is the net
        // balance: a refused part is never counted as zero (owner rule, pack 445).
        result.put('netAccountBalance', netOf(invoiceBalance, debitMemoBalance, creditMemoBalance, paymentBalance, refundBalance));

        // Status-related queries
        Map<String, Object> statusInfo = queryBillingStatus(accountId);
        result.putAll(statusInfo);

        return result;
    }

    @TestVisible
    private static Decimal netOf(Decimal invoiceBalance, Decimal debitMemoBalance, Decimal creditMemoBalance,
            Decimal paymentBalance, Decimal refundBalance) {
        if (invoiceBalance == null || debitMemoBalance == null || creditMemoBalance == null
                || paymentBalance == null || refundBalance == null) {
            return null;
        }
        return invoiceBalance + debitMemoBalance - creditMemoBalance - paymentBalance + refundBalance;
    }

    private static final String INVOICES_UNREADABLE =
        'Unable to read this account\'s invoices, so its balances are not shown. Contact your administrator.';

    // The account's currency, which every balance below is converted into. A refused Account read
    // must not fall back to USD: the balances would then show in the wrong currency as if real.
    // So the user gets a fixed sentence, and the platform text goes to the debug log only.
    // An account the user cannot see (empty result) keeps the USD default, as before.
    @TestVisible
    private static String currencyOf(Id accountId) {
        try {
            List<SObject> accs = Database.query(
                'SELECT CurrencyIsoCode FROM Account WHERE Id = :accountId LIMIT 1',
                AccessLevel.USER_MODE
            );
            if (!accs.isEmpty()) {
                return (String) accs[0].get('CurrencyIsoCode');
            }
        } catch (QueryException e) {
            throw RLM_AuraErrors.failed(
                'Unable to read the account\'s currency, so its balances are not shown. Contact your administrator.',
                'RLM_OnAccountBillingController.currencyOf', e);
        }
        return 'USD';
    }

    // The invoice counts drive the status pill, and every card needs them: a refused Invoice read
    // reports a fixed sentence (the platform text goes to the debug log), as the currency read does,
    // instead of a raw query error or counts of zero that would read as "no billing activity".
    private static Map<String, Object> queryBillingStatus(Id accountId) {
        try {
            return queryInvoiceStatus(accountId);
        } catch (QueryException e) {
            throw RLM_AuraErrors.failed(INVOICES_UNREADABLE, 'RLM_OnAccountBillingController.queryBillingStatus', e);
        } catch (SecurityException e) {
            // Measured on a 264 scratch org (deploy 0AfWt00000hUL33KAG, 2026-11-26, a test user
            // with no Invoice read): the first inline WITH USER_MODE COUNT() below raised
            // System.SecurityException "Access to entity 'Invoice' denied". The tests' dynamic
            // Database.query(..., AccessLevel.USER_MODE) probes of a refused object raised
            // QueryException. Both are caught; which inline queries raise which is not measured.
            throw RLM_AuraErrors.failed(INVOICES_UNREADABLE, 'RLM_OnAccountBillingController.queryBillingStatus', e);
        }
    }

    private static Map<String, Object> queryInvoiceStatus(Id accountId) {
        Map<String, Object> info = new Map<String, Object>();
        Date today = Date.today();
        Date delinquentThreshold = today.addDays(-60);

        // Total posted invoices
        Integer totalInvoices = [
            SELECT COUNT() FROM Invoice
            WHERE BillingAccountId = :accountId AND Status = 'Posted'
            WITH USER_MODE
        ];
        info.put('totalInvoices', totalInvoices);

        // Overdue invoices (past due date, still have balance)
        Integer overdueCount = [
            SELECT COUNT() FROM Invoice
            WHERE BillingAccountId = :accountId
              AND Status = 'Posted'
              AND Balance > 0
              AND DueDate < :today
            WITH USER_MODE
        ];
        info.put('overdueCount', overdueCount);

        // Delinquent invoices (60+ days past due)
        Integer delinquentCount = [
            SELECT COUNT() FROM Invoice
            WHERE BillingAccountId = :accountId
              AND Status = 'Posted'
              AND Balance > 0
              AND DueDate < :delinquentThreshold
            WITH USER_MODE
        ];
        info.put('delinquentCount', delinquentCount);

        // Four reads below are optional to the summary: partially-paid overdue, written-off, disputes
        // and collections (the open-with-balance count between them is not). A refused or failed one
        // gives null (shown as unavailable), never a zero or false that reads as "none" (owner rule,
        // pack 445).
        // An org without the Dispute object, or without the license-gated Dispute fields the count
        // reads, has no disputes, so that count is a real zero.

        // Overdue invoices that have partial payments applied (Balance < TotalAmountWithTax)
        Integer partiallyPaidOverdueCount = 0;
        try {
            for (Invoice inv : [
                SELECT Id, Balance, TotalAmountWithTax FROM Invoice
                WHERE BillingAccountId = :accountId
                  AND Status = 'Posted'
                  AND Balance > 0
                  AND DueDate < :today
                WITH USER_MODE
            ]) {
                if (inv.Balance < inv.TotalAmountWithTax) {
                    partiallyPaidOverdueCount++;
                }
            }
        } catch (Exception e) {
            partiallyPaidOverdueCount = unavailable('partiallyPaidOverdueCount', e);
        }
        info.put('partiallyPaidOverdueCount', partiallyPaidOverdueCount);

        // Open invoices with balance
        Integer openWithBalance = [
            SELECT COUNT() FROM Invoice
            WHERE BillingAccountId = :accountId
              AND Status = 'Posted'
              AND Balance > 0
            WITH USER_MODE
        ];
        info.put('openWithBalance', openWithBalance);

        // Written-off invoices
        Integer writtenOffCount = 0;
        try {
            writtenOffCount = [
                SELECT COUNT() FROM Invoice
                WHERE BillingAccountId = :accountId
                  AND Status = 'WrittenOff'
                WITH USER_MODE
            ];
        } catch (Exception e) {
            // An unknown picklist value in the filter matches no rows rather than throwing, so a
            // failure here is a refused or failed read.
            writtenOffCount = unavailable('writtenOffCount', e);
        }
        info.put('writtenOffCount', writtenOffCount);

        // Open disputes
        Integer disputeCount = 0;
        if (disputeFieldsPresent()) {
            try {
                List<AggregateResult> dRes = Database.query(
                    'SELECT COUNT(Id) cnt FROM Dispute '
                    + 'WHERE Invoice.BillingAccountId = :accountId '
                    + 'AND Status != \'Closed\'',
                    AccessLevel.USER_MODE
                );
                if (!dRes.isEmpty() && dRes[0].get('cnt') != null) {
                    disputeCount = (Integer) dRes[0].get('cnt');
                }
            } catch (Exception e) {
                disputeCount = unavailable('disputeCount', e);
            }
        }
        info.put('disputeCount', disputeCount);

        // Collections — check if any CollectionPlan records exist for this account
        // CollectionPlan is named in static SOQL, so it exists wherever this class compiles: a
        // failure is a refused or failed read, and the account may be in collections.
        Boolean inCollections = false;
        try {
            Integer collectionPlanCount = [
                SELECT COUNT() FROM CollectionPlan
                WHERE AccountId = :accountId
                WITH USER_MODE
                LIMIT 1
            ];
            inCollections = collectionPlanCount > 0;
        } catch (Exception e) {
            unavailable('inCollections', e);
            inCollections = null;
        }
        info.put('inCollections', inCollections);

        return info;
    }

    // The Dispute fields the dispute count reads. InvoiceId and the other billing dispute fields
    // are license-gated extensions absent from a baseline build (see
    // RLM_InvoiceSummaryController.disputeHasFields). Not final, so a test can name a field the
    // org lacks.
    @TestVisible
    private static Set<String> disputeFields = new Set<String>{ 'InvoiceId', 'Status' };

    // True only when the Dispute object exists and has every field in disputeFields.
    private static Boolean disputeFieldsPresent() {
        Schema.SObjectType dispute = globalDescribe().get('Dispute');
        if (dispute == null) {
            return false;
        }
        Map<String, Schema.SObjectField> fields = dispute.getDescribe().fields.getMap();
        for (String name : disputeFields) {
            if (!fields.containsKey(name)) {
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

    // Logs a refused or failed optional status read; returns null for the caller to report.
    private static Integer unavailable(String key, Exception e) {
        System.debug(LoggingLevel.WARN, 'RLM_OnAccountBillingController.' + key + ' unavailable: '
            + e.getTypeName() + ': ' + e.getMessage());
        return null;
    }

    /**
     * Aggregate query with currency correction.
     * Salesforce auto-converts SUM amounts in multi-currency orgs using standard
     * CurrencyType rates, even with GROUP BY CurrencyIsoCode. To use dated rates
     * instead, we reverse the standard conversion and re-apply the dated rate.
     * Returns null, not zero, when the read is refused or fails, so the caller shows the balance
     * (and the net balance) as unavailable. An org without the object has none of its records,
     * so that balance is a real zero.
     */
    private static Decimal queryAggregate(
        String objectName, String sumField, String accountField,
        String conditions, Id accountId, String targetCurrency,
        Map<String, Decimal> standardRates, Map<String, Decimal> datedRates,
        Boolean isMultiCurrency
    ) {
        String query = 'SELECT SUM(' + sumField + ') total';
        if (isMultiCurrency) {
            query += ', CurrencyIsoCode curr';
        }
        query += ' FROM ' + objectName
              + ' WHERE ' + accountField + ' = :accountId AND ' + conditions;
        if (isMultiCurrency) {
            query += ' GROUP BY CurrencyIsoCode';
        }

        if (!globalDescribe().containsKey(objectName)) {
            return 0;
        }
        Decimal total = 0;
        try {
            for (AggregateResult ar : Database.query(query, AccessLevel.USER_MODE)) {
                Decimal amount = ar.get('total') != null ? (Decimal) ar.get('total') : 0;
                if (isMultiCurrency) {
                    String sourceCurrency = (String) ar.get('curr');
                    amount = correctConversion(
                        amount, sourceCurrency, targetCurrency,
                        standardRates, datedRates
                    );
                    if (amount == null) {
                        // A currency with no rate: the balance is unavailable, never converted at 1.
                        System.debug(LoggingLevel.WARN, 'RLM_OnAccountBillingController.queryAggregate ' + objectName
                            + ' unavailable: no conversion rate for ' + sourceCurrency + ' or ' + targetCurrency);
                        return null;
                    }
                }
                total += amount;
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'RLM_OnAccountBillingController.queryAggregate ' + objectName
                + ' unavailable: ' + e.getTypeName() + ': ' + e.getMessage());
            return null;
        }
        return total;
    }

    /**
     * Salesforce SUM auto-converts using standard rates. This method reverses
     * that conversion and re-applies dated rates to match platform behavior:
     *   1. Undo standard conversion:  rawAmount = autoConverted * standardRate
     *   2. Apply dated conversion:    result    = rawAmount / datedRate * targetDatedRate
     *
     * Accepted behavior (owner decision, 2026-11-25, pack 433): when the group currency equals the
     * target currency this returns the auto-converted SUM unchanged. SUM() has already converted
     * into the corporate currency, so when the account and its invoices, memos, payments or refunds
     * share a non-corporate currency, each such balance (and the net balance) shows the
     * corporate-converted figure labelled in the account currency (pinned for payments by
     * RLM_OnAccountBillingControllerTest). Revisit only if a customer reports a mismatch.
     *
     * Returns null when a rate it needs is missing, never a rate of 1, which would show a foreign
     * balance unconverted as if it were real. The standard rates include inactive currencies (see
     * loadStandardRates), so a record in a since-deactivated currency still has its rate.
     */
    @TestVisible
    private static Decimal correctConversion(
        Decimal autoConverted, String fromCurrency, String toCurrency,
        Map<String, Decimal> standardRates, Map<String, Decimal> datedRates
    ) {
        if (fromCurrency == toCurrency || autoConverted == 0) {
            return autoConverted;
        }
        Decimal stdFromRate   = standardRates.get(fromCurrency);
        Decimal datedFromRate = datedRates.get(fromCurrency);
        Decimal datedToRate   = datedRates.get(toCurrency);
        if (stdFromRate == null || datedFromRate == null || datedToRate == null) {
            return null;
        }

        Decimal rawAmount = autoConverted * stdFromRate;
        return rawAmount.divide(datedFromRate, 10, RoundingMode.HALF_UP) * datedToRate;
    }

    @TestVisible
    private static Map<String, Decimal> loadStandardRates() {
        Map<String, Decimal> rates = new Map<String, Decimal>();
        try {
            for (SObject ct : Database.query(
                // Every currency, active or not: a record keeps the currency it was created in, so a
                // since-deactivated currency still needs its rate (none is inactive on the 264 org
                // measured, so whether a deactivated currency keeps its rate is not measured).
                'SELECT IsoCode, ConversionRate FROM CurrencyType',
                AccessLevel.USER_MODE
            )) {
                rates.put((String) ct.get('IsoCode'), (Decimal) ct.get('ConversionRate'));
            }
        } catch (Exception e) {
            // Without the standard rates every foreign-currency balance would be summed at rate 1,
            // a figure that looks real but is wrong: refuse with a fixed sentence, as currencyOf does.
            // Not reached by any restricted user measured: a Minimum Access user with no permission
            // sets still reads CurrencyType (264 org, 2026-11-26).
            throw RLM_AuraErrors.failed(RATES_UNREADABLE, 'RLM_OnAccountBillingController.loadStandardRates', e);
        }
        return rates;
    }

    private static final String RATES_UNREADABLE =
        'Unable to read the currency conversion rates, so this account\'s balances are not shown. Contact your administrator.';

    private static Map<String, Decimal> loadDatedRates() {
        Map<String, Decimal> rates = new Map<String, Decimal>();
        try {
            for (SObject dcr : Database.query(
                'SELECT IsoCode, ConversionRate FROM DatedConversionRate '
                + 'WHERE StartDate <= TODAY AND NextStartDate > TODAY',
                AccessLevel.USER_MODE
            )) {
                rates.put((String) dcr.get('IsoCode'), (Decimal) dcr.get('ConversionRate'));
            }
        } catch (Exception e) {
            // ACM not enabled
        }
        return rates;
    }
}