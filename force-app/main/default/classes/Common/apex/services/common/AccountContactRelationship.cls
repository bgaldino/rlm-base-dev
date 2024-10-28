public with sharing virtual class AccountContactRelationship {
    @AuraEnabled
    public Id accountId { get; set; }

    @AuraEnabled
    public String currencyIsoCode { get; set; }
    @AuraEnabled
    public String isActive { get; set; }

    @AuraEnabled
    public Id contactId { get; set; }

    @AuraEnabled
    public String roles { get; set; }

}