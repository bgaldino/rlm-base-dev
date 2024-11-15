public with sharing class TaxInformation {
    @AuraEnabled
    public Boolean isTaxIdRequired { get; set; }
    @AuraEnabled
    public Boolean isBusinessTypeApplicable { get; set; }
    @AuraEnabled
    public Boolean isNoTaxRegistrationIdReasonApplicable { get; set; }
    @AuraEnabled
    public String taxIdLabel { get; set; }
    @AuraEnabled
    public String taxIdExemptionLabel { get; set; }
    @AuraEnabled
    public String taxIdFormatRegex { get; set; }
    @AuraEnabled
    public String taxIdSample { get; set; }
    @AuraEnabled
    public Map<String, String> taxIdExemptionReasons { get; set; }
    @AuraEnabled
    public Map<String, String> taxIdErrors { get; set; }
    @AuraEnabled
    public TaxValidationSchema taxValidationSchema { get; set; }
}
