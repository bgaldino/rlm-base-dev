public with sharing class QuoteLineTriggerDataBag {
    public Set<Id> quoteIds = new Set<Id>();
    public Map<Id, Quote> quoteMap = new Map<Id, Quote>();
    public Map<Id, List<QuoteLineItem>> newQuoteLineItemsByQuote = new Map<Id, List<QuoteLineItem>>();
    public Map<Id, List<QuoteLineItem>> quoteLineItemsWithRelatedFieldsByQuote = new Map<Id, List<QuoteLineItem>>();
    public List<QuoteLineItem> quoteLineItemsByQuoteId = new List<QuoteLineItem>();
    public List<Asset> activeAssets =  new List<Asset>();
    public Map<Id, QuoteLineItem> newQuoteLineItems = new Map<Id, QuoteLineItem>();
    public Map<Id, QuoteLineItem> oldQuoteLineItems = new Map<Id, QuoteLineItem>();
    public List<Id> productIds = new List<Id>();
    public Map<Id, Map<String, Object>> productAttributes = new Map<Id, Map<String, Object>>();
}