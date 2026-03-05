public with sharing class RLM_QuoteSummaryController {

    @AuraEnabled(cacheable=true)
    public static RLM_QuoteSummaryDTO getQuoteSummary(Id quoteId) {
        return RLM_QuoteSummaryService.getQuoteSummary(quoteId);
    }

    @AuraEnabled
public static List<RLM_SegmentSummaryDTO> getSegmentSummaries(Id quoteId) {
    return RLM_QuoteSummaryService.getSegmentSummaries(quoteId);
}

}