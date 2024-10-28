public with sharing class TaxValidationReqItem {
    public String validationType = 'TAX_INFO';
    @AuraEnabled
    public String countryIsoCode { get; set; }
    @AuraEnabled
    public String taxId { get; set; }
    @AuraEnabled
    public String businessType { get; set; }
    @AuraEnabled
    public String legalEmailAddress { get; set; }
    @AuraEnabled
    public String SDICode { get; set; }
    @AuraEnabled
    public String taxIdExemptReason { get; set; }
}
