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
            // WITH USER_MODE raises this, not a QueryException, when the object itself is refused.
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
            // Field may not be accessible
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
            // Status value may not exist
        }
        info.put('writtenOffCount', writtenOffCount);

        // Open disputes
        Integer disputeCount = 0;
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
            // Dispute object may not be available
        }
        info.put('disputeCount', disputeCount);

        // Collections — check if any CollectionPlan records exist for this account
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
            // CollectionPlan object may not be available
        }
        info.put('inCollections', inCollections);

        return info;
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

        if (!Schema.getGlobalDescribe().containsKey(objectName)) {
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
     */
    private static Decimal correctConversion(
        Decimal autoConverted, String fromCurrency, String toCurrency,
        Map<String, Decimal> standardRates, Map<String, Decimal> datedRates
    ) {
        if (fromCurrency == toCurrency || autoConverted == 0) {
            return autoConverted;
        }
        Decimal stdFromRate   = standardRates.containsKey(fromCurrency) ? standardRates.get(fromCurrency) : 1;
        Decimal datedFromRate = datedRates.containsKey(fromCurrency) ? datedRates.get(fromCurrency) : 1;
        Decimal datedToRate   = datedRates.containsKey(toCurrency)   ? datedRates.get(toCurrency)   : 1;

        Decimal rawAmount = autoConverted * stdFromRate;
        return rawAmount.divide(datedFromRate, 10, RoundingMode.HALF_UP) * datedToRate;
    }

    private static Map<String, Decimal> loadStandardRates() {
        Map<String, Decimal> rates = new Map<String, Decimal>();
        try {
            for (SObject ct : Database.query(
                'SELECT IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true',
                AccessLevel.USER_MODE
            )) {
                rates.put((String) ct.get('IsoCode'), (Decimal) ct.get('ConversionRate'));
            }
        } catch (Exception e) {
            // Not available
        }
        return rates;
    }

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