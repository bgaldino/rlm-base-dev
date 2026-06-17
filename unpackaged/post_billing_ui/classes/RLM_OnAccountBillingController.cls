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
            List<SObject> accs = Database.query(
                'SELECT CurrencyIsoCode FROM Account WHERE Id = :accountId LIMIT 1'
            );
            if (!accs.isEmpty()) {
                accountCurrency = (String) accs[0].get('CurrencyIsoCode');
            }
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
            'Status = \'Posted\' AND TotalChargeAmount != 0',
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

        Decimal netBalance = invoiceBalance + debitMemoBalance
            - creditMemoBalance - paymentBalance + refundBalance;
        result.put('netAccountBalance', netBalance);

        // Status-related queries
        Map<String, Object> statusInfo = queryBillingStatus(accountId);
        result.putAll(statusInfo);

        return result;
    }

    private static Map<String, Object> queryBillingStatus(Id accountId) {
        Map<String, Object> info = new Map<String, Object>();
        Date today = Date.today();
        Date delinquentThreshold = today.addDays(-60);

        // Total posted invoices
        Integer totalInvoices = [
            SELECT COUNT() FROM Invoice
            WHERE BillingAccountId = :accountId AND Status = 'Posted'
        ];
        info.put('totalInvoices', totalInvoices);

        // Overdue invoices (past due date, still have balance)
        Integer overdueCount = [
            SELECT COUNT() FROM Invoice
            WHERE BillingAccountId = :accountId
              AND Status = 'Posted'
              AND Balance > 0
              AND DueDate < :today
        ];
        info.put('overdueCount', overdueCount);

        // Delinquent invoices (60+ days past due)
        Integer delinquentCount = [
            SELECT COUNT() FROM Invoice
            WHERE BillingAccountId = :accountId
              AND Status = 'Posted'
              AND Balance > 0
              AND DueDate < :delinquentThreshold
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
        ];
        info.put('openWithBalance', openWithBalance);

        // Written-off invoices
        Integer writtenOffCount = 0;
        try {
            writtenOffCount = [
                SELECT COUNT() FROM Invoice
                WHERE BillingAccountId = :accountId
                  AND Status = 'WrittenOff'
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
                + 'AND Status != \'Closed\''
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

        Decimal total = 0;
        try {
            for (AggregateResult ar : Database.query(query)) {
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
            // Object may not exist or user may lack permissions
        }
        return total;
    }

    /**
     * Salesforce SUM auto-converts using standard rates. This method reverses
     * that conversion and re-applies dated rates to match platform behavior:
     *   1. Undo standard conversion:  rawAmount = autoConverted * standardRate
     *   2. Apply dated conversion:    result    = rawAmount / datedRate * targetDatedRate
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
                'SELECT IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true'
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
                + 'WHERE StartDate <= TODAY AND NextStartDate > TODAY'
            )) {
                rates.put((String) dcr.get('IsoCode'), (Decimal) dcr.get('ConversionRate'));
            }
        } catch (Exception e) {
            // ACM not enabled
        }
        return rates;
    }
}