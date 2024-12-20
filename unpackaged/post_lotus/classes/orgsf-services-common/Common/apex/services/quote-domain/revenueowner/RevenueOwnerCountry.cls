public with sharing virtual class RevenueOwnerCountry {
    @AuraEnabled
    public String isoCode { get; set; }
    @AuraEnabled
    public String name { get; set; }
}
