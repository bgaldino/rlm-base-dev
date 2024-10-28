public with sharing class MerchantInfo {
    @AuraEnabled
    public String cyberSourceEndPointIframe { get; set; }
    @AuraEnabled
    public Boolean is3DS2 { get; set; }
    //Do not Aura Enable this
    public String secretKey { get; set; }
    @AuraEnabled
    public String merchantId { get; set; }
    @AuraEnabled
    public String accessKey { get; set; }
    @AuraEnabled
    public String profileId { get; set; }
    @AuraEnabled
    public List<String> validCreditCardTypes { get; set; }
    @AuraEnabled
    public String complianceLanguageForCC { get; set; }
    @AuraEnabled
    public String returnURL { get; set; }
}
