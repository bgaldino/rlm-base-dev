public with sharing class RevenueOwnerCountryDetail extends RevenueOwnerCountry {
    @AuraEnabled
    public String revenueOwner { get; set; }
    @AuraEnabled
    public List<SupportedCurrency> supportedCurrencies { get; set; }
    @AuraEnabled
    public List<String> businessTypes { get; set; }
    @AuraEnabled
    public List<String> paymentMethods { get; set; }
    @AuraEnabled
    public TaxInformation taxInformation { get; set; }
    @AuraEnabled
    public ZipCodeMetadata zipCodeMetadata { get; set; }
    @AuraEnabled
    public List<StateProvinceMetadata> stateProvinceMetadataList { get; set; }
    @AuraEnabled
    public Map<String,String> countryLabelTranslations {get; set;}
}