public with sharing class AccountContactResponseItem extends BaseResponseItem {
    public Id contactId {get; set;}

    public AccountContactResponseItem(String requestId){
        super(requestId);
    }
}