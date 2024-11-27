public with sharing class BillingInfoServiceRequestItem extends BaseRequestItem {
    public BillingInformation billingInfo { get; set; }

    public BillingInfoServiceRequestItem(BillingInformation billingInfo) {
         this.billingInfo = billingInfo;
    }
}