public interface IQuoteLineDAO {
    void insertLines(List<QuoteLineItem> lines);
    void updateLines(List<QuoteLineItem> lines);
    void deleteLines(List<QuoteLineItem> lines);
    void updateOpportunityLines(List<OpportunityLineItem> opportunityLines);
    List<QuoteLineItem> getQuoteLinesByQuoteId(Id quoteId);
    List<QuoteLineItem> getUsageQuoteLinesByQuoteId(Id quoteId);
    List<QuoteLineItem> getQuoteLinesByQuoteIds(Set<Id> quoteIds);
    List<QuoteLineItem> getQuoteLinesByQuoteIdsConvertCurrencies(Set<Id> quoteIds);
    List<QuoteLineItem> getQuoteLineByIds(Set<Id> quoteLineids);
    List<QuoteLineItem> getQuoteLinesForSync(Set<Id> quoteIds);
    List<ProductSellingModel> getProductSellingModel(Set<Id> psmIdList);
}