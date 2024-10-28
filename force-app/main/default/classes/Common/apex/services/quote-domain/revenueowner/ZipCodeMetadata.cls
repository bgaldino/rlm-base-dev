public with sharing class ZipCodeMetadata {
    @AuraEnabled
    public Boolean isRequired { get; set; }
    @AuraEnabled
    public String validationRegex { get; set; }
    @AuraEnabled
    public String hintText { get; set; }
}
