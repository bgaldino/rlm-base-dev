public with sharing abstract class AbstractCIPQuote implements ICIPQuoteDAO{
    public virtual List<Quote> getQuoteByQuoteId(Set<Id> quoteId,List<String> fields) {
        throw new NotImplementedException();
    }
    public virtual List<Quote> getQuoteByQuoteIdContractual(Id quoteId,List<String> fields) {
        throw new NotImplementedException();
    }
}