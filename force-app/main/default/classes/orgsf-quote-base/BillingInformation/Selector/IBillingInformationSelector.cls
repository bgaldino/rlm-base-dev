public interface IBillingInformationSelector {
    List<BillingInformation__c> getBillingInfo(Id accountId, String country, String billingCurrency);
    List<BillingInformation__c> getBillingInfoByName(Id accountId, String name);
    List<BillingInformation__c> getBillingInfoDuplicate(BillingInformation billingInfo);
}