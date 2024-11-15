public with sharing class BillingInformationDAO implements IBillingInformationDAO {
    public List<Database.SaveResult> updateBillingInfo(List<BillingInformation__c> billingInfoList) {
        List<Database.SaveResult> saveResultList;
        if (billingInfoList.getSObjectType().getDescribe().isUpdateable()) {
            saveResultList = Database.update(billingInfoList, SecurityCheck.getAccessLevel());
        }
        return saveResultList;
    }

    public List<Database.SaveResult> insertBillingInfo(List<BillingInformation__c> billingInfoList) {
        List<Database.SaveResult> saveResultList;
        if (billingInfoList.getSObjectType().getDescribe().isCreateable()) {
            saveResultList = Database.insert(billingInfoList, SecurityCheck.getAccessLevel());
        }
        return saveResultList;
    }
}
