public interface IQuoteLineItemDPPValidationService {
    void validateQuoteLineItems(List<QuoteLineItem> quoteLineItems);
    void validateQuoteIds(Set<Id> quoteIds);
    void validateQuoteLineByQuoteId(Map<Id, List<QuoteLineItem>> quotelineItemByQuoteIdMap);
}
