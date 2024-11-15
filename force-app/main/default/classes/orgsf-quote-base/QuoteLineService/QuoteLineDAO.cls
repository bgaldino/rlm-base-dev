public with sharing class QuoteLineDAO implements IQuoteLineDAO {
    /************************************************
     * Setup class instance
     ************************************************/
    private static IQuoteLineDAO instance = null;

    public static IQuoteLineDAO getInstance() {
        if (instance == null) {
            instance = new QuoteLineDAO();
        }
        return instance;
    }

    /** @description: Make class mockable for unit tests */
    public static void setInstance(IQuoteLineDAO existingInstance) {
        instance = existingInstance;
    }

    public void insertLines(List<QuoteLineItem> lines) {
        if (lines.getSObjectType().getDescribe().isCreateable()) {
            Database.insert(lines, SecurityCheck.getAccessLevel());
        }
    }

    public void updateLines(List<QuoteLineItem> lines) {
        if (lines.getSObjectType().getDescribe().isUpdateable()) {
            Database.update(lines, SecurityCheck.getAccessLevel());
        }
    }

    public void deleteLines(List<QuoteLineItem> lines) {
        if (lines.getSObjectType().getDescribe().isDeletable()) {
            Database.delete(lines, SecurityCheck.getAccessLevel());
        }
    }

    public void updateOpportunityLines(List<OpportunityLineItem> opportunityLines) {
        if (opportunityLines.getSObjectType().getDescribe().isUpdateable()) {
            Database.update(opportunityLines, SecurityCheck.getAccessLevel());
        }
    }

    public List<QuoteLineItem> getQuoteLinesByQuoteId(Id quoteId) {
        return this.getQuoteLinesByQuoteIds(new Set<Id>{ quoteId });
    }
    
    public List<QuoteLineItem> getUsageQuoteLinesByQuoteId(Id quoteId) {
        List<String> fields = getQuoteLineFields();
        fields.add('NetUnitPrice');
        fields.add('PricingTermCount');
        fields.add('Quote.Pricebook2Id');

        return this.runQuery(fields, new Set<Id>{ quoteId });
    }

    public List<QuoteLineItem> getQuoteLinesByQuoteIds(Set<Id> quoteIds) {
        List<String> fields = getQuoteLineFields();
        fields.add('NetUnitPrice');
        fields.add('PricingTermCount');

        return this.runQuery(fields, quoteIds);
    }
    
    public List<QuoteLineItem> getQuoteLinesByQuoteIdsConvertCurrencies(Set<Id> quoteIds) {
        List<String> fields = getQuoteLineFields();

        fields.add('convertCurrency(NetUnitPrice)');
        return this.runQuery(fields, quoteIds);
    }

    public List<QuoteLineItem> getQuoteLinesForSync(Set<Id> quoteIds) {
        List<String> fields = new List<String>{
            'Id',
            'quoteId',
            'BillingName__c',
            'BillingAddress__City__s',
            'BillingAddress__CountryCode__s',
            'BillingAddress__PostalCode__s',
            'BillingAddress__StateCode__s',
            'BillingAddress__Street__s',
            'ShippingName__c',
            'ShippingAddress__City__s',
            'ShippingAddress__CountryCode__s',
            'ShippingAddress__PostalCode__s',
            'ShippingAddress__StateCode__s',
            'ShippingAddress__Street__s',
            'StartDate',
            'EndDate',
            'PricingTermCount',
            'AutoRenewal__c',
            'BillingFrequency__c',
            'BillingLanguage__c',
            'InvoiceDispatchMethod__c',
            'OpportunityLineItemId',
            'PaymentMethod__c',
            'PaymentTerm__c',
            'PreBillDays__c',
            'RenewalTerm__c',
            'BusinessType__c',
            'SellingModelType',
            'Quote.AccountId',
            'Quote.ServiceStartDate__c',
            'Quote.BillingCountry',
            'Quote.Status',
            'Tenant__c'
        };
        return this.runQuery(fields, quoteIds);
    }

    public List<QuoteLineItem> getQuoteLineByIds(Set<Id> quoteLineIds) {
        List<String> fields = getQuoteLineFields();
        return getQuoteLineByIds(quoteLineIds, fields);
    }

    public List<QuoteLineItem> getQuoteLineByIds(Set<Id> quoteLineIds, List<String> fields) {
        String query = String.format(
            'SELECT {0} FROM QuoteLineItem WHERE Id IN :quoteLineIds',
            new List<String>{ String.join(fields, ', ') }
        );

        return Database.queryWithBinds(query, new Map<String, Object>{ 'quoteLineIds' => quoteLineIds }, SecurityCheck.getAccessLevel());
    }

    private List<QuoteLineItem> runQuery(List<String> fields, Set<Id> quoteIds) {
        String query = String.format(
            'SELECT {0} FROM QuoteLineItem WHERE QuoteId IN :quoteIds Order BY SortOrder ASC',
            new List<String>{ String.join(fields, ', ') }
        );

        return Database.queryWithBinds(query, new Map<String, Object>{ 'quoteIds' => quoteIds }, SecurityCheck.getAccessLevel());
    }
/*     public List<AppliedSpecialTerm__c> getAppliedSpecialTerms(Id quoteId, List<String> resipList) {
        String value = '(\'' + String.join(resipList, '\',\'') + '\')';
        return Database.queryWithBinds(
            'SELECT Id, Title__c, SubType__c, TermText__c, Custom__c, Quote__r.Name, ParentTerm__c, ParentTerm__r.RecordType.Name, StrippedHtmlTermText__c FROM AppliedSpecialTerm__c WHERE Quote__c = :quoteId AND (ParentTerm__r.RecordType.Name = \'QST\' OR ParentTerm__r.RecordType.Name = \'PST\' ) AND OmitFromQuote__c = false AND (RestrictedAppliedTermApprovals__c  INCLUDES ' +
                value +
                ' OR (Custom__c = true AND CustomRoutingApprovals__c INCLUDES ' +
                value +
                '))',
            new Map<String, Object>{ 'quoteId' => quoteId, 'resipList' => resipList },
            SecurityCheck.getAccessLevel()
        );
    } */
/*     public List<sbaa__ApprovalRule__c> getAppRuleData(Id ruleId) {
        return Database.queryWithBinds(
            'SELECT Id, ApprovalTermFilters__c FROM sbaa__ApprovalRule__c WHERE Id = :ruleId',
            new Map<String, Object>{ 'ruleId' => ruleId },
            SecurityCheck.getAccessLevel()
        );
    } */

    private static List<String> getQuoteLineFields() {
        return new List<String>{
            'Id',
            'QuoteId',
            'Description',
            'Product2Id',
            'Product2.Name',
            'Product2.BasedOnId',
            'ProductSellingModelId',
            'PricebookEntryId',
            'Quantity',
            'StartQuantity',
            'ServiceDate',
            'BillingFrequency',
            'UnitPrice',
            'OpportunityLineItemId',
            'TotalPrice',
            'StartDate',
            'EndDate',
            'PeriodBoundary',
            'PeriodBoundaryDay',
            'SubscriptionTerm',
            'Discount',
            'DiscountAmount',
            'ListPrice',
            'Tenant__c',
            'Tenant__r.Quoting_Status__c',
            'ApprovalLevel__c',
            'SortOrder',
            'CurrencyIsoCode',
            'PricebookEntry.Pricebook2Id',
            'PricebookEntry.IsDerived',
            'SellingModelType',
            'QuoteActionId',
            'Quote.CurrencyIsoCode',
            'Quote.Status',
            'Quote.QuoteType__c',
            'Quote.AccountId',
            'Quote.ServiceStartDate__c',
            'Quote.ServiceEndDate__c',
            'Quote.Opportunity.AccountId'
        };
    }

    public List<ProductSellingModel> getProductSellingModel(Set<Id> psmIdList) {
        return Database.queryWithBinds(
            'SELECT Id, SellingModelType FROM ProductSellingModel WHERE Id IN :psmIdList',
            new Map<String, Object>{ 'psmIdList' => psmIdList },
            SecurityCheck.getAccessLevel()
        );
    }
}
