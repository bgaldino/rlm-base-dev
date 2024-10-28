public with sharing class QuoteCloneServiceResponseItem extends BaseResponseItem {
    public Id clonedQuoteId { get; set; }
    public ErrorCollector qliErrorCollector { get; set; }

    public QuoteCloneServiceResponseItem(String requestId) {
        super(requestId);
    }
}