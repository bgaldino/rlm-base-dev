trigger RLM_HomeServices_QuoteLineItemQuoteRefresh on QuoteLineItem (after insert, after update, after delete) {
    Set<Id> quoteIds = new Set<Id>();
    if (Trigger.isDelete) {
        for (QuoteLineItem qli : Trigger.old) {
            if (qli.QuoteId != null) {
                quoteIds.add(qli.QuoteId);
            }
        }
    } else {
        for (QuoteLineItem qli : Trigger.new) {
            if (qli.QuoteId != null) {
                quoteIds.add(qli.QuoteId);
            }
        }
    }
    List<RLM_HomeServices_QuoteDataRefresh__e> events = new List<RLM_HomeServices_QuoteDataRefresh__e>();
    for (Id qId : quoteIds) {
        events.add(new RLM_HomeServices_QuoteDataRefresh__e(RLM_HomeServices_QuoteId__c = String.valueOf(qId)));
    }
    if (!events.isEmpty()) {
        EventBus.publish(events);
    }
}