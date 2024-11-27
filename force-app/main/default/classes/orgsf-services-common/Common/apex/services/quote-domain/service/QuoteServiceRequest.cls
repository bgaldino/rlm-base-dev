public with sharing class QuoteServiceRequest {
    public List<QuoteRecord> quoteRecords { get; private set; }

    public QuoteServiceRequest setQuoteRecords(List<QuoteRecord> quoteRecords) {
        this.quoteRecords = quoteRecords;
        return this;
    }

    public QuoteServiceRequest createRequest(List<QuoteRecord> quoteRecords) {
        return new QuoteServiceRequest().setQuoteRecords(quoteRecords);
    }
}
