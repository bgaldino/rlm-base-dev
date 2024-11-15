public with sharing class EffectiveDiscountingFactorDAO implements IEffectiveDiscountingFactorDAO {

    public List<EffectiveDiscountingFactor__mdt> getEffectiveDiscountingFactorForCountryAndCurrency(String countryCode, String currencyCode) {
        String countryLikeStr = countryCode + '%';
        return [
            SELECT Id, StandardCountry__c, Currency__c, StartDate__c, EndDate__c, CurrentFX__c 
            FROM EffectiveDiscountingFactor__mdt 
            WHERE StandardCountry__c LIKE :countryLikeStr 
            AND Currency__c = :currencyCode
            AND StartDate__c <= TODAY
            AND EndDate__c >= TODAY
            WITH SECURITY_ENFORCED
        ];
    }


}