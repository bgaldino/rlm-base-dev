public with sharing class QuoteTriggerApprovalLevelRunner {
    IQuoteLineDAO quoteLineDAO;

    public QuoteTriggerApprovalLevelRunner() {
        this((IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO'));
    }

    public QuoteTriggerApprovalLevelRunner(IQuoteLineDAO quoteLineDAO) {
        this.quoteLineDAO = quoteLineDAO;
    }

    public void processQuotes(List<Quote> quotes, Map<Id, Quote> oldQuotes, Map<Id, QuoteLineItem> quoteLinesToUpdate) {
        Set<Id> idsToProcess = new Set<Id>();

        for (Quote quote : quotes) {
            if (quote?.Term__c != null && quote.Term__c != oldQuotes?.get(quote.Id).Term__c) {
                EffectiveQuantityService.quotesHadTermChange = true;
                idsToProcess.add(quote.Id);
            }
        }

        if(idsToProcess.size() == 0) {
            return;
        }

        List<QuoteLineItem> quoteLineItems = quoteLineDAO.getQuoteLinesByQuoteIds(idsToProcess);

        for (QuoteLineItem quoteLineItem : quoteLineItems) {
            QuoteLineItem quoteLineToUpdate = null;
            if (!quoteLinesToUpdate.containsKey(quoteLineItem.Id)) {
                quoteLinesToUpdate.put(quoteLineItem.Id, new QuoteLineItem(Id= quoteLineItem.Id));
            }
            quoteLineToUpdate = quoteLinesToUpdate.get(quoteLineItem.Id);

            quoteLineToUpdate.EffectiveQuantity__c = 0;
        }
    }
}
