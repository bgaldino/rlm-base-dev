public with sharing class RLM_InvoiceTaxSummaryController {
    public class TaxSummaryRow {
        @AuraEnabled public String taxName;
        @AuraEnabled public Decimal totalTaxAmount;
        @AuraEnabled public String currencyIsoCode;

        public TaxSummaryRow(String taxName, Decimal totalTaxAmount, String currencyIsoCode) {
            this.taxName = taxName;
            this.totalTaxAmount = totalTaxAmount;
            this.currencyIsoCode = currencyIsoCode;
        }
    }

    @AuraEnabled(cacheable=true)
    public static List<TaxSummaryRow> getTaxSummaryByInvoice(Id invoiceId) {
        if (invoiceId == null) {
            return new List<TaxSummaryRow>();
        }

        List<Map<String, Object>> groups = new List<Map<String, Object>>();
        for (AggregateResult ar : [
            SELECT
                TaxName taxName,
                CurrencyIsoCode currencyIsoCode,
                SUM(TaxAmount) totalTaxAmount
            FROM InvoiceLineTax
            WHERE InvoiceLine.InvoiceId = :invoiceId
            WITH USER_MODE GROUP BY TaxName, CurrencyIsoCode
            ORDER BY TaxName, CurrencyIsoCode
        ]) {
            groups.add(ar.getPopulatedFieldsAsMap());
        }

        return toRows(groups);
    }

    // One row per aggregate group, in query order. Each map is an AggregateResult's
    // getPopulatedFieldsAsMap(): its keys are the query's aliases with their case as written,
    // and the lookup is case-sensitive, so the keys below must match those aliases exactly.
    @TestVisible
    private static List<TaxSummaryRow> toRows(List<Map<String, Object>> groups) {
        List<TaxSummaryRow> rows = new List<TaxSummaryRow>();
        for (Map<String, Object> g : groups) {
            rows.add(new TaxSummaryRow(
                (String) g.get('taxName'),
                (Decimal) g.get('totalTaxAmount'),
                (String) g.get('currencyIsoCode')
            ));
        }
        return rows;
    }
}
