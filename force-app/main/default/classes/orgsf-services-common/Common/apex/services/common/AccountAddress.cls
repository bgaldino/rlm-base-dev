public with sharing virtual class AccountAddress {
    @AuraEnabled
    public String accountId { get; set; }
    @AuraEnabled
    public String name { get; set; }

    @AuraEnabled
    public String street { get; set; }
    @AuraEnabled
    public String city { get; set; }
    @AuraEnabled
    public String state { get; set; }
    @AuraEnabled
    public String postalCode { get; set; }
    @AuraEnabled
    public String country { get; set; }

    @AuraEnabled
    public Map<String, String> additionalFields { get; set; }

    @AuraEnabled
    public String addressType { get; set; }
}
