public with sharing class QuoteToQLISyncHelper {
    private static final String REJECTED_QUOTE_STATUS = 'Rejected';
    private static Set<String> INVALID_QUOTE_STATUS_FOR_SYNC = new Set<String>{ 'Booked', 'Archived' };

    public static Boolean shouldSyncQuote(Quote newQuote, Quote oldQuote) {
        if (newQuote == null || oldQuote == null) {
            return false;
        }

        return !INVALID_QUOTE_STATUS_FOR_SYNC.contains(newQuote.Status) && !isQuoteRejected(newQuote, oldQuote);
    }

    private static Boolean isQuoteRejected(Quote newQuote, Quote oldQuote) {
        return newQuote.Status != oldQuote.Status && newQuote.Status == REJECTED_QUOTE_STATUS;
    }

    public static Boolean shouldPropogate(Quote quote, QuoteLineItem quoteLineItem, String sellingModelType) {
        if (quote == null || quoteLineItem == null) {
            return false;
        }

        Boolean areFieldsEqual = true;

        areFieldsEqual &= quote.BillingName == quoteLineItem.BillingName__c;
        areFieldsEqual &= quote.BillingCity == quoteLineItem.BillingAddress__City__s;
        areFieldsEqual &= quote.BillingCountry == quoteLineItem.BillingAddress__CountryCode__s;
        areFieldsEqual &= quote.BillingPostalCode == quoteLineItem.BillingAddress__PostalCode__s;
        areFieldsEqual &= quote.BillingState == quoteLineItem.BillingAddress__StateCode__s;
        areFieldsEqual &= quote.BillingStreet == quoteLineItem.BillingAddress__Street__s;
        areFieldsEqual &= quote.ShippingName == quoteLineItem.ShippingName__c;
        areFieldsEqual &= quote.ShippingCity == quoteLineItem.ShippingAddress__City__s;
        areFieldsEqual &= quote.ShippingCountry == quoteLineItem.ShippingAddress__CountryCode__s;
        areFieldsEqual &= quote.ShippingPostalCode == quoteLineItem.ShippingAddress__PostalCode__s;
        areFieldsEqual &= quote.ShippingState == quoteLineItem.ShippingAddress__StateCode__s;
        areFieldsEqual &= quote.ShippingStreet == quoteLineItem.ShippingAddress__Street__s;
        if (sellingModelType == 'OneTime') {
            areFieldsEqual &= quoteLineItem.StartDate == null;
            areFieldsEqual &= quoteLineItem.EndDate == null;
        } else {
            areFieldsEqual &= quote.ServiceStartDate__c == quoteLineItem.StartDate;
            areFieldsEqual &= quote.ServiceEndDate__c == quoteLineItem.EndDate;
        }
        //areFieldsEqual &= quote.PrimaryBillingContact__c == quoteLineItem.PrimaryBillingContact__c;
        //areFieldsEqual &= quote.SecondaryBillingContact__c == quoteLineItem.SecondaryBillingContact__c;
        areFieldsEqual &= quote.AutoRenewal__c == quoteLineItem.AutoRenewal__c;
        areFieldsEqual &= quote.BillingFrequency__c == quoteLineItem.BillingFrequency__c;
        //areFieldsEqual &= isJSONEqual(quote.BillingFrequencySpecialTerm__c, quoteLineItem.BillingFrequencySpecialTerm__c);
        areFieldsEqual &= quote.BillingLanguage__c == quoteLineItem.BillingLanguage__c;
        areFieldsEqual &= quote.InvoiceDispatchMethod__c == quoteLineItem.InvoiceDispatchMethod__c;
        areFieldsEqual &= quote.PaymentMethod__c == quoteLineItem.PaymentMethod__c;
        areFieldsEqual &= quote.PaymentTerm__c == quoteLineItem.PaymentTerm__c;
        //areFieldsEqual &= isJSONEqual(quote.PaymentDetailJSON__c, quoteLineItem.PaymentDetailJSON__c);
        areFieldsEqual &= quote.PreBillDays__c == quoteLineItem.PreBillDays__c;
        areFieldsEqual &= quote.RenewalTerm__c == quoteLineItem.RenewalTerm__c;
        areFieldsEqual &= quote.BusinessType__c == quoteLineItem.BusinessType__c;
        //areFieldsEqual &= quote.TaxExemptStatus__c == quoteLineItem.TaxExemptStatus__c;
        //areFieldsEqual &= quote.TaxExemptionId__c == quoteLineItem.TaxExemptionId__c;
        //areFieldsEqual &= quote.TaxRegistrationId__c == quoteLineItem.TaxRegistrationId__c;
        //areFieldsEqual &= quote.NoTaxRegistrationIdReason__c == quoteLineItem.NoTaxRegistrationIdReason__c;
        //areFieldsEqual &= isJSONEqual(quote.TaxInformationJSON__c, quoteLineItem.TaxInformationJSON__c);
        //areFieldsEqual &= quote.PurchaseOrderAmount__c == quoteLineItem.PurchaseOrderAmount__c;
        //areFieldsEqual &= quote.PurchaseOrderNumber__c == quoteLineItem.PurchaseOrderNumber__c;
        //areFieldsEqual &= quote.PurchaseOrderRequired__c == quoteLineItem.PurchaseOrderRequired__c;
        //areFieldsEqual &= quote.BillingCompanyName__c == quoteLineItem.BillingCompanyName__c;
        return !areFieldsEqual;
    }

    //Only does 1 layer currently
    @TestVisible
    private static Boolean isJSONEqual(String jsonA, String jsonB) {
        Map<String, Object> mapA;
        Map<String, Object> mapB;

        if (jsonA == jsonB) {
            return true;
        }

        try {
            mapA = (Map<String, Object>) JSON.deserializeUntyped(jsonA);
        } catch (Exception e) {
            mapA = new Map<String, Object>();
        }

        try {
            mapB = (Map<String, Object>) JSON.deserializeUntyped(jsonB);
        } catch (Exception e) {
            mapB = new Map<String, Object>();
        }

        if (mapA.size() != mapB.size()) {
            return false;
        }

        for (String key : mapA.keySet()) {
            if (!mapA.containsKey(key) || !mapB.containsKey(key) || mapA.get(key) != mapB.get(key)) {
                return false;
            }
        }

        return true;
    }
}