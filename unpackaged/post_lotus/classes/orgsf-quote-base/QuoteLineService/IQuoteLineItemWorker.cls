public interface IQuoteLineItemWorker {
    
    void registerNew(QuoteLineItem record);

    void registerNew(List<QuoteLineItem> records);

    void registerDeleted(QuoteLineItem record);

    void registerDeleted(List<QuoteLineItem> records);

    void registerDirty(QuoteLineItem record);

    void registerDirty(QuoteLineItem record, List<SObjectField> dirtyFields);

    void registerDirty(List<QuoteLineItem> records, List<SObjectField> dirtyFields);

    void commitWork();
}