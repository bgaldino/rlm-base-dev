trigger RLM_HomeServices_QuoteLineItemDatesTrigger on QuoteLineItem (before insert) {
    Set<Id> quoteIds = new Set<Id>();
    for (QuoteLineItem qli : Trigger.new) {
        quoteIds.add(qli.QuoteId);
    }

    if (!RLM_HomeServices_Settings__c.getOrgDefaults().RLM_Enabled__c) {
        return;
    }

    Date startDate = Date.newInstance(
        Date.today().year(), Date.today().month(), 1
    );

    for (QuoteLineItem qli : Trigger.new) {
        qli.StartDate        = startDate;
        qli.SubscriptionTerm = 12;
    }
}