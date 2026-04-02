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

        List<TaxSummaryRow> rows = new List<TaxSummaryRow>();

        for (AggregateResult ar : [
            SELECT
                TaxName taxName,
                CurrencyIsoCode currencyIsoCode,
                SUM(TaxAmount) totalTaxAmount
            FROM InvoiceLineTax
            WHERE InvoiceLine.InvoiceId = :invoiceId
            GROUP BY TaxName, CurrencyIsoCode
            ORDER BY TaxName, CurrencyIsoCode
        ]) {
            rows.add(new TaxSummaryRow(
                (String) ar.get('taxName'),
                (Decimal) ar.get('totalTaxAmount'),
                (String) ar.get('currencyIsoCode')
            ));
        }

        return rows;
    }
}