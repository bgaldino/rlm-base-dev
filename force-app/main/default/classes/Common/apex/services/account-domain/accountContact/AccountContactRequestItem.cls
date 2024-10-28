public with sharing class AccountContactRequestItem extends BaseRequestItem {
    
    public AccountContact accountContact {get; set;}

    public AccountContactRequestItem(AccountContact accountContact){
        this.accountContact = accountContact;
    }
}