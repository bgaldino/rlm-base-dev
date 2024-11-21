public with sharing class QuoteSyncRunner {
    @TestVisible
    private static Map<Id, Quote> quoteMap = new Map<Id, Quote>();

    public static void syncQuotes(List<Quote> newQuotes, Map<Id, Quote> oldQuotes, Map<Id, QuoteLineItem> quoteLinesToUpdate) {
        IQuoteLineDAO quoteLineDAO = (IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO');

        if (newQuotes == null || newQuotes?.isEmpty()) {
            return;
        }

        if (oldQuotes == null || oldQuotes?.isEmpty()) {
            return;
        }

        Set<Id> quoteIdsForQuery = new Set<Id>();

        for (Quote quote : newQuotes) {
            Boolean addToSet = !quoteMap.containsKey(quote.Id);
            quoteMap.put(quote.Id, quote);

            if (!QuoteToQLISyncHelper.shouldSyncQuote(quote, oldQuotes.get(quote.Id))) {
                continue;
            }

            if (addToSet) {
                quoteIdsForQuery.add(quote.Id);
            }
        }

        if (quoteIdsForQuery.size() == 0) {
            return;
        }

        List<QuoteLineItem> quoteLineItems = quoteLineDAO.getQuoteLinesForSync(quoteIdsForQuery);

        getQuoteLinesToPropogate(quoteLineItems, quoteLinesToUpdate);
        
        if (quoteLinesToUpdate.size() == 0) {
            return;
        }
        
          SObjectAccessDecision securityDecision = Security.stripInaccessible(AccessType.UPDATABLE, quoteLinesToUpdate.values());
        if (!securityDecision.getRecords().isEmpty()) {
            quoteLineDAO.updateLines(securityDecision.getRecords());
        }
    }

    private static List<QuoteLineItem> getQuoteLinesToPropogate(List<QuoteLineItem> quoteLineItems, Map<Id, QuoteLineItem> quoteLinesToUpdate) {
        List<QuoteLineItem> updatedQuoteLineItems = new List<QuoteLineItem>();

        if (quoteLineItems == null || quoteLineItems.size() == 0) {
            return updatedQuoteLineItems;
        }

        for (QuoteLineItem quoteLineItem : quoteLineItems) {
            Quote mappedQuote = quoteMap.get(quoteLineItem.QuoteId);
            if (QuoteToQLISyncHelper.shouldPropogate(mappedQuote, quoteLineItem, quoteLineItem.SellingModelType)) {
                QuoteLineItem qli = null;
                if (!quoteLinesToUpdate.containsKey(quoteLineItem.Id)) {
                    quoteLinesToUpdate.put(quoteLineItem.Id, new QuoteLineItem(Id = quoteLineItem.Id));
                }
                qli = quoteLinesToUpdate.get(quoteLineItem.Id);

                qli.Id = quoteLineItem.Id;
                qli.BillingName__c = mappedQuote.BillingName;
                qli.BillingAddress__City__s = mappedQuote.BillingCity;
                qli.BillingAddress__CountryCode__s = mappedQuote.BillingCountry;
                qli.BillingAddress__PostalCode__s = mappedQuote.BillingPostalCode;
                qli.BillingAddress__StateCode__s = mappedQuote.BillingState;
                qli.BillingAddress__Street__s = mappedQuote.BillingStreet;
                qli.ShippingName__c = mappedQuote.ShippingName;
                qli.ShippingAddress__City__s = mappedQuote.ShippingCity;
                qli.ShippingAddress__CountryCode__s = mappedQuote.ShippingCountry;
                qli.ShippingAddress__PostalCode__s = mappedQuote.ShippingPostalCode;
                qli.ShippingAddress__StateCode__s = mappedQuote.ShippingState;
                qli.ShippingAddress__Street__s = mappedQuote.ShippingStreet;
                if (quoteLineItem.SellingModelType != 'OneTime') {
                    qli.StartDate = mappedQuote.ServiceStartDate__c;
                    qli.EndDate = mappedQuote.ServiceEndDate__c;
                }
                //qli.PrimaryBillingContact__c = mappedQuote.PrimaryBillingContact__c;
                //qli.SecondaryBillingContact__c = mappedQuote.SecondaryBillingContact__c;
                qli.AutoRenewal__c = mappedQuote.AutoRenewal__c;
                qli.BillingFrequency__c = mappedQuote.BillingFrequency__c;
                //qli.BillingFrequencySpecialTerm__c = mappedQuote.BillingFrequencySpecialTerm__c;
                qli.BillingLanguage__c = mappedQuote.BillingLanguage__c;
                qli.InvoiceDispatchMethod__c = mappedQuote.InvoiceDispatchMethod__c;
                qli.PaymentMethod__c = mappedQuote.PaymentMethod__c;
                qli.PaymentTerm__c = mappedQuote.PaymentTerm__c;
                //qli.PaymentDetailJSON__c = mappedQuote.PaymentDetailJSON__c;
                qli.PreBillDays__c = mappedQuote.PreBillDays__c;
                qli.RenewalTerm__c = mappedQuote.RenewalTerm__c;
                qli.BusinessType__c = mappedQuote.BusinessType__c;
                //qli.TaxExemptStatus__c = mappedQuote.TaxExemptStatus__c;
                //qli.TaxExemptionId__c = mappedQuote.TaxExemptionId__c;
                //qli.TaxRegistrationId__c = mappedQuote.TaxRegistrationId__c;
                //qli.NoTaxRegistrationIdReason__c = mappedQuote.NoTaxRegistrationIdReason__c;
                //qli.TaxInformationJSON__c = mappedQuote.TaxInformationJSON__c;
                //qli.PurchaseOrderAmount__c = mappedQuote.PurchaseOrderAmount__c;
                //qli.PurchaseOrderNumber__c = mappedQuote.PurchaseOrderNumber__c;
                //qli.PurchaseOrderRequired__c = mappedQuote.PurchaseOrderRequired__c;
                //qli.BillingCompanyName__c = mappedQuote.BillingCompanyName__c;
                updatedQuoteLineItems.add(qli);
            }
        }

        return updatedQuoteLineItems;
    }
}