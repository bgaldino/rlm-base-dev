public interface ICIPQuoteLineDAO {
    List<SObject> getQuoteLinesByQuoteIdContractual(Id quoteId,List<String> fields);
    List<QuoteLineItem> getQuoteLinesByQuoteIdContractual(Set<Id> quoteId,List<String> fields);
}