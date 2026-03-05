public with sharing class RLM_QuoteSummaryService {

    public static RLM_QuoteSummaryDTO getQuoteSummary(Id quoteId) {
        Quote q = RLM_QuoteSummaryRepository.getQuote(quoteId);

        return new RLM_QuoteSummaryDTO(
            q.Subtotal,
            q.RLM_TotalDiscountAmount__c,
            q.TotalPrice
        );
    }

    public static List<RLM_SegmentSummaryDTO> getSegmentSummaries(Id quoteId) {
        return RLM_QuoteSummaryRepository.getSegmentAggregates(quoteId);
    }
}