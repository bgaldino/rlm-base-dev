public with sharing class UsageDetailsWrapper {
    public String id {get; set;}
    public String name {get; set;} 
    public Date startDate {get; set;}
    public Date endDate {get; set;}
    public Id tenantInformationId {get; set;}
    public Decimal quantity {get; set;}
    public Id contractId {get; set;} 
    public Id quoteId {get; set;} 
    public String usageTypeName {get; set;} 
    public String currencyIsoCode {get; set;} 
    public Id usageTypeId {get; set;} 
    public String usageModel {get; set;} 

    public UsageDetailsWrapper () {}
}