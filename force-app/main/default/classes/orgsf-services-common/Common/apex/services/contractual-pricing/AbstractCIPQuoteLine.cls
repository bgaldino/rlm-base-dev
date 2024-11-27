public with sharing abstract class AbstractCIPQuoteLine implements ICIPQuoteLineDAO{
    public virtual List<SObject> getQuoteLinesByQuoteIdContractual(Id quoteId,List<String> fields) {
        throw new NotImplementedException();
    }
    public virtual List<QuoteLineItem> getQuoteLinesByQuoteIdContractual(Set<Id> quoteId,List<String> fields) {
        throw new NotImplementedException();
    }
}