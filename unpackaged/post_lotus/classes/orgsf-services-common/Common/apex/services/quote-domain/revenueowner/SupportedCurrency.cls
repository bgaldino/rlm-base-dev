public with sharing class SupportedCurrency {
    @AuraEnabled
    public String currencyCode { get; private set; }
    @AuraEnabled
    public Boolean isDefault { get; private set; }

    public SupportedCurrency(String currencyCode) {
        this(currencyCode, false);
    }

    public SupportedCurrency(String currencyCode, Boolean isDefault) {
        this.currencyCode = currencyCode;
        this.isDefault = isDefault;
    }
}
