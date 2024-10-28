public with sharing virtual class BillingInformation {
    @AuraEnabled
    public Id billingInformationId { get; set; }
    @AuraEnabled
    public String name { get; set; }
    @AuraEnabled
    public Id accountId { get; set; }
     @AuraEnabled
    public Id primaryContact { get; set; }
     @AuraEnabled
    public Id secondaryContact { get; set; }

     @AuraEnabled
    public String autoRenewPreference { get; set; }
     @AuraEnabled
    public String frequency { get; set; }
     @AuraEnabled
    public String language { get; set; }
     @AuraEnabled
    public String country { get; set; }
     @AuraEnabled
    public String billingCurrency { get; set; }
     @AuraEnabled
    public String invoiceDispatchMethod { get; set; }
     @AuraEnabled
    public String paymentMethod { get; set; }
     @AuraEnabled
    public String paymentTerm { get; set; }
     @AuraEnabled
    public Integer preBillDays { get; set; }
     @AuraEnabled
    public Integer renewalTerm { get; set; }
    
     @AuraEnabled
    public String businessType { get; set; }
     @AuraEnabled
    public String noTaxRegistrationIdReason { get; set; }
     @AuraEnabled
    public String taxExemptStatus { get; set; }
     @AuraEnabled
    public String taxExemptionId { get; set; }
     @AuraEnabled
    public String taxRegistrationId { get; set; }
    @AuraEnabled
    public String billingCompanyName {get; set;}
}