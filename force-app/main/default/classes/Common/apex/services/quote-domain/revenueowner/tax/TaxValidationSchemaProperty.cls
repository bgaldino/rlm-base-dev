public with sharing class TaxValidationSchemaProperty {
    @AuraEnabled
    public Integer minimumLength { get; set; }
    @AuraEnabled
    public Integer maximumLength { get; set; }
    @AuraEnabled
    public String regexPattern { get; set; }
}
