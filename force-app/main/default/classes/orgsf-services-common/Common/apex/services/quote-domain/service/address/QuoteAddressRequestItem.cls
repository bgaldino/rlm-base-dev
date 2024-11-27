public with sharing class QuoteAddressRequestItem extends BaseRequestItem {
    @AuraEnabled
    public AccountAddress accountAddress { get; set; }

    @AuraEnabled
    public String quoteId { get; set; }

    @AuraEnabled
    public Boolean saveToAccount { get; set; }

    public QuoteAddressRequestItem() {
        this.saveToAccount = false;
    }
}
