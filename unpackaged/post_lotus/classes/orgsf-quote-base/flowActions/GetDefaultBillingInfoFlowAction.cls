public with sharing class GetDefaultBillingInfoFlowAction {
    @InvocableMethod(label='Get Default Billing Information')
    public static List<BillingInformation__c> getDefaultBillingInfo(List<GetDefaultBillingInfoRequest> requestList) {
        List<BillingInformation__c> result = new List<BillingInformation__c>();
        for (GetDefaultBillingInfoRequest request : requestList) {
            IBillingInfoService billingInfoService = (IBillingInfoService) ServiceRegistry.getInstance('IBillingInfoService');
            List<BillingInformation> billingInfoList = billingInfoService.getBillingInformation(request.accountId, request.country, request.billingCurrency);
            if (billingInfoList.size() == 1) {
                result.add(createBillingInformation(billingInfoList.get(0)));
            }
        }
        return result;
    }

    public class GetDefaultBillingInfoRequest {
        @InvocableVariable(required=true)
        public Id accountId;

        @InvocableVariable(required=true)
        public String country;

        @InvocableVariable(required=true)
        public String billingCurrency;
    }

    private static BillingInformation__c createBillingInformation(BillingInformation billingInfoRecord) {
        BillingInformation__c billingInfo = new BillingInformation__c();
        billingInfo.Id = billingInfoRecord.billingInformationId;
        billingInfo.Name = billingInfoRecord.name;
        billingInfo.Account__c = billingInfoRecord.accountId;
        billingInfo.PrimaryBillingContact__c = billingInfoRecord.primaryContact;
        billingInfo.SecondaryBillingContact__c = billingInfoRecord.secondaryContact;
        billingInfo.AutoRenewal__c = billingInfoRecord.autoRenewPreference;
        billingInfo.BillingFrequency__c = billingInfoRecord.frequency;
        billingInfo.BillingLanguage__c = billingInfoRecord.language;
        billingInfo.BillingCountry__c = billingInfoRecord.country;
        billingInfo.CurrencyIsoCode = billingInfoRecord.billingCurrency;
        billingInfo.InvoiceDispatchMethod__c = billingInfoRecord.invoiceDispatchMethod;
        billingInfo.PaymentMethod__c = billingInfoRecord.paymentMethod;
        billingInfo.PaymentTerm__c = billingInfoRecord.paymentTerm;
        billingInfo.PreBillDays__c = billingInfoRecord.preBillDays;
        billingInfo.RenewalTerm__c = billingInfoRecord.renewalTerm;
        billingInfo.BusinessType__c = billingInfoRecord.businessType;
        billingInfo.TaxExemptStatus__c = billingInfoRecord.taxExemptStatus;
        billingInfo.TaxExemptionId__c = billingInfoRecord.taxExemptionId;
        billingInfo.TaxRegistrationId__c = billingInfoRecord.taxRegistrationId;
        billingInfo.NoTaxRegistrationIdReason__c = billingInfoRecord.noTaxRegistrationIdReason;
        billingInfo.BillingCompanyName__c = billingInfoRecord.billingCompanyName;
        return billingInfo;
    }
}