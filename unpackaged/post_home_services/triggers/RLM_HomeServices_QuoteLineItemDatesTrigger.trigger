trigger RLM_HomeServices_QuoteLineItemDatesTrigger on QuoteLineItem (before insert) {
    Set<Id> quoteIds = new Set<Id>();
    for (QuoteLineItem qli : Trigger.new) {
        quoteIds.add(qli.QuoteId);
    }

    Map<Id, Id> quoteToOppId = new Map<Id, Id>();
    for (Quote q : [SELECT Id, OpportunityId FROM Quote WHERE Id IN :quoteIds]) {
        quoteToOppId.put(q.Id, q.OpportunityId);
    }

    Set<Id> oppIds = new Set<Id>(quoteToOppId.values());
    Set<Id> rlmOppIds = new Set<Id>();
    for (Opportunity opp : [
        SELECT Id FROM Opportunity
        WHERE Id IN :oppIds
        AND RecordType.DeveloperName = 'RLM_HomeServices_Opportunity'
    ]) {
        rlmOppIds.add(opp.Id);
    }

    Date startDate = Date.newInstance(
        Date.today().year(), Date.today().month(), 1
    );

    for (QuoteLineItem qli : Trigger.new) {
        Id oppId = quoteToOppId.get(qli.QuoteId);
        if (rlmOppIds.contains(oppId)) {
            qli.StartDate        = startDate;
            qli.SubscriptionTerm = 12;
        }
    }
}