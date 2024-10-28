public with sharing virtual class AccountContact {
    @AuraEnabled
    public Id accountId {get; set;}

    @AuraEnabled
    public String firstName;
    @AuraEnabled
    public String lastName;

    @AuraEnabled
    public String email;
    @AuraEnabled
    public String phoneNumber;

    @AuraEnabled
    public String mailingCountry;

}