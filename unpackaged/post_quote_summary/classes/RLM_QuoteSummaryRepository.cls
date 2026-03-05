public with sharing class RLM_QuoteSummaryRepository {

    // ------------------------------------------------------------
    // Quote Header Summary
    // ------------------------------------------------------------
    public static Quote getQuote(Id quoteId) {
        return [
            SELECT Id,
                   Subtotal,
                   RLM_TotalDiscountAmount__c,
                   TotalPrice
            FROM Quote
            WHERE Id = :quoteId
            LIMIT 1
        ];
    }

    // ------------------------------------------------------------
    // Segment Aggregates (Flow-first, RLM-safe)
    // ------------------------------------------------------------
    public static List<RLM_SegmentSummaryDTO> getSegmentAggregates(Id quoteId) {

        // NOTE:
        // We intentionally do NOT filter RLM_* fields in WHERE
        // because RLM creates non-segmented / shadow QLI rows.
        // Filtering is done post-aggregation in Apex.
        // Use a local bind variable — Database.query() resolves binds from the enclosing scope
        Id quoteIdBind = quoteId;
        String soql =
            'SELECT RLM_RampKey__c ramp, ' +
                     'RLM_SegmentKey__c seg, ' +
                     'RLM_SegmentLabel__c label, ' +
                     'SUM(Subtotal) subtotal, ' +
                     'SUM(TotalAdjustmentAmount) discount, ' +
                     'SUM(TotalPrice) total ' +
            'FROM QuoteLineItem ' +
            'WHERE QuoteId = :quoteIdBind ' +
            'GROUP BY RLM_RampKey__c, RLM_SegmentKey__c, RLM_SegmentLabel__c ' +
            'ORDER BY RLM_RampKey__c, RLM_SegmentKey__c';

        List<AggregateResult> rows =
            (List<AggregateResult>) Database.query(soql);

        List<RLM_SegmentSummaryDTO> results = new List<RLM_SegmentSummaryDTO>();

        for (AggregateResult ar : rows) {

            // 🚨 Skip non-segmented / bundle / shadow rows
            if (ar.get('seg') == null) {
                continue;
            }

            results.add(new RLM_SegmentSummaryDTO(
                (String) ar.get('ramp'),
                (String) ar.get('seg'),
                (String) ar.get('label'),
                (Decimal) ar.get('subtotal'),
                (Decimal) ar.get('discount'),
                (Decimal) ar.get('total')
            ));
        }

        return results;
    }
}