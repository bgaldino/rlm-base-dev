public with sharing class QLISyncRunner {
    private static IQuoteDAO quoteDAO = (IQuoteDAO) ServiceRegistry.getInstance('IQuoteDAO');
    private static IQuoteLineDAO quoteLineDAO = (IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO');

    private static Map<Id, Quote> quoteMap = new Map<Id, Quote>();
    private static Map<Id, ProductSellingModel> productSellingModelMap = new Map<Id, ProductSellingModel>();

    //Invoke in the before trigger
    public static void syncNewLines(List<QuoteLineItem> quoteLineItems) {
        if ((quoteLineItems == null || quoteLineItems?.isEmpty())) {
            return;
        }

        Set<Id> quoteIdsForQuery = new Set<Id>();
        Set<Id> psmIdsForQuery = new Set<Id>();

        for (QuoteLineItem quoteLineItem : quoteLineItems) {
            quoteIdsForQuery.add(quoteLineItem.QuoteId);
            psmIdsForQuery.add(quoteLineItem.ProductSellingModelId);
        }

        quoteMap = new Map<Id, Quote>(quoteDAO.getQuotesForSync(quoteIdsForQuery));
        productSellingModelMap = new Map<Id, ProductSellingModel>(quoteLineDAO.getProductSellingModel(psmIdsForQuery));

        propogateData(quoteLineItems);
    }

    private static void propogateData(List<QuoteLineItem> quoteLineItems) {
        for (QuoteLineItem quoteLineItem : quoteLineItems) {
            Quote quoteToSync = quoteMap.get(quoteLineItem.QuoteId);
            ProductSellingModel psm = productSellingModelMap.get(quoteLineItem.ProductSellingModelId);
            String sellingModelType;
            if (psm != null) {
                sellingModelType = psm.SellingModelType;
            }
            if (QuoteToQLISyncHelper.shouldPropogate(quoteToSync, quoteLineItem, sellingModelType)) {
                quoteLineItem.BillingName__c = quoteToSync.BillingName;
                quoteLineItem.BillingAddress__City__s = quoteToSync.BillingCity;
                quoteLineItem.BillingAddress__CountryCode__s = quoteToSync.BillingCountry;
                quoteLineItem.BillingAddress__PostalCode__s = quoteToSync.BillingPostalCode;
                quoteLineItem.BillingAddress__StateCode__s = quoteToSync.BillingState;
                quoteLineItem.BillingAddress__Street__s = quoteToSync.BillingStreet;
                quoteLineItem.ShippingName__c = quoteToSync.ShippingName;
                quoteLineItem.ShippingAddress__City__s = quoteToSync.ShippingCity;
                quoteLineItem.ShippingAddress__CountryCode__s = quoteToSync.ShippingCountry;
                quoteLineItem.ShippingAddress__PostalCode__s = quoteToSync.ShippingPostalCode;
                quoteLineItem.ShippingAddress__StateCode__s = quoteToSync.ShippingState;
                quoteLineItem.ShippingAddress__Street__s = quoteToSync.ShippingStreet;
                if (sellingModelType == 'OneTime') {
                    quoteLineItem.StartDate = null;
                    quoteLineItem.EndDate = null;
                } else {
                    quoteLineItem.StartDate = quoteToSync.ServiceStartDate__c;
                    quoteLineItem.EndDate = quoteToSync.ServiceEndDate__c;
                }
                quoteLineItem.PrimaryBillingContact__c = quoteToSync.PrimaryBillingContact__c;
                quoteLineItem.SecondaryBillingContact__c = quoteToSync.SecondaryBillingContact__c;
                quoteLineItem.AutoRenewal__c = quoteToSync.AutoRenewal__c;
                quoteLineItem.BillingFrequency__c = quoteToSync.BillingFrequency__c;
                quoteLineItem.BillingFrequencySpecialTerm__c = quoteToSync.BillingFrequencySpecialTerm__c;
                quoteLineItem.BillingLanguage__c = quoteToSync.BillingLanguage__c;
                quoteLineItem.InvoiceDispatchMethod__c = quoteToSync.InvoiceDispatchMethod__c;
                quoteLineItem.PaymentMethod__c = quoteToSync.PaymentMethod__c;
                quoteLineItem.PaymentTerm__c = quoteToSync.PaymentTerm__c;
                quoteLineItem.PaymentDetailJSON__c = quoteToSync.PaymentDetailJSON__c;
                quoteLineItem.PreBillDays__c = quoteToSync.PreBillDays__c;
                quoteLineItem.RenewalTerm__c = quoteToSync.RenewalTerm__c;
                quoteLineItem.BusinessType__c = quoteToSync.BusinessType__c;
                quoteLineItem.TaxExemptStatus__c = quoteToSync.TaxExemptStatus__c;
                quoteLineItem.TaxExemptionId__c = quoteToSync.TaxExemptionId__c;
                quoteLineItem.TaxRegistrationId__c = quoteToSync.TaxRegistrationId__c;
                quoteLineItem.NoTaxRegistrationIdReason__c = quoteToSync.NoTaxRegistrationIdReason__c;
                quoteLineItem.TaxInformationJSON__c = quoteToSync.TaxInformationJSON__c;
                quoteLineItem.PurchaseOrderAmount__c = quoteToSync.PurchaseOrderAmount__c;
                quoteLineItem.PurchaseOrderNumber__c = quoteToSync.PurchaseOrderNumber__c;
                quoteLineItem.PurchaseOrderRequired__c = quoteToSync.PurchaseOrderRequired__c;
                quotelineItem.BillingCompanyName__c = quoteToSync.BillingCompanyName__c;
            }
        }
    }
}