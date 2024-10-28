public with sharing class ConstantFXRateDAO implements IConstantFXRateDAO{

    public List<ConstantFXRate__mdt> getConstantFXRates(String currencyCode) {
        return [SELECT Id, ConstantFXRate__c, CurrencyISOCode__c FROM ConstantFXRate__mdt WHERE CurrencyISOCode__c = :currencyCode WITH SECURITY_ENFORCED];
    }
}