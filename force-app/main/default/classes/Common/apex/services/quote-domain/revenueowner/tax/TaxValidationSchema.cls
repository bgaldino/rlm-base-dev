public with sharing class TaxValidationSchema {
    @AuraEnabled
    public List<String> requiredFields = new List<String>();
    @AuraEnabled
    public List<TaxValidationSchemaOption> taxValidationSchemaOptions = new List<TaxValidationSchemaOption>();
}
