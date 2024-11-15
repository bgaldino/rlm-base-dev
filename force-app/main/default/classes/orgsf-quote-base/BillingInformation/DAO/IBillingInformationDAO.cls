public interface IBillingInformationDAO {
    List<Database.SaveResult> updateBillingInfo(List<BillingInformation__c> billingInfoList);
    List<Database.SaveResult> insertBillingInfo(List<BillingInformation__c> billingInfoList);
}