public with sharing class BillingInfoServiceResponseItem extends BaseResponseItem {
    @AuraEnabled
    public Id billingInformationId { get; set; }

    public BillingInfoServiceResponseItem(String requestId) {
        super(requestId);
    }
}