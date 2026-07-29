public with sharing class RLM_HomeServices_ProspectValueCardCtrl {

    public class ProspectData {
        @AuraEnabled public Decimal opportunityAmount;
        @AuraEnabled public String  opportunityStage;
        @AuraEnabled public Boolean hasContracts;
        @AuraEnabled public Boolean hasOrders;
        @AuraEnabled public List<LineItemWrapper> lineItems;
        @AuraEnabled public String  firstName;
        @AuraEnabled public String  lastName;
        @AuraEnabled public String  email;
    }

    public class LineItemWrapper {
        @AuraEnabled public String  lineItemId;
        @AuraEnabled public String  productName;
        @AuraEnabled public Decimal unitPrice;
        @AuraEnabled public Decimal quantity;
        @AuraEnabled public String  displayUrl;
    }

    @AuraEnabled(cacheable=true)
    public static ProspectData getProspectData(String accountId) {
        ProspectData result = new ProspectData();
        result.opportunityAmount = 0;
        result.opportunityStage  = '';
        result.hasContracts      = false;
        result.hasOrders         = false;
        result.lineItems         = new List<LineItemWrapper>();

        Id validatedAccountId;
        try {
            validatedAccountId = Id.valueOf(accountId);
        } catch (Exception e) {
            return result;
        }

        // Pull Account-level fields so the LWC doesn't need them in @wire(getRecord)
        try {
            Account acc = [
                SELECT RLM_HomeServices_FirstName__c, RLM_HomeServices_LastName__c, RLM_HomeServices_Email__c
                FROM   Account
                WHERE  Id = :validatedAccountId
                LIMIT  1
            ];
            result.firstName = acc.RLM_HomeServices_FirstName__c;
            result.lastName  = acc.RLM_HomeServices_LastName__c;
            result.email     = acc.RLM_HomeServices_Email__c;
        } catch (Exception e) {
            // Fields may not exist in all orgs — safe to ignore
        }

        List<Opportunity> opps = [
            SELECT Id, Amount, StageName
            FROM   Opportunity
            WHERE  AccountId = :validatedAccountId
            ORDER BY CreatedDate DESC
            LIMIT 1
        ];

        if (opps.isEmpty()) {
            return result;
        }

        Opportunity opp = opps[0];
        result.opportunityAmount = opp.Amount != null ? opp.Amount : 0;
        result.opportunityStage  = opp.StageName;

        result.hasContracts = [
            SELECT COUNT() FROM Contract WHERE AccountId = :validatedAccountId
        ] > 0;

        result.hasOrders = [
            SELECT COUNT() FROM Order WHERE AccountId = :validatedAccountId
        ] > 0;

        List<QuoteLineItem> qlis = [
            SELECT  QLI.Id,
                    QLI.UnitPrice,
                    QLI.Quantity,
                    QLI.Product2.Name,
                    QLI.Product2.DisplayUrl
            FROM    QuoteLineItem QLI
            WHERE   QLI.Quote.OpportunityId = :opp.Id
            ORDER BY QLI.Quote.CreatedDate DESC, QLI.LineNumber ASC
            LIMIT 10
        ];

        for (QuoteLineItem qli : qlis) {
            LineItemWrapper w = new LineItemWrapper();
            w.lineItemId        = qli.Id;
            w.productName       = qli.Product2.Name;
            w.unitPrice         = qli.UnitPrice;
            w.quantity          = qli.Quantity;
            w.displayUrl        = qli.Product2.DisplayUrl;
            result.lineItems.add(w);
        }

        return result;
    }
}