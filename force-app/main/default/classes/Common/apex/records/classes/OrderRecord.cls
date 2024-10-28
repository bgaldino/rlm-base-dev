public with sharing class OrderRecord extends AbstractRecord {
    public Id id {get; set;}
    public Date effectiveDate {get; set;}
    public Id accountId {get; set;}
    public String status {get; set;}
    public Id contractId {get; set;}
}