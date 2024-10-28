public with sharing class TaxValidationSchemaOption {
    @AuraEnabled
    public Map<String, List<String>> matchIf = new Map<String, List<String>>();
    @AuraEnabled
    public List<String> requiredFields = new List<String>();
    @AuraEnabled
    public Map<String, TaxValidationSchemaProperty> validationProperties = new Map<String, TaxValidationSchemaProperty>();
}
