public interface ICIPQuoteDAO {
    List<Quote> getQuoteByQuoteIdContractual(Id quoteId,List<String> fields);
    List<Quote> getQuoteByQuoteId(Set<Id> quoteId,List<String> fields);
}