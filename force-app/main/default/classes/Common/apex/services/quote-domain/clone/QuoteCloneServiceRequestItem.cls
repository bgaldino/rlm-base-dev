public with sharing class QuoteCloneServiceRequestItem extends BaseRequestItem {
    public Quote quote { get; set; }

    public QuoteCloneServiceRequestItem(Quote quote) {
         this.quote = quote;
    }
}