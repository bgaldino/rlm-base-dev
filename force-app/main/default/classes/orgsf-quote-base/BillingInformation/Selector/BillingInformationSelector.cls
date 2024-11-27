public with sharing class BillingInformationSelector implements IBillingInformationSelector {
    public List<BillingInformation__c> getBillingInfo(Id accountId, String country, String billingCurrency) {
        return [
            SELECT
                Id,
                Name,
                Account__c,
                PrimaryBillingContact__c,
                SecondaryBillingContact__c,
                AutoRenewal__c,
                BillingFrequency__c,
                BillingLanguage__c,
                BillingCountry__c,
                CurrencyIsoCode,
                InvoiceDispatchMethod__c,
                PaymentMethod__c,
                PaymentTerm__c,
                PreBillDays__c,
                RenewalTerm__c,
                BusinessType__c,
                TaxExemptStatus__c,
                TaxExemptionId__c,
                TaxRegistrationId__c,
                NoTaxRegistrationIdReason__c,
                BillingCompanyName__c
            FROM BillingInformation__c
            WHERE Account__c = :accountId 
            AND BillingCountry__c = :country 
            AND CurrencyIsoCode = :billingCurrency
        ];
    }

    public List<BillingInformation__c> getBillingInfoByName(Id accountId, String name) {
        return [
            SELECT
                Id
            FROM BillingInformation__c
            WHERE Account__c = :accountId 
            AND Name = :name
        ];
    }

    public List<BillingInformation__c> getBillingInfoDuplicate(BillingInformation billingInfo) {
        return [
            SELECT
                Id,
                Name
            FROM BillingInformation__c
            WHERE Account__c = :billingInfo.accountId 
            AND PrimaryBillingContact__c = :billingInfo.primaryContact
            AND SecondaryBillingContact__c = :billingInfo.secondaryContact
            AND AutoRenewal__c = :billingInfo.autoRenewPreference
            AND BillingFrequency__c = :billingInfo.frequency
            AND BillingLanguage__c = :billingInfo.language
            AND BillingCountry__c = :billingInfo.country
            AND CurrencyIsoCode = :billingInfo.billingCurrency
            AND InvoiceDispatchMethod__c = :billingInfo.invoiceDispatchMethod
            AND PaymentMethod__c = :billingInfo.paymentMethod
            AND PaymentTerm__c = :billingInfo.paymentTerm
            AND PreBillDays__c = :billingInfo.preBillDays
            AND RenewalTerm__c = :billingInfo.renewalTerm
            AND BusinessType__c = :billingInfo.businessType
            AND TaxExemptStatus__c = :billingInfo.taxExemptStatus
            AND TaxExemptionId__c = :billingInfo.taxExemptionId
            AND TaxRegistrationId__c = :billingInfo.taxRegistrationId
            AND NoTaxRegistrationIdReason__c = :billingInfo.noTaxRegistrationIdReason
            AND BillingCompanyName__c = :billingInfo.billingCompanyName
        ];
    }
}