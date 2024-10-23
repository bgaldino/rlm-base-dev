public with sharing class QuoteLineServiceRequest{
    
    public List<QuoteLine> quoteLines  {get; private set;} 
    public Id quoteId {get; private set;} 
 
    public QuoteLineServiceRequest setQuoteLines(List<QuoteLine> quoteLines) {
        this.quoteLines = quoteLines;
        return this;
    }
    
    public QuoteLineServiceRequest setQuoteId(Id quoteId) {
        this.quoteId = quoteId;
        return this;
    }

    public QuoteLineServiceRequest createRequest(List<QuoteLine> quoteLines) {
        return new QuoteLineServiceRequest().setQuoteLines(quoteLines);
    }
    
    public QuoteLineServiceRequest createRequest(List<QuoteLine> quoteLines, Id quoteId) {
        return new QuoteLineServiceRequest().setQuoteLines(quoteLines).setQuoteId(quoteId);
    }
}