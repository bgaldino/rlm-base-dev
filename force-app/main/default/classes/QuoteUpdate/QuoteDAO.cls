public with sharing class QuoteDAO implements IQuoteDAO {
    public void quoteUpdate(List<Quote> quotes) {
        if (quotes.getSObjectType().getDescribe().isUpdateable()) {
            Database.update(quotes, SecurityCheck.getAccessLevel());
        }
    }

    //updating quotes and returing Database results
    public List<Database.SaveResult> quoteUpdate(List<Quote> quotes, Boolean allorNone) {
        List<Database.SaveResult> srList = new List<Database.SaveResult>();
        if (quotes.getSObjectType().getDescribe().isUpdateable()) {
            srList = Database.update(quotes, allorNone, SecurityCheck.getAccessLevel());
        }
        return srList;
    }

    public List<Database.SaveResult> quoteInsert(List<Quote> quotes) {
        List<Database.SaveResult> saveResultList;
        if (quotes.getSObjectType().getDescribe().isCreateable()) {
            saveResultList = Database.insert(quotes, SecurityCheck.getAccessLevel());
        }
        return saveResultList;
    }

    public List<Quote> getQuotesForSync(Set<Id> quoteIds) {
        List<String> fields = new List<String>{
            'Id',
            'BillingName',
            'BillingCity',
            'BillingCountry',
            'BillingPostalCode',
            'BillingState',
            'BillingStreet',
            'ShippingName',
            'ShippingCity',
            'ShippingCountry',
            'ShippingPostalCode',
            'ShippingState',
            'ShippingStreet',
            'ServiceStartDate__c',
            'ServiceEndDate__c',
            'PrimaryBillingContact__c',
            'SecondaryBillingContact__c',
            'AutoRenewal__c',
            'BillingFrequency__c',
            'BillingFrequencySpecialTerm__c',
            'BillingLanguage__c',
            'InvoiceDispatchMethod__c',
            'PaymentMethod__c',
            'PaymentDetailJSON__c',
            'PaymentTerm__c',
            'PreBillDays__c',
            'RenewalTerm__c',
            'BusinessType__c',
            'TaxExemptStatus__c',
            'TaxExemptionId__c',
            'TaxRegistrationId__c',
            'NoTaxRegistrationIdReason__c',
            'TaxInformationJSON__c',
            'PurchaseOrderAmount__c',
            'PurchaseOrderNumber__c',
            'PurchaseOrderRequired__c',
            'IsSyncing',
            'Term__c',
            'Status',
            'Opportunity.Account.LDP_Status__c',
            'MaintenanceModeEnabled__c',
            'BillingCompanyName__c'
        };

        return runQuery(fields, quoteIds);
    }

    private List<Quote> runQuery(List<String> fields, Set<Id> quoteIds) {
        String query = String.format(
            'SELECT {0} FROM Quote WHERE Id IN :quoteIds',
            new List<String>{ String.join(fields, ', ') }
        );

        return Database.queryWithBinds(query, new Map<String, Object>{ 'quoteIds' => quoteIds }, SecurityCheck.getAccessLevel());
    }

    public List<Quote> getAcceptedQuotesOnOppty(Id opptyId) {
        return Database.queryWithBinds(
            'SELECT Id, Status FROM Quote WHERE Status = \'Accepted\' AND OpportunityId = :opptyId',
            new Map<String, Object>{ 'opptyId' => opptyId },
            SecurityCheck.getAccessLevel()
        );
    }
}