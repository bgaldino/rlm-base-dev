public with sharing class AcctContRltnServiceRequestItem extends BaseRequestItem {
    @AuraEnabled
    public AccountContactRelationship accountContactRelationship { get; set; }

    public AcctContRltnServiceRequestItem(AccountContactRelationship accountContactRelationship) {
        this.accountContactRelationship = accountContactRelationship;
    }
}